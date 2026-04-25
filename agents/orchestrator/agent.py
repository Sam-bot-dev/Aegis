"""Orchestrator Agent.

Top-level coordinator. Given a batch of perceptual signals plus a snapshot of
the venue's responders, runs the Phase 1 agent graph:

    signals → ClassifierAgent → CascadeAgent → DispatcherAgent

Emits audit events at every step, writes the incident document to Firestore,
and returns a structured ``OrchestratorOutput`` the HTTP layer can return.

Phase 2 wraps this into a Vertex AI ADK agent with explicit tool-calling.
"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass, field

from aegis_shared.audit import write_audit
from aegis_shared.logger import get_logger
from aegis_shared.schemas import (
    Incident,
    IncidentClassification,
    IncidentStatus,
    PerceptualSignal,
    Severity,
    new_id,
)
from pydantic import BaseModel, Field

from agents.cascade.agent import CascadeAgent, CascadeInput, CascadeOutput
from agents.classifier.agent import ClassifierAgent, ClassifierInput
from agents.dispatcher.agent import (
    DispatcherAgent,
    DispatcherInput,
    DispatcherOutput,
    ResponderRecord,
)

log = get_logger(__name__)


@dataclass
class OrchestratorInput:
    signals: Sequence[PerceptualSignal]
    venue_id: str
    zone_id: str
    responders: Sequence[ResponderRecord] = field(default_factory=list)
    venue_context: dict[str, object] = field(default_factory=dict)
    language_preferences: Sequence[str] = ()


class OrchestratorOutput(BaseModel):
    incident: Incident
    classification: IncidentClassification
    cascade: CascadeOutput
    dispatch: DispatcherOutput
    agent_trace: list[str] = Field(default_factory=list)
    drill_mode: bool = False
    autonomous_mode: bool = False
    s1_hitl_gated: bool = False
    external_webhooks_fired: bool = False


class OrchestratorAgent:
    version = "orchestrator-v0.1"

    def __init__(
        self,
        classifier: ClassifierAgent | None = None,
        cascade: CascadeAgent | None = None,
        dispatcher: DispatcherAgent | None = None,
    ) -> None:
        self._classifier = classifier or ClassifierAgent()
        self._cascade = cascade or CascadeAgent()
        self._dispatcher = dispatcher or DispatcherAgent()

    async def run(self, inp: OrchestratorInput) -> OrchestratorOutput:
        trace: list[str] = []

        drill_mode = bool(inp.venue_context.get("drill_mode", False))
        autonomous_mode = bool(inp.venue_context.get("autonomous_mode", False))

        incident = Incident(
            venue_id=inp.venue_id,
            zone_id=inp.zone_id,
            status=IncidentStatus.DETECTED,
            agent_trace_id=new_id("TRC"),
        )
        trace.append(
            f"Incident {incident.incident_id} created" + (" (DRILL)" if drill_mode else "")
        )

        if drill_mode:
            await write_audit(
                venue_id=inp.venue_id,
                incident_id=incident.incident_id,
                action="incident.drill_mode_enabled",
                actor_type="system",
                actor_id="orchestrator",
                explanation=(
                    "Venue is in drill mode; external webhooks will be suppressed "
                    "and dispatches will be tagged drill=true."
                ),
            )

        await write_audit(
            venue_id=inp.venue_id,
            incident_id=incident.incident_id,
            action="incident.detected",
            actor_type="system",
            actor_id="orchestrator",
            input_obj=[s.model_dump(mode="json") for s in inp.signals],
            explanation="Signal batch accepted by orchestrator.",
        )

        # 1. Classify
        classification = await self._classifier.run(
            ClassifierInput(
                signals=list(inp.signals),
                venue_id=inp.venue_id,
                zone_id=inp.zone_id,
            )
        )
        incident.classification = classification
        incident.status = IncidentStatus.CLASSIFIED
        incident.summary = f"{classification.category.value}: {classification.rationale}"
        trace.append(
            f"Classified as {classification.category.value}/"
            f"{classification.severity.value} (conf={classification.confidence:.2f})"
        )

        await write_audit(
            venue_id=inp.venue_id,
            incident_id=incident.incident_id,
            action="incident.classified",
            actor_id=self._classifier.version,
            model_version=self._classifier.version,
            confidence=classification.confidence,
            input_obj=[s.signal_id for s in inp.signals],
            output_obj=classification.model_dump(mode="json"),
            explanation=classification.rationale,
        )

        # 2. Cascade + 3. Dispatch can run in parallel for S1/S2.
        cascade_task = asyncio.create_task(
            self._cascade.run(
                CascadeInput(
                    classification=classification,
                    venue_id=inp.venue_id,
                    zone_id=inp.zone_id,
                    venue_context=inp.venue_context,
                )
            )
        )
        dispatch_task: asyncio.Task[DispatcherOutput] | None = None
        if classification.severity in (Severity.S1_CRITICAL, Severity.S2_URGENT):
            dispatch_task = asyncio.create_task(
                self._dispatcher.run(
                    DispatcherInput(
                        incident_id=incident.incident_id,
                        venue_id=inp.venue_id,
                        zone_id=inp.zone_id,
                        classification=classification,
                        responders=inp.responders,
                        language_preferences=inp.language_preferences,
                    )
                )
            )

        cascade_output = await cascade_task
        # Prefer the dedicated CascadeAgent's predictions when it produced any.
        # If the CascadeAgent fell back to the heuristic and the upstream
        # ClassifierAgent already returned cascade predictions (from Gemini),
        # keep the classifier's so we don't waste those tokens.
        if cascade_output.predictions:
            classification.cascade_predictions = cascade_output.predictions
        elif not classification.cascade_predictions:
            classification.cascade_predictions = []
        trace.append(
            f"Cascade: {len(classification.cascade_predictions)} predictions, "
            f"{len(cascade_output.recommended_preemptive_actions)} recommended actions"
        )
        await write_audit(
            venue_id=inp.venue_id,
            incident_id=incident.incident_id,
            action="incident.cascade_predicted",
            actor_id=self._cascade.version,
            model_version=self._cascade.version,
            output_obj=cascade_output.model_dump(mode="json"),
            explanation=cascade_output.rationale,
        )

        if dispatch_task is not None:
            dispatch_output = await dispatch_task
            incident.status = IncidentStatus.DISPATCHED
            trace.append(
                f"Dispatched {len(dispatch_output.dispatched)} primary, "
                f"{len(dispatch_output.backup_ladder)} backup"
            )
            await write_audit(
                venue_id=inp.venue_id,
                incident_id=incident.incident_id,
                action="incident.dispatched",
                actor_id=self._dispatcher.version,
                model_version=self._dispatcher.version,
                output_obj=dispatch_output.model_dump(mode="json"),
                explanation=dispatch_output.rationale,
            )
        else:
            dispatch_output = DispatcherOutput(
                incident_id=incident.incident_id,
                rationale=f"Severity {classification.severity.value} did not warrant dispatch.",
            )
            trace.append("No dispatch (below threshold)")

        # Safety envelope: S1 requires operator opt-in via autonomous_mode.
        # If off, we still return the dispatch plan but mark it advisory so
        # downstream (the HTTP layer / UI) knows to keep the human gate.
        s1_hitl_gated = (
            classification.severity == Severity.S1_CRITICAL
            and not autonomous_mode
            and not drill_mode
        )
        if s1_hitl_gated:
            trace.append("S1 gated on human operator (autonomous_mode=false)")

        return OrchestratorOutput(
            incident=incident,
            classification=classification,
            cascade=cascade_output,
            dispatch=dispatch_output,
            agent_trace=trace,
            drill_mode=drill_mode,
            autonomous_mode=autonomous_mode,
            s1_hitl_gated=s1_hitl_gated,
            external_webhooks_fired=False,
        )

/**
 * Aegis — Firebase Cloud Functions.
 *
 * syncCustomClaims — Firestore trigger on `/users/{uid}` writes. Translates
 * the user doc's `role`, `venues`, and `skills` fields into custom claims on
 * the Firebase Auth token so security rules (`request.auth.token.role`) work.
 *
 * Deploy: `firebase deploy --only functions`
 */

const { onDocumentWritten } = require("firebase-functions/v2/firestore");
const { setGlobalOptions } = require("firebase-functions/v2");
const admin = require("firebase-admin");

admin.initializeApp();

setGlobalOptions({ region: "asia-south1", maxInstances: 10 });

exports.syncCustomClaims = onDocumentWritten(
  "users/{uid}",
  async (event) => {
    const uid = event.params.uid;
    const after = event.data && event.data.after && event.data.after.exists
      ? event.data.after.data()
      : null;

    if (!after) {
      try {
        await admin.auth().setCustomUserClaims(uid, null);
        console.log(`Cleared claims for ${uid}`);
      } catch (err) {
        console.warn(`Failed to clear claims for ${uid}: ${err.message}`);
      }
      return;
    }

    const claims = {
      role: after.role || null,
      venues: Array.isArray(after.venues) ? after.venues : [],
      skills: Array.isArray(after.skills) ? after.skills : [],
      venue_memberships: Array.isArray(after.venue_memberships)
        ? after.venue_memberships
        : (Array.isArray(after.venues) ? after.venues : []),
    };

    try {
      await admin.auth().setCustomUserClaims(uid, claims);
      console.log(
        `Set claims for ${uid}: role=${claims.role} venues=${claims.venues.length}`,
      );
    } catch (err) {
      console.error(`setCustomUserClaims failed for ${uid}: ${err.message}`);
      throw err;
    }
  },
);

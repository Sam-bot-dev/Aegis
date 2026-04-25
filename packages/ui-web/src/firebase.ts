/**
 * Shared Firebase web SDK bootstrap.
 *
 * Reads configuration from ``NEXT_PUBLIC_FIREBASE_*`` env vars so the same
 * module works in both ``apps/staff`` (PWA) and ``apps/dashboard`` (desktop).
 * Auto-connects to the Firestore emulator when ``NEXT_PUBLIC_USE_EMULATOR=1``.
 */

import { initializeApp, getApps, type FirebaseApp } from "firebase/app";
import {
  getFirestore,
  connectFirestoreEmulator,
  type Firestore,
} from "firebase/firestore";
import {
  getAuth,
  connectAuthEmulator,
  type Auth,
} from "firebase/auth";

export interface FirebaseConfig {
  apiKey: string;
  authDomain: string;
  projectId: string;
  storageBucket: string;
  messagingSenderId: string;
  appId: string;
}

export function readFirebaseConfig(): FirebaseConfig {
  return {
    apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY ?? "",
    authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN ?? "",
    projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID ?? "",
    storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET ?? "",
    messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID ?? "",
    appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID ?? "",
  };
}

let _app: FirebaseApp | null = null;
let _db: Firestore | null = null;
let _auth: Auth | null = null;

export function getFirebaseApp(): FirebaseApp {
  if (_app) return _app;
  const config = readFirebaseConfig();
  _app = getApps().length ? getApps()[0]! : initializeApp(config);
  return _app;
}

function isAlreadyConnectedError(err: unknown): boolean {
  // The Firebase SDK throws when connect*Emulator is called twice. The
  // message text is the only signal exposed; everything else is a real
  // failure we should NOT swallow (otherwise we'd silently leave the client
  // pointing at production).
  const msg =
    err && typeof err === "object" && "message" in err
      ? String((err as { message: unknown }).message)
      : "";
  return /already.*(connected|started|been called)/i.test(msg);
}

export function getDb(): Firestore {
  if (_db) return _db;
  const db = getFirestore(getFirebaseApp());
  if (
    typeof window !== "undefined" &&
    process.env.NEXT_PUBLIC_USE_EMULATOR === "1"
  ) {
    try {
      connectFirestoreEmulator(db, "127.0.0.1", 8080);
    } catch (err) {
      if (!isAlreadyConnectedError(err)) {
        // Surface the real error rather than silently using the production
        // client when the developer asked for the emulator.
        // eslint-disable-next-line no-console
        console.error("connectFirestoreEmulator failed", err);
        throw err;
      }
    }
  }
  _db = db;
  return _db;
}

export function getFirebaseAuth(): Auth {
  if (_auth) return _auth;
  const auth = getAuth(getFirebaseApp());
  if (
    typeof window !== "undefined" &&
    process.env.NEXT_PUBLIC_USE_EMULATOR === "1"
  ) {
    try {
      connectAuthEmulator(auth, "http://127.0.0.1:9099", {
        disableWarnings: true,
      });
    } catch (err) {
      if (!isAlreadyConnectedError(err)) {
        // eslint-disable-next-line no-console
        console.error("connectAuthEmulator failed", err);
        throw err;
      }
    }
  }
  _auth = auth;
  return _auth;
}

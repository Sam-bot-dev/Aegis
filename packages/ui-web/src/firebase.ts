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

export function getDb(): Firestore {
  if (_db) return _db;
  _db = getFirestore(getFirebaseApp());
  if (
    typeof window !== "undefined" &&
    process.env.NEXT_PUBLIC_USE_EMULATOR === "1"
  ) {
    try {
      connectFirestoreEmulator(_db, "127.0.0.1", 8080);
    } catch {
      /* already connected */
    }
  }
  return _db;
}

export function getFirebaseAuth(): Auth {
  if (_auth) return _auth;
  _auth = getAuth(getFirebaseApp());
  if (
    typeof window !== "undefined" &&
    process.env.NEXT_PUBLIC_USE_EMULATOR === "1"
  ) {
    try {
      connectAuthEmulator(_auth, "http://127.0.0.1:9099", {
        disableWarnings: true,
      });
    } catch {
      /* already connected */
    }
  }
  return _auth;
}

/**
 * React context for Firebase Auth state.
 *
 * Wrap your app with <AuthProvider> (typically in src/app/layout.tsx).
 * Access state via `useAuth()` hook.
 */

"use client";

import * as React from "react";
import {
  type User,
  onAuthStateChanged,
  type Auth,
  getAuth,
} from "firebase/auth";
import { getFirebaseApp } from "./firebase";

const AuthContext = React.createContext<{
  user: User | null;
  loading: boolean;
}>({
  user: null,
  loading: true,
});

export function useAuth() {
  return React.useContext(AuthContext);
}

export function AuthProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [user, setUser] = React.useState<User | null>(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    let auth: Auth | null = null;
    try {
      auth = getAuth(getFirebaseApp());
    } catch {
      // Firebase not initialized — stay unauthenticated
      setLoading(false);
      return;
    }

    const unsub = onAuthStateChanged(auth, (u) => {
      setUser(u);
      setLoading(false);
    }, (err) => {
      // eslint-disable-next-line no-console
      console.error("Auth state change error:", err);
      setLoading(false);
    });

    return () => unsub();
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading }}>{children}</AuthContext.Provider>
  );
}

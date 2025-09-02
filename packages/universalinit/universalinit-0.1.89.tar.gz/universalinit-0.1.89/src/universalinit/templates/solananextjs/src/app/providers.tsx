"use client";

import React, { createContext, useCallback, useEffect, useMemo, useState } from "react";
import { loadSession, saveSession } from "@/lib/storage";
import type { Session, UserRole } from "@/lib/types";
import { connectWallet, disconnectWallet } from "@/lib/solana";

export interface SessionContextValue {
  /** Current user session or null if not connected. */
  session: Session | null;
  /** Connect a wallet for the given role and persist the session. */
  connect: (role: UserRole) => Promise<void>;
  /** Disconnect the wallet and clear session. */
  disconnect: () => Promise<void>;
}

// PUBLIC_INTERFACE
export const SessionContext = createContext<SessionContextValue>({
  session: null,
  connect: async () => {},
  disconnect: async () => {},
});

// PUBLIC_INTERFACE
export function Providers({ children }: { children: React.ReactNode }) {
  /** Root provider for the application. Manages only session state (no theme switching). */
  const [session, setSession] = useState<Session | null>(null);

  // Load session on mount
  useEffect(() => {
    const s = loadSession();
    if (s) setSession(s);
  }, []);

  const connect = useCallback(async (role: UserRole) => {
    const publicKey = await connectWallet();
    const next: Session = {
      role,
      publicKey,
      connectedAt: Date.now(),
    };
    setSession(next);
    saveSession(next);
  }, []);

  const disconnect = useCallback(async () => {
    await disconnectWallet();
    setSession(null);
    saveSession(null);
  }, []);

  const sessionValue = useMemo(
    () => ({ session, connect, disconnect }),
    [session, connect, disconnect]
  );

  return <SessionContext.Provider value={sessionValue}>{children}</SessionContext.Provider>;
}

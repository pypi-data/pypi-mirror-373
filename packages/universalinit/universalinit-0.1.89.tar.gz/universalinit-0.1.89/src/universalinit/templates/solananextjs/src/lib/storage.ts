"use client";

import type { Session, SignedPrescription } from "./types";

const LS_KEYS = {
  session: "solrx.session.v1",
  prescriptions: "solrx.prescriptions.v1",
} as const;

function safeParse<T>(raw: string | null, fallback: T): T {
  if (!raw) return fallback;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

// PUBLIC_INTERFACE
export function loadSession(): Session | null {
  /** Load the current wallet session from local storage. */
  return safeParse<Session | null>(localStorage.getItem(LS_KEYS.session), null);
}

// PUBLIC_INTERFACE
export function saveSession(session: Session | null): void {
  /** Save or clear the current wallet session in local storage. */
  if (session) localStorage.setItem(LS_KEYS.session, JSON.stringify(session));
  else localStorage.removeItem(LS_KEYS.session);
}

// PUBLIC_INTERFACE
export function loadPrescriptions(): SignedPrescription[] {
  /** Load all prescriptions from local storage (doctor-side storage). */
  return safeParse<SignedPrescription[]>(localStorage.getItem(LS_KEYS.prescriptions), []);
}

// PUBLIC_INTERFACE
export function savePrescriptions(list: SignedPrescription[]): void {
  /** Persist the given prescriptions list in local storage. */
  localStorage.setItem(LS_KEYS.prescriptions, JSON.stringify(list));
}

// PUBLIC_INTERFACE
export function addPrescription(p: SignedPrescription): void {
  /** Append a prescription to local storage. */
  const list = loadPrescriptions();
  list.unshift(p);
  savePrescriptions(list);
}

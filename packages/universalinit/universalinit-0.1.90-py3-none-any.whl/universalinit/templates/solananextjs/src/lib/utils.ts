import type { PrescriptionPayload } from "./types";

// PUBLIC_INTERFACE
export function generateId(prefix = "rx"): string {
  /** Create a compact unique id combining time and randomness. */
  const rand = Math.random().toString(36).slice(2, 8);
  return `${prefix}_${Date.now().toString(36)}${rand}`;
}

// PUBLIC_INTERFACE
export function canonicalizePayload(payload: PrescriptionPayload): string {
  /** Create a deterministic, human-readable canonical message to sign. */
  const ordered: Record<string, string> = {
    patientName: payload.patientName.trim(),
    patientDOB: payload.patientDOB,
    medication: payload.medication.trim(),
    dosage: payload.dosage.trim(),
    quantity: payload.quantity.trim(),
    refills: (payload.refills ?? "").trim(),
    notes: (payload.notes ?? "").trim(),
    expiresOn: payload.expiresOn ?? "",
    createdAt: payload.createdAt,
  };
  // Create a compact canonical string:
  return [
    `Prescription`,
    `Patient:${ordered.patientName}|DOB:${ordered.patientDOB}`,
    `Med:${ordered.medication}|Dose:${ordered.dosage}|Qty:${ordered.quantity}`,
    `Refills:${ordered.refills || "0"}`,
    `Expires:${ordered.expiresOn || "N/A"}`,
    `Created:${ordered.createdAt}`,
  ].join("\n");
}

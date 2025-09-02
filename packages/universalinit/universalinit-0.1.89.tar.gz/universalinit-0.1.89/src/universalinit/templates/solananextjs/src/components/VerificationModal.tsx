"use client";

import React from "react";
import Modal from "./Modal";
import Button from "./Button";
import { verifySignature } from "@/lib/solana";
import { canonicalizePayload } from "@/lib/utils";
import type { SignedPrescription } from "@/lib/types";

// PUBLIC_INTERFACE
export default function VerificationModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  /** Modal for verifying a signed prescription by recomputing the canonical message from the payload and validating the signature. */
  const [input, setInput] = React.useState("");
  const [result, setResult] = React.useState<null | { ok: boolean; error?: string; p?: SignedPrescription }>(null);

  const onVerify = () => {
    try {
      // Parse the JSON input. It may or may not include a 'message' property.
      const obj = JSON.parse(input) as SignedPrescription;

      // Validate required fields for verification.
      if (!obj?.payload || !obj?.signature || !obj?.doctorPublicKey) {
        throw new Error("Invalid prescription JSON: missing payload, signature, or doctorPublicKey.");
      }

      // Recompute canonical message from payload instead of trusting obj.message.
      const canonicalMessage = canonicalizePayload(obj.payload);

      // Verify using the derived canonical message.
      const ok = verifySignature(canonicalMessage, obj.signature, obj.doctorPublicKey);

      setResult({ ok, p: obj, error: ok ? undefined : "Signature verification failed." });
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : "Failed to parse/verify.";
      setResult({ ok: false, error: message });
    }
  };

  const footer = (
    <div className="flex items-center justify-end gap-2">
      <Button variant="ghost" onClick={onClose}>Close</Button>
      <Button onClick={onVerify}>Verify</Button>
    </div>
  );

  return (
    <Modal open={open} onClose={onClose} title="Verify Prescription" footer={footer}>
      <div className="space-y-3">
        <p className="text-sm text-muted">
          Paste the prescription JSON shared by the doctor. The app will verify the Solana signature against the doctor&apos;s public key.
        </p>
        <textarea
          className="w-full min-h-40 border border-base rounded-lg p-2 bg-transparent"
          placeholder="Paste JSON here..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        {result && (
          <div className={`p-3 rounded-lg border ${result.ok ? "border-green-300 bg-green-50 dark:bg-green-900/20" : "border-red-300 bg-red-50 dark:bg-red-900/20"}`}>
            <div className="font-medium">
              {result.ok ? "Signature valid ✅" : "Invalid signature ❌"}
            </div>
            {result.p && (
              <div className="mt-2 text-sm">
                <div><strong>Patient:</strong> {result.p.payload.patientName}</div>
                <div><strong>Medication:</strong> {result.p.payload.medication} ({result.p.payload.dosage})</div>
                <div><strong>Doctor:</strong> {result.p.doctorPublicKey}</div>
              </div>
            )}
            {result.error && <div className="text-sm mt-2 text-red-700 dark:text-red-300">{result.error}</div>}
          </div>
        )}
      </div>
    </Modal>
  );
}

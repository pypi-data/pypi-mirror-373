"use client";

import React from "react";
import Card from "./Card";
import Button from "./Button";
import { canonicalizePayload, generateId } from "@/lib/utils";
import { signMessage } from "@/lib/solana";
import { addPrescription } from "@/lib/storage";
import type { PrescriptionPayload, SignedPrescription } from "@/lib/types";

const Input = (props: React.InputHTMLAttributes<HTMLInputElement>) => (
  <input
    {...props}
    className="w-full px-3 py-2 rounded-lg border border-base bg-transparent focus:ring-primary"
  />
);

const TextArea = (props: React.TextareaHTMLAttributes<HTMLTextAreaElement>) => (
  <textarea
    {...props}
    className="w-full px-3 py-2 rounded-lg border border-base bg-transparent min-h-24 focus:ring-primary"
  />
);

export default function PrescriptionForm({ onCreated }: { onCreated: (p: SignedPrescription) => void }) {
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const fd = new FormData(e.currentTarget);
      const payload: PrescriptionPayload = {
        patientName: String(fd.get("patientName") || "").trim(),
        patientDOB: String(fd.get("patientDOB") || ""),
        medication: String(fd.get("medication") || "").trim(),
        dosage: String(fd.get("dosage") || "").trim(),
        quantity: String(fd.get("quantity") || "").trim(),
        refills: String(fd.get("refills") || "").trim(),
        notes: String(fd.get("notes") || "").trim(),
        expiresOn: String(fd.get("expiresOn") || ""),
        createdAt: new Date().toISOString(),
      };

      if (!payload.patientName || !payload.patientDOB || !payload.medication || !payload.dosage || !payload.quantity) {
        throw new Error("Please fill all required fields.");
      }

      const message = canonicalizePayload(payload);
      const signed = await signMessage(message);

      const p: SignedPrescription = {
        id: generateId(),
        doctorPublicKey: signed.publicKey,
        payload,
        message,
        signature: signed.signature,
        status: "active",
        createdAt: new Date().toISOString(),
      };

      addPrescription(p);
      onCreated(p);
      e.currentTarget.reset();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to create prescription.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <form onSubmit={onSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="md:col-span-2">
          <h3 className="text-lg font-semibold">New Prescription</h3>
          <p className="text-sm text-muted">Fill the fields and sign with your Solana wallet.</p>
        </div>
        <div>
          <label className="text-sm">Patient Name*</label>
          <Input name="patientName" placeholder="Jane Doe" required />
        </div>
        <div>
          <label className="text-sm">Patient DOB*</label>
          <Input name="patientDOB" type="date" required />
        </div>
        <div className="md:col-span-2">
          <label className="text-sm">Medication*</label>
          <Input name="medication" placeholder="Amoxicillin" required />
        </div>
        <div>
          <label className="text-sm">Dosage*</label>
          <Input name="dosage" placeholder="500mg twice daily" required />
        </div>
        <div>
          <label className="text-sm">Quantity*</label>
          <Input name="quantity" placeholder="20 tablets" required />
        </div>
        <div>
          <label className="text-sm">Refills</label>
          <Input name="refills" placeholder="0" />
        </div>
        <div>
          <label className="text-sm">Expires On</label>
          <Input name="expiresOn" type="date" />
        </div>
        <div className="md:col-span-2">
          <label className="text-sm">Notes</label>
          <TextArea name="notes" placeholder="Instructions or notes (optional)" />
        </div>
        {error && (
          <div className="md:col-span-2 text-sm text-red-600 border border-red-300 bg-red-50 dark:bg-red-950/30 rounded-lg px-3 py-2">
            {error}
          </div>
        )}
        <div className="md:col-span-2 flex justify-end">
          <Button type="submit" disabled={loading}>
            {loading ? "Signing..." : "Create & Sign"}
          </Button>
        </div>
      </form>
    </Card>
  );
}

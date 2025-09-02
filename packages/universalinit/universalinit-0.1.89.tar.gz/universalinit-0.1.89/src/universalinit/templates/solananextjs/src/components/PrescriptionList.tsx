"use client";

import React from "react";
import Card from "./Card";
import Button from "./Button";
import type { SignedPrescription } from "@/lib/types";
import { savePrescriptions } from "@/lib/storage";

export default function PrescriptionList({
  prescriptions,
  onChange,
}: {
  prescriptions: SignedPrescription[];
  onChange: (next: SignedPrescription[]) => void;
}) {
  const copyToClipboard = async (p: SignedPrescription) => {
    const data = JSON.stringify(p, null, 2);
    await navigator.clipboard.writeText(data);
    alert("Prescription JSON copied to clipboard.");
  };

  const markFulfilled = (id: string) => {
    const next = prescriptions.map((p) => (p.id === id ? { ...p, status: "fulfilled" as const } : p));
    savePrescriptions(next);
    onChange(next);
  };

  const remove = (id: string) => {
    const next = prescriptions.filter((p) => p.id !== id);
    savePrescriptions(next);
    onChange(next);
  };

  const Badge = ({ status }: { status: SignedPrescription["status"] }) => {
    const color =
      status === "active" ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300" :
      status === "fulfilled" ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300" :
      "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300";
    return <span className={`px-2 py-1 rounded-full text-xs ${color}`}>{status}</span>;
  };

  return (
    <Card className="mt-6">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold">My Prescriptions</h3>
        <span className="text-sm text-muted">{prescriptions.length} total</span>
      </div>
      <div className="space-y-3">
        {prescriptions.length === 0 && (
          <div className="text-sm text-muted">No prescriptions yet.</div>
        )}
        {prescriptions.map((p) => (
          <div key={p.id} className="border border-base rounded-lg p-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">#{p.id}</span>
                <Badge status={p.status} />
              </div>
              <div className="flex items-center gap-2">
                <Button variant="ghost" onClick={() => copyToClipboard(p)}>Copy JSON</Button>
                {p.status === "active" && (
                  <Button variant="secondary" onClick={() => markFulfilled(p.id)}>Mark Fulfilled</Button>
                )}
                <Button variant="ghost" onClick={() => remove(p.id)}>Remove</Button>
              </div>
            </div>
            <div className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
              <div>
                <strong>Patient:</strong> {p.payload.patientName} ({p.payload.patientDOB})
              </div>
              <div>
                <strong>Medication:</strong> {p.payload.medication}, {p.payload.dosage}
              </div>
              <div>
                <strong>Quantity:</strong> {p.payload.quantity} | <strong>Refills:</strong> {p.payload.refills || "0"}
              </div>
              <div>
                <strong>Doctor:</strong> {p.doctorPublicKey.slice(0, 8)}...{p.doctorPublicKey.slice(-6)}
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}

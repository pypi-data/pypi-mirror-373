"use client";

import React from "react";
import NavBar from "@/components/NavBar";
import WalletConnect from "@/components/WalletConnect";
import PrescriptionForm from "@/components/PrescriptionForm";
import PrescriptionList from "@/components/PrescriptionList";
import Card from "@/components/Card";
import { SessionContext } from "../providers";
import { loadPrescriptions } from "@/lib/storage";
import type { SignedPrescription } from "@/lib/types";

export default function DoctorPage() {
  const { session } = React.useContext(SessionContext);
  const [list, setList] = React.useState<SignedPrescription[]>([]);

  React.useEffect(() => {
    setList(loadPrescriptions());
  }, []);

  return (
    <>
      <NavBar />
      <main className="max-w-6xl mx-auto px-4 py-6 space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold">Doctor Dashboard</h1>
          <WalletConnect role="doctor" />
        </div>
        {!session || session.role !== "doctor" ? (
          <Card>
            <p className="text-sm">Please connect your Doctor wallet to create and sign prescriptions.</p>
          </Card>
        ) : (
          <>
            <PrescriptionForm onCreated={(p) => setList((prev) => [p, ...prev])} />
            <PrescriptionList prescriptions={list} onChange={setList} />
          </>
        )}
      </main>
    </>
  );
}

"use client";

import React from "react";
import NavBar from "@/components/NavBar";
import WalletConnect from "@/components/WalletConnect";
import Card from "@/components/Card";
import Button from "@/components/Button";
import VerificationModal from "@/components/VerificationModal";
import { SessionContext } from "../providers";

export default function PharmacistPage() {
  const { session } = React.useContext(SessionContext);
  const [open, setOpen] = React.useState(false);

  return (
    <>
      <NavBar />
      <main className="max-w-4xl mx-auto px-4 py-6 space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold">Pharmacist Dashboard</h1>
          <WalletConnect role="pharmacist" />
        </div>

        {!session || session.role !== "pharmacist" ? (
          <Card>
            <p className="text-sm">Please connect your Pharmacist wallet to verify prescriptions.</p>
          </Card>
        ) : (
          <Card>
            <p className="text-sm text-muted">
              Click verify to open a modal where you can paste a prescription JSON shared by the doctor. The app will validate the Solana signature.
            </p>
            <div className="mt-4">
              <Button onClick={() => setOpen(true)}>Verify Prescription</Button>
            </div>
          </Card>
        )}

        <VerificationModal open={open} onClose={() => setOpen(false)} />
      </main>
    </>
  );
}

"use client";

import React from "react";
import Button from "./Button";
import { SessionContext } from "@/app/providers";

export default function WalletConnect({ role }: { role: "doctor" | "pharmacist" }) {
  const { session, connect, disconnect } = React.useContext(SessionContext);

  if (session && session.role === role) {
    const short = `${session.publicKey.slice(0, 4)}...${session.publicKey.slice(-4)}`;
    return (
      <div className="flex items-center gap-2">
        <span className="text-sm text-muted">Connected: {short}</span>
        <Button variant="ghost" onClick={() => disconnect()}>Disconnect</Button>
      </div>
    );
  }

  return (
    <Button onClick={() => connect(role)} variant="secondary">
      Connect {role === "doctor" ? "Doctor" : "Pharmacist"} Wallet
    </Button>
  );
}

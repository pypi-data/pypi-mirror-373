"use client";

import Link from "next/link";
import NavBar from "@/components/NavBar";
import Card from "@/components/Card";
import Button from "@/components/Button";

export default function Home() {
  return (
    <>
      <NavBar />
      <main className="max-w-6xl mx-auto px-4 py-10">
        <section className="text-center mb-10">
          <h1 className="text-3xl md:text-4xl font-semibold">SolRx: Solana-based Medical Prescriptions</h1>
          <p className="text-muted mt-2">Create, sign, and verify prescriptions securely using your Solana wallet.</p>
        </section>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <h2 className="text-xl font-semibold">Doctor</h2>
            <p className="text-sm text-muted mt-1">Connect your wallet, create prescriptions, and sign them on-chain using message signatures.</p>
            <div className="mt-4">
              <Link href="/doctor"><Button>Go to Doctor Dashboard</Button></Link>
            </div>
          </Card>

          <Card>
            <h2 className="text-xl font-semibold">Pharmacist</h2>
            <p className="text-sm text-muted mt-1">Connect your wallet (for role-based access) and verify signed prescriptions shared by doctors.</p>
            <div className="mt-4">
              <Link href="/pharmacist"><Button variant="secondary">Go to Pharmacist Dashboard</Button></Link>
            </div>
          </Card>
        </div>

        <section className="mt-10">
          <Card>
            <h3 className="text-lg font-semibold">How it works</h3>
            <ol className="list-decimal pl-5 mt-3 space-y-1 text-sm text-muted">
              <li>Doctor connects wallet, fills a prescription form, and signs a canonical message.</li>
              <li>The signed prescription (JSON) can be shared securely with the pharmacist.</li>
              <li>Pharmacist pastes the JSON and verifies the signature using the doctor&apos;s public key.</li>
              <li>All data is stored locally in your browser. No backend is used.</li>
            </ol>
          </Card>
        </section>
      </main>
    </>
  );
}

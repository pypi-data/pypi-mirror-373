"use client";

import React from "react";
import Link from "next/link";

export default function NavBar() {
  return (
    <header className="border-b border-base bg-surface">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary" />
          <span className="font-semibold">SolRx</span>
        </Link>
        <nav className="flex items-center gap-3">
          <Link className="text-sm hover:underline" href="/doctor">Doctor</Link>
          <Link className="text-sm hover:underline" href="/pharmacist">Pharmacist</Link>
        </nav>
      </div>
    </header>
  );
}

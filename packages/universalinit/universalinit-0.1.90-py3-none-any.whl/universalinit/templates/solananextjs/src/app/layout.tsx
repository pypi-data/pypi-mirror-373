import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "SolRx | Solana Prescriptions",
  description: "Create and verify medical prescriptions using Solana signatures",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning>
        <Providers>
          <div className="min-h-dvh flex flex-col">{children}</div>
        </Providers>
      </body>
    </html>
  );
}

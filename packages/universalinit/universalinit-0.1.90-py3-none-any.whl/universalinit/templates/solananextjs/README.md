This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## SolRx Frontend

This template provides a modern, minimal UI to create, sign, and verify medical prescriptions using a Solana wallet. No backend is used — data is persisted in your browser via localStorage.

Key features:
- Doctor wallet login and prescription signing
- Pharmacist wallet login and verification
- Responsive UI with modal dialogs
- Light/Dark theme (toggle in navbar)
- Local storage of sessions and prescriptions

Notes:
- A Solana wallet extension such as Phantom is required in the browser.
- Signature verification uses Ed25519 (tweetnacl) and Base58 (bs58).
- Doctor can export a prescription as JSON (copy to clipboard) and share securely with the pharmacist.

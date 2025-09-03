"use client";

import nacl from "tweetnacl";
import bs58 from "bs58";

/** Phantom-like provider detection. */
// PUBLIC_INTERFACE
export function getProvider(): Window["solana"] | null {
  /** Return the injected Solana provider if present (e.g., Phantom). */
  if (typeof window === "undefined") return null;
  const anyWindow = window as Window;
  if (anyWindow?.solana?.isPhantom || anyWindow?.solana) {
    return anyWindow.solana!;
  }
  return null;
}

// PUBLIC_INTERFACE
export async function connectWallet(): Promise<string> {
  /** Connect to the wallet and return the base58 public key. */
  const provider = getProvider();
  if (!provider) throw new Error("No Solana wallet found. Install Phantom or a compatible wallet.");
  const res = await provider.connect();
  const pk = res?.publicKey?.toBase58?.() ?? res?.publicKey?.toString?.();
  if (!pk) throw new Error("Failed to read wallet public key.");
  return pk;
}

// PUBLIC_INTERFACE
export async function disconnectWallet(): Promise<void> {
  /** Disconnect the current wallet if connected. */
  const provider = getProvider();
  if (!provider) return;
  try {
    await provider.disconnect();
  } catch {
    // ignore
  }
}

// PUBLIC_INTERFACE
export async function signMessage(message: string): Promise<{
  signature: string;
  publicKey: string;
}> {
  /** Request the wallet to sign an arbitrary message. Returns base58 signature and public key. */
  const provider = getProvider();
  if (!provider) throw new Error("No wallet available to sign.");

  const encoder = new TextEncoder();
  const msgBytes = encoder.encode(message);

  if (!provider.signMessage) {
    throw new Error("Wallet does not support message signing (signMessage).");
  }
  const res = await provider.signMessage(msgBytes, "utf8");
  const sigBytes = ArrayBuffer.isView(res)
    ? (res as Uint8Array)
    : (res as { signature: Uint8Array }).signature;

  const pk = provider.publicKey?.toBase58?.() ?? provider.publicKey?.toString?.();
  if (!pk) {
    throw new Error("Unable to read wallet public key.");
  }
  return {
    signature: bs58.encode(sigBytes),
    publicKey: pk,
  };
}

// PUBLIC_INTERFACE
export function verifySignature(message: string, signatureB58: string, publicKeyB58: string): boolean {
  /** Verify a base58-encoded signature for the given message using the base58 public key. */
  const encoder = new TextEncoder();
  const msgBytes = encoder.encode(message);
  const sigBytes = bs58.decode(signatureB58);
  const pubKeyBytes = bs58.decode(publicKeyB58);
  return nacl.sign.detached.verify(msgBytes, sigBytes, pubKeyBytes);
}

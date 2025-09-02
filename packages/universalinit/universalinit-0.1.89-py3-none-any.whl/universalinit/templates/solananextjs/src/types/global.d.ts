declare global {
  interface SolanaProvider {
    isPhantom?: boolean;
    isConnected?: boolean;
    publicKey?: {
      toString(): string;
      toBase58(): string;
    };
    connect: (opts?: { onlyIfTrusted?: boolean }) => Promise<{ publicKey: { toString(): string; toBase58(): string } }>;
    disconnect: () => Promise<void>;
    signMessage?: (message: Uint8Array, display?: string) => Promise<Uint8Array | { signature: Uint8Array }>;
  }

  interface Window {
    solana?: SolanaProvider;
  }
}

export {};

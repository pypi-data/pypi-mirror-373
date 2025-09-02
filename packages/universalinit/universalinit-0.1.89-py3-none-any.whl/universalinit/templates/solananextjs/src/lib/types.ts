export type UserRole = "doctor" | "pharmacist";

export interface Session {
  role: UserRole;
  publicKey: string; // Base58 string from wallet
  connectedAt: number;
}

export interface PrescriptionPayload {
  patientName: string;
  patientDOB: string; // ISO date
  medication: string;
  dosage: string;
  quantity: string;
  refills?: string;
  notes?: string;
  expiresOn?: string; // ISO date
  createdAt: string; // ISO
}

export interface SignedPrescription {
  id: string;
  doctorPublicKey: string; // base58
  payload: PrescriptionPayload;
  message: string; // canonical message used for signing
  signature: string; // base58 signature
  status: "active" | "fulfilled" | "expired";
  createdAt: string; // ISO
}

"use client";

import React from "react";
import Button from "./Button";

interface ModalProps {
  open: boolean;
  title?: string;
  onClose: () => void;
  footer?: React.ReactNode;
  children: React.ReactNode;
}

export default function Modal({ open, title, onClose, footer, children }: ModalProps) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative z-10 w-full max-w-xl bg-surface border border-base rounded-xl shadow-lg">
        <div className="flex items-center justify-between p-4 border-b border-base">
          <h3 className="text-lg font-semibold">{title}</h3>
          <Button variant="ghost" onClick={onClose} aria-label="Close">✕</Button>
        </div>
        <div className="p-4">{children}</div>
        {footer && <div className="p-4 border-t border-base">{footer}</div>}
      </div>
    </div>
  );
}

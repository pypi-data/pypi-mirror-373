"use client";

import React from "react";
import clsx from "clsx";

export default function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={clsx(
        "bg-surface border border-base rounded-xl shadow-sm p-4 md:p-6",
        className
      )}
      {...props}
    />
  );
}

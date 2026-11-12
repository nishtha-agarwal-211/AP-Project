import { createHash } from "node:crypto";

// Hand-built on purpose. Object.fromEntries() would reorder keys like "10"/"2"
// numerically, which breaks canonical ordering.
export function canonicalJson(v: unknown): string {
  if (v === null || typeof v !== "object") {
    if (typeof v === "number" && !Number.isFinite(v)) throw new Error("non-finite number");
    return JSON.stringify(v);
  }
  if (Array.isArray(v)) return "[" + v.map(canonicalJson).join(",") + "]";
  const o = v as Record<string, unknown>;
  const keys = Object.keys(o).filter((k) => o[k] !== undefined).sort();
  return "{" + keys.map((k) => JSON.stringify(k) + ":" + canonicalJson(o[k])).join(",") + "}";
}

export const sha256Hex = (v: unknown) =>
  createHash("sha256").update(canonicalJson(v), "utf8").digest("hex");

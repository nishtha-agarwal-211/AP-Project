import test from "node:test";
import assert from "node:assert/strict";
import { canonicalJson, sha256Hex } from "./canonical.js";

test("key order does not change hash", () => {
  assert.equal(sha256Hex({ a: 1, b: { d: 1, c: 2 } }), sha256Hex({ b: { c: 2, d: 1 }, a: 1 }));
});
test("compact and sorted", () => {
  assert.equal(canonicalJson({ b: 2, a: { d: 1, c: 2 } }), '{"a":{"c":2,"d":1},"b":2}');
});
test("numeric-string keys sort as strings", () => {
  assert.equal(canonicalJson({ "10": 1, "2": 2 }), '{"10":1,"2":2}');
});

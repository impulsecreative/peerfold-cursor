#!/usr/bin/env node
// Fails when a tool name this plugin references is missing from a registry.
//
//   node scripts/check-tool-names.mjs scripts/registry-snapshot.txt
//   node scripts/check-tool-names.mjs https://app.peerfold.com/llms-full.txt
//
// A registry is a file or URL. A line that is exactly one snake_case name
// counts as a registry entry, and so does any backticked snake_case name in
// prose, so a plain list and an llms-full.txt both work. A registry that
// yields fewer than --min names (default 50) is reported as not a registry,
// and the check fails, because a document that names a handful of tools
// cannot vouch for the rest.

import { promises as fs } from "node:fs";
import process from "node:process";
import { extractToolNames } from "./extract-tool-names.mjs";

const args = process.argv.slice(2);
const source = args.find((arg) => !arg.startsWith("--"));
const minArg = args.find((arg) => arg.startsWith("--min="));
const min = minArg ? Number(minArg.slice("--min=".length)) : 50;
if (!source) {
  console.error("Usage: node scripts/check-tool-names.mjs <registry file or URL> [--min=N]");
  process.exit(2);
}

async function loadRegistry(from) {
  let text;
  if (/^https?:\/\//.test(from)) {
    const response = await fetch(from);
    if (!response.ok) throw new Error(`${from} answered ${response.status}`);
    text = await response.text();
  } else {
    text = await fs.readFile(from, "utf8");
  }
  const names = new Set();
  for (const line of text.split("\n")) {
    const trimmed = line.trim();
    if (/^[a-z][a-z0-9]*(?:_[a-z0-9]+)+$/.test(trimmed)) names.add(trimmed);
    for (const match of trimmed.matchAll(/`([a-z][a-z0-9]*(?:_[a-z0-9]+)+)`/g)) names.add(match[1]);
  }
  return names;
}

const registry = await loadRegistry(source);
const referenced = await extractToolNames();
console.log(`Registry ${source}: ${registry.size} names. Plugin references ${referenced.size} names.`);

if (registry.size < min) {
  console.error(`The registry yields ${registry.size} names, under the ${min} needed to count as a tool registry. It cannot vouch for the plugin.`);
  process.exit(1);
}

const missing = [...referenced.keys()].filter((name) => !registry.has(name)).sort();
if (missing.length > 0) {
  console.error("Tool names referenced by the plugin but missing from the registry:");
  for (const name of missing) console.error(`- ${name} (${[...referenced.get(name)].sort().join(", ")})`);
  process.exit(1);
}
console.log("Every referenced tool name is in the registry.");

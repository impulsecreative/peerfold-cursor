#!/usr/bin/env node
// Prints every Peerfold MCP tool name this plugin references, one per line.
// A tool name is a backticked snake_case identifier in a rule, skill, command
// or agent file. Names listed in scripts/not-tool-names.txt are field names
// and argument names that share the shape and are left out.

import { promises as fs } from "node:fs";
import path from "node:path";
import process from "node:process";

const repoRoot = process.cwd();
const dirs = ["rules", "skills", "commands", "agents"];
const identifier = /`([a-z][a-z0-9]*(?:_[a-z0-9]+)+)`/g;

async function walk(dir, out) {
  for (const entry of await fs.readdir(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) await walk(full, out);
    else if (entry.isFile()) out.push(full);
  }
  return out;
}

export async function extractToolNames() {
  const notTools = new Set(
    (await fs.readFile(path.join(repoRoot, "scripts", "not-tool-names.txt"), "utf8"))
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line && !line.startsWith("#")),
  );
  const found = new Map();
  for (const dir of dirs) {
    const abs = path.join(repoRoot, dir);
    const files = await walk(abs, []).catch(() => []);
    for (const file of files) {
      const text = await fs.readFile(file, "utf8");
      for (const match of text.matchAll(identifier)) {
        const name = match[1];
        if (notTools.has(name)) continue;
        if (!found.has(name)) found.set(name, new Set());
        found.get(name).add(path.relative(repoRoot, file));
      }
    }
  }
  return found;
}

if (process.argv[1] && path.resolve(process.argv[1]) === new URL(import.meta.url).pathname) {
  const found = await extractToolNames();
  const verbose = process.argv.includes("--where");
  for (const name of [...found.keys()].sort()) {
    console.log(verbose ? `${name}\t${[...found.get(name)].sort().join(", ")}` : name);
  }
}

#!/usr/bin/env node
// Fails on text this repository must never carry: an em dash (U+2014), an
// absolute home path, a ".." path segment in a path-like string, or a secret
// key prefix. Skips .git and this script's own pattern list.

import { promises as fs } from "node:fs";
import path from "node:path";
import process from "node:process";

const repoRoot = process.cwd();
const skipDirs = new Set([".git", "node_modules"]);
const checks = [
  { name: "em dash (U+2014)", pattern: /\u2014/ },
  { name: "absolute path", pattern: /(^|[\s"'`(=])\/(Users|home)\// },
  { name: "parent path segment", pattern: /(^|[\s"'`(=])(\.\.\/|[^\s"'`]*\/\.\.(\/|[\s"'`]|$))/ },
  { name: "secret key", pattern: /sk_(live|test)_/ },
];

async function walk(dir, out) {
  for (const entry of await fs.readdir(dir, { withFileTypes: true })) {
    if (skipDirs.has(entry.name)) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) await walk(full, out);
    else if (entry.isFile()) out.push(full);
  }
  return out;
}

const files = await walk(repoRoot, []);
const findings = [];
for (const file of files) {
  const rel = path.relative(repoRoot, file);
  const text = await fs.readFile(file, "utf8").catch(() => null);
  if (text === null) continue;
  const lines = text.split("\n");
  lines.forEach((line, index) => {
    for (const check of checks) {
      if (check.pattern.test(line)) findings.push(`${rel}:${index + 1}: ${check.name}`);
    }
  });
}

if (findings.length > 0) {
  console.error("Text check failed:");
  for (const finding of findings) console.error(`- ${finding}`);
  process.exit(1);
}
console.log(`Text check passed (${files.length} files).`);

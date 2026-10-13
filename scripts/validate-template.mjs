#!/usr/bin/env node
// Validates this repository as a single Cursor plugin at the repository root.
// Checks the manifest, the paths it references, the MCP config pair, the logo,
// and the frontmatter on every rule, skill, agent and command.

import { promises as fs } from "node:fs";
import path from "node:path";
import process from "node:process";

const repoRoot = process.cwd();
const errors = [];
const warnings = [];

const pluginNamePattern = /^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$/;

function addError(message) {
  errors.push(message);
}

function addWarning(message) {
  warnings.push(message);
}

async function pathExists(targetPath) {
  try {
    await fs.access(targetPath);
    return true;
  } catch {
    return false;
  }
}

async function readJsonFile(filePath, context) {
  let raw;
  try {
    raw = await fs.readFile(filePath, "utf8");
  } catch {
    addError(`${context} is missing: ${filePath}`);
    return null;
  }
  try {
    return JSON.parse(raw);
  } catch (error) {
    addError(`${context} contains invalid JSON (${filePath}): ${error.message}`);
    return null;
  }
}

function parseFrontmatter(content) {
  const normalized = content.replace(/\r\n/g, "\n");
  if (!normalized.startsWith("---\n")) return null;
  const closingIndex = normalized.indexOf("\n---\n", 4);
  if (closingIndex === -1) return null;
  const fields = {};
  for (const line of normalized.slice(4, closingIndex).split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const separator = line.indexOf(":");
    if (separator === -1) continue;
    fields[line.slice(0, separator).trim()] = line.slice(separator + 1).trim();
  }
  return fields;
}

async function walkFiles(dirPath) {
  const files = [];
  const stack = [dirPath];
  while (stack.length > 0) {
    const current = stack.pop();
    for (const entry of await fs.readdir(current, { withFileTypes: true })) {
      const entryPath = path.join(current, entry.name);
      if (entry.isDirectory()) stack.push(entryPath);
      else if (entry.isFile()) files.push(entryPath);
    }
  }
  return files;
}

function isSafeRelativePath(value) {
  if (typeof value !== "string" || value.length === 0) return false;
  if (value.startsWith("http://") || value.startsWith("https://")) return true;
  if (path.isAbsolute(value)) return false;
  const normalized = path.posix.normalize(value.replace(/\\/g, "/"));
  return !normalized.startsWith(".." + "/") && normalized !== "..";
}

function extractPathValues(value) {
  if (typeof value === "string") return [value];
  if (Array.isArray(value)) return value.flatMap((entry) => extractPathValues(entry));
  if (value && typeof value === "object") {
    const candidates = [];
    if (typeof value.path === "string") candidates.push(value.path);
    if (typeof value.file === "string") candidates.push(value.file);
    return candidates;
  }
  return [];
}

async function validateReferencedPath(fieldName, pathValue) {
  if (pathValue.startsWith("http://") || pathValue.startsWith("https://")) return;
  if (!isSafeRelativePath(pathValue)) {
    addError(`Manifest field "${fieldName}" has invalid path "${pathValue}". Use a relative path without ".." or an absolute prefix.`);
    return;
  }
  if (!(await pathExists(path.resolve(repoRoot, pathValue)))) {
    addError(`Manifest field "${fieldName}" references a missing path "${pathValue}".`);
  }
}

async function validateFrontmatterFile(filePath, componentName, requiredKeys) {
  const content = await fs.readFile(filePath, "utf8");
  const parsed = parseFrontmatter(content);
  const relativeFile = path.relative(repoRoot, filePath);
  if (!parsed) {
    addError(`${componentName} file is missing YAML frontmatter: ${relativeFile}`);
    return;
  }
  for (const key of requiredKeys) {
    if (!parsed[key] || parsed[key].length === 0) {
      addError(`${componentName} file is missing "${key}" in its frontmatter: ${relativeFile}`);
    }
  }
  if (parsed.name && !pluginNamePattern.test(parsed.name)) {
    addError(`${componentName} "name" must be lowercase kebab-case: ${relativeFile}`);
  }
}

async function validateComponents() {
  const markdownExt = new Set([".md", ".mdc", ".markdown"]);

  const rulesDir = path.join(repoRoot, "rules");
  if (await pathExists(rulesDir)) {
    for (const file of await walkFiles(rulesDir)) {
      if (markdownExt.has(path.extname(file).toLowerCase())) {
        await validateFrontmatterFile(file, "Rule", ["description"]);
      }
    }
  } else {
    addWarning("No rules/ directory found.");
  }

  const skillsDir = path.join(repoRoot, "skills");
  if (await pathExists(skillsDir)) {
    let count = 0;
    for (const entry of await fs.readdir(skillsDir, { withFileTypes: true })) {
      if (!entry.isDirectory()) continue;
      const skillFile = path.join(skillsDir, entry.name, "SKILL.md");
      if (!(await pathExists(skillFile))) {
        addError(`skills/${entry.name}/ has no SKILL.md.`);
        continue;
      }
      count += 1;
      await validateFrontmatterFile(skillFile, "Skill", ["name", "description"]);
    }
    if (count === 0) addWarning("skills/ holds no skills.");
  } else {
    addWarning("No skills/ directory found.");
  }

  const agentsDir = path.join(repoRoot, "agents");
  if (await pathExists(agentsDir)) {
    for (const file of await walkFiles(agentsDir)) {
      if (markdownExt.has(path.extname(file).toLowerCase())) {
        await validateFrontmatterFile(file, "Agent", ["name", "description"]);
      }
    }
  }

  const commandsDir = path.join(repoRoot, "commands");
  if (await pathExists(commandsDir)) {
    for (const file of await walkFiles(commandsDir)) {
      const ext = path.extname(file).toLowerCase();
      if (markdownExt.has(ext) || ext === ".txt") {
        await validateFrontmatterFile(file, "Command", ["name", "description"]);
      }
    }
  }
}

async function validateMcpConfig() {
  const primary = path.join(repoRoot, "mcp.json");
  const mirror = path.join(repoRoot, ".mcp.json");
  if (!(await pathExists(primary))) {
    addError("mcp.json is missing at the repository root.");
    return;
  }
  const config = await readJsonFile(primary, "mcp.json");
  if (!config) return;
  if (!config.mcpServers || typeof config.mcpServers !== "object" || Object.keys(config.mcpServers).length === 0) {
    addError('mcp.json must hold a non-empty "mcpServers" object.');
    return;
  }
  const raw = JSON.stringify(config);
  const placeholders = raw.match(/\$\{[A-Z0-9_]+\}/g) ?? [];
  if (placeholders.length > 0) {
    addError(`mcp.json uses variables (${placeholders.join(", ")}) but this plugin declares none. Declare them under "variables" in plugin.json or remove them.`);
  }
  if (/sk_(live|test)_/.test(raw)) addError("mcp.json contains a secret key.");
  if (!(await pathExists(mirror))) {
    addError(".mcp.json is missing. It must be a byte-identical copy of mcp.json.");
  } else {
    const [a, b] = await Promise.all([fs.readFile(primary), fs.readFile(mirror)]);
    if (!a.equals(b)) addError("mcp.json and .mcp.json differ. Keep them byte-identical.");
  }
}

async function validateLogo(logoPath) {
  if (typeof logoPath !== "string" || !logoPath.endsWith(".svg")) return;
  const resolved = path.resolve(repoRoot, logoPath);
  if (!(await pathExists(resolved))) return;
  const svg = await fs.readFile(resolved, "utf8");
  const viewBox = svg.match(/viewBox="\s*([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\s*"/);
  if (!viewBox) {
    addError(`Logo ${logoPath} has no viewBox.`);
    return;
  }
  if (Number(viewBox[3]) !== Number(viewBox[4])) {
    addError(`Logo ${logoPath} is not square (viewBox ${viewBox[3]} by ${viewBox[4]}).`);
  }
}

async function main() {
  if (await pathExists(path.join(repoRoot, ".cursor-plugin", "marketplace.json"))) {
    addError("This is a single-plugin repository. Remove .cursor-plugin/marketplace.json.");
  }
  if (await pathExists(path.join(repoRoot, "plugins"))) {
    addError("This is a single-plugin repository. The plugin lives at the root, not under plugins/.");
  }

  const manifestPath = path.join(repoRoot, ".cursor-plugin", "plugin.json");
  const manifest = await readJsonFile(manifestPath, "Plugin manifest");
  if (!manifest) {
    summarizeAndExit();
    return;
  }

  if (typeof manifest.name !== "string" || !pluginNamePattern.test(manifest.name)) {
    addError('"name" in plugin.json must be lowercase and use only alphanumerics, hyphens, and periods.');
  }
  if (typeof manifest.description !== "string" || manifest.description.trim().length === 0) {
    addError('"description" in plugin.json is required for a directory listing.');
  }
  if (typeof manifest.version !== "string" || !/^\d+\.\d+\.\d+$/.test(manifest.version)) {
    addError('"version" in plugin.json must be a semantic version such as 0.2.0.');
  }
  if (manifest.author && typeof manifest.author === "object") {
    for (const key of Object.keys(manifest.author)) {
      if (key !== "name" && key !== "email") {
        addError(`"author.${key}" is not allowed by the Cursor plugin schema (only name and email).`);
      }
    }
  }
  for (const field of ["homepage", "repository"]) {
    if (typeof manifest[field] !== "string" || !manifest[field].startsWith("https://")) {
      addError(`"${field}" in plugin.json must be an https URL.`);
    }
  }
  if (!manifest.logo) addError('"logo" in plugin.json is required for a directory listing.');

  for (const field of ["logo", "rules", "skills", "agents", "commands", "hooks", "mcpServers"]) {
    for (const value of extractPathValues(manifest[field])) {
      await validateReferencedPath(field, value);
    }
  }
  await validateLogo(manifest.logo);
  await validateComponents();
  await validateMcpConfig();

  for (const file of ["README.md", "LICENSE", "SUBMISSION.md"]) {
    if (!(await pathExists(path.join(repoRoot, file)))) addError(`${file} is missing.`);
  }

  summarizeAndExit();
}

function summarizeAndExit() {
  if (warnings.length > 0) {
    console.log("Warnings:");
    for (const warning of warnings) console.log(`- ${warning}`);
    console.log("");
  }
  if (errors.length > 0) {
    console.error("Validation failed:");
    for (const error of errors) console.error(`- ${error}`);
    process.exit(1);
  }
  console.log("Validation passed.");
}

await main();

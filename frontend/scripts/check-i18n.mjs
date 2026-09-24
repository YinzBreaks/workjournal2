// Fails if any locale file is missing a key that en.json has, or has one
// en.json doesn't. Plural objects only need an "other" form.
// Run: npm run check:i18n
import { readFileSync, readdirSync } from "node:fs";

const dir = new URL("../src/i18n/locales/", import.meta.url);
const REQUIRED = ["en", "ar", "fa", "uk"];
const PLURAL_FORMS = new Set(["zero", "one", "two", "few", "many", "other"]);

function isPlural(node) {
  return node && typeof node === "object" && "other" in node &&
    Object.keys(node).every((k) => PLURAL_FORMS.has(k));
}

function keys(node, prefix = "") {
  return Object.entries(node).flatMap(([k, v]) => {
    const path = prefix ? `${prefix}.${k}` : k;
    if (typeof v === "object" && !isPlural(v)) return keys(v, path);
    return [path];
  });
}

const files = readdirSync(dir).filter((f) => f.endsWith(".json"));
const locales = Object.fromEntries(
  files.map((f) => [f.replace(".json", ""), JSON.parse(readFileSync(new URL(f, dir), "utf8"))])
);

let failed = false;
for (const code of REQUIRED) {
  if (!locales[code]) {
    console.error(`missing required locale: ${code}.json`);
    failed = true;
  }
}

const reference = new Set(keys(locales.en));
for (const [code, messages] of Object.entries(locales)) {
  const have = new Set(keys(messages));
  const missing = [...reference].filter((k) => !have.has(k));
  const extra = [...have].filter((k) => !reference.has(k));
  if (!["ltr", "rtl"].includes(messages._meta?.dir)) {
    console.error(`${code}: _meta.dir must be "ltr" or "rtl"`);
    failed = true;
  }
  if (missing.length || extra.length) {
    failed = true;
    if (missing.length) console.error(`${code}: missing ${missing.join(", ")}`);
    if (extra.length) console.error(`${code}: unexpected ${extra.join(", ")}`);
  }
}

if (failed) process.exit(1);
console.log(`i18n OK: ${Object.keys(locales).join(", ")} (${reference.size} keys each)`);

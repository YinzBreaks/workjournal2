import { createContext, useContext, useEffect, useMemo, useState } from "react";

// Every locales/*.json file is picked up automatically: adding a language
// means dropping in one file (copy en.json, translate, set _meta).
const files = import.meta.glob("./locales/*.json", { eager: true });

export const LOCALES = Object.fromEntries(
  Object.entries(files).map(([path, mod]) => [
    path.match(/([\w-]+)\.json$/)[1],
    mod.default ?? mod,
  ])
);

const FALLBACK = "en";
const STORAGE_KEY = "bj_locale";

function lookup(messages, key) {
  return key.split(".").reduce((node, part) => node?.[part], messages);
}

function initialLocale() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && LOCALES[saved]) return saved;
  } catch {
    // Storage blocked: fall through to the browser language.
  }
  const browser = (navigator.language || FALLBACK).split("-")[0];
  return LOCALES[browser] ? browser : FALLBACK;
}

const I18nContext = createContext(null);

export function I18nProvider({ children }) {
  const [locale, setLocaleState] = useState(initialLocale);

  useEffect(() => {
    document.documentElement.lang = locale;
    document.documentElement.dir = LOCALES[locale]._meta.dir;
  }, [locale]);

  const value = useMemo(() => {
    const plurals = new Intl.PluralRules(locale);

    // t("tasks.position", { current: 1, total: 3 }). If the entry is an
    // object, `count` picks the plural form (one/few/many/other...).
    function t(key, vars = {}) {
      let message = lookup(LOCALES[locale], key) ?? lookup(LOCALES[FALLBACK], key) ?? key;
      if (typeof message === "object") {
        message = message[plurals.select(vars.count ?? 0)] ?? message.other;
      }
      return String(message).replace(/\{(\w+)\}/g, (_, name) => vars[name] ?? `{${name}}`);
    }

    function setLocale(next) {
      setLocaleState(next);
      try {
        localStorage.setItem(STORAGE_KEY, next);
      } catch {
        // Not remembered across visits; still switches for this one.
      }
    }

    return { locale, setLocale, t };
  }, [locale]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within I18nProvider");
  return ctx;
}

export function useT() {
  return useI18n().t;
}

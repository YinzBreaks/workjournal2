// Dates from the API are plain "YYYY-MM-DD" strings. Parsing them with
// `new Date("2026-09-24")` treats them as UTC midnight, which shows as the
// previous day in Pittsburgh. Appending a local time avoids that.
export function formatDate(isoDate, locale) {
  return new Date(`${isoDate}T00:00:00`).toLocaleDateString(locale, {
    month: "short",
    day: "numeric",
  });
}

// Today's date in the user's time zone, as "YYYY-MM-DD".
export function todayISO() {
  return new Date().toLocaleDateString("en-CA");
}

// 150 -> "2h 30m" (or the locale's own short units).
export function formatMinutes(totalMinutes, locale) {
  const unit = (value, name) =>
    new Intl.NumberFormat(locale, { style: "unit", unit: name, unitDisplay: "narrow" }).format(value);
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  if (hours === 0) return unit(minutes, "minute");
  if (minutes === 0) return unit(hours, "hour");
  return `${unit(hours, "hour")} ${unit(minutes, "minute")}`;
}

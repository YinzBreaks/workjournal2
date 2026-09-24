// Dates from the API are plain "YYYY-MM-DD" strings. Parsing them with
// `new Date("2026-09-24")` treats them as UTC midnight, which shows as the
// previous day in Pittsburgh. Appending a local time avoids that.
export function formatDate(isoDate) {
  return new Date(`${isoDate}T00:00:00`).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });
}

// Today's date in the user's time zone, as "YYYY-MM-DD".
export function todayISO() {
  return new Date().toLocaleDateString("en-CA");
}

export function formatMinutes(totalMinutes) {
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  if (hours === 0) return `${minutes}m`;
  if (minutes === 0) return `${hours}h`;
  return `${hours}h ${minutes}m`;
}

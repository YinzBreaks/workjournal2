// Tell the beattietech.local hub something happened, so it shows up in the
// ecosystem activity feed. Same contract as beattieNetTrack's events.ts:
// Caddy routes /api/events on every host to the hub. Fire-and-forget: a
// hub outage must never break the journal.
const APP_ID = "journal";

export function emitHubEvent(eventType, payload) {
  const body = {
    app_id: APP_ID,
    event_type: eventType,
    appId: APP_ID,
    eventType,
    payload: { domains: [], contentType: "journal", ...payload },
  };
  try {
    fetch("/api/events", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      keepalive: true,
    }).catch(() => {});
  } catch {
    // Ignore: events are best-effort.
  }
}

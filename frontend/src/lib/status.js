// Assignment statuses, in board order. Must match AssignmentStatus in
// backend/app/models.py. Labels live in the locale files under "status".
export const STATUSES = ["not_started", "in_progress", "complete"];

// Muted on purpose: calm UI, no loud badges.
export const STATUS_PILL = {
  not_started: "bg-gray-100 text-gray-600",
  in_progress: "bg-gray-100 text-gray-700",
  complete: "bg-brand-50 text-brand-700",
};

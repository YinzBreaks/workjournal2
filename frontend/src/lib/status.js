// Assignment statuses, in board order. Must match AssignmentStatus in
// backend/app/models.py.
export const STATUSES = ["not_started", "in_progress", "complete"];

export const STATUS_LABEL = {
  not_started: "Not started",
  in_progress: "In progress",
  complete: "Complete",
};

export const STATUS_PILL = {
  not_started: "bg-gray-100 text-gray-600",
  in_progress: "bg-amber-50 text-amber-700",
  complete: "bg-green-50 text-green-700",
};

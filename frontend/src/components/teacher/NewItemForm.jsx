import { useState } from "react";
import { useT } from "../../i18n";
import ItemForm from "./ItemForm";

// A "+ New ..." button that opens an ItemForm. onSubmit({ title,
// description }) must return a promise; the form closes when it resolves.
export default function NewItemForm({ openLabel, titleLabel, descriptionLabel, onSubmit }) {
  const t = useT();
  const [open, setOpen] = useState(false);

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="text-sm font-medium text-brand-600 hover:text-brand-700"
      >
        {openLabel}
      </button>
    );
  }

  return (
    <ItemForm
      titleLabel={titleLabel}
      descriptionLabel={descriptionLabel}
      submitLabel={t("teacher.create")}
      savingLabel={t("teacher.creating")}
      onSubmit={async (fields) => {
        await onSubmit(fields);
        setOpen(false);
      }}
      onCancel={() => setOpen(false)}
    />
  );
}

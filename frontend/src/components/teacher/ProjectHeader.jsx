import { useState } from "react";
import { useT } from "../../i18n";
import ItemForm from "./ItemForm";

// A project's name and description, with Edit and Delete.
// onSave(project, { title, description }) returns a promise; onDelete(project)
// confirms and deletes.
export default function ProjectHeader({ project, onSave, onDelete }) {
  const t = useT();
  const [editing, setEditing] = useState(false);

  if (editing) {
    return (
      <div className="mb-3 rounded-lg border border-gray-200 bg-white p-4">
        <ItemForm
          initial={project}
          titleLabel={t("teacher.projectTitle")}
          descriptionLabel={t("teacher.projectDescription")}
          submitLabel={t("teacher.save")}
          savingLabel={t("teacher.saving")}
          onSubmit={async (fields) => {
            await onSave(project, fields);
            setEditing(false);
          }}
          onCancel={() => setEditing(false)}
        />
      </div>
    );
  }

  return (
    <>
      <div className="flex items-baseline justify-between gap-4">
        <h3 className="text-lg font-semibold text-gray-900">{project.title}</h3>
        <div className="flex shrink-0 gap-3 text-xs">
          <button onClick={() => setEditing(true)} className="text-gray-500 hover:text-gray-800">
            {t("teacher.edit")}
          </button>
          <button onClick={() => onDelete(project)} className="text-gray-500 hover:text-red-600">
            {t("teacher.deleteProject")}
          </button>
        </div>
      </div>
      {project.description && <p className="text-sm text-gray-500 mb-3">{project.description}</p>}
    </>
  );
}

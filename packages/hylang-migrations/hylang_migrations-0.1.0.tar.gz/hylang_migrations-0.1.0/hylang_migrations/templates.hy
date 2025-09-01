(require hyrule [-> ->> as-> let])

(defn create-migration-template [name]
  "Generate a migration template"
  f"(require hyrule [-> ->> as-> let])

(defn up []
  \"Run the migration\"
  (print f\"Running migration: {name}\")
  ;; Add your migration code here
  None)

(defn down []
  \"Rollback the migration\"
  (print f\"Rolling back migration: {name}\")
  ;; Add your rollback code here
  None)
")

(defn create-model-template [name]
  "Generate a model template"
  f"(require hyrule [-> ->> as-> let])

(defclass {name} []
  (defn __init__ [self]
    ;; Initialize model
    None))
")

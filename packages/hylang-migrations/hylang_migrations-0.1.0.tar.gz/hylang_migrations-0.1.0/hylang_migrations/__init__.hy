;;; __init__.hy - Pure Hylang package initialization
;;; Package entry point for hylang_migrations

(setv __version__ "0.1.0")
(setv __author__ "Your Name")
(setv __email__ "your.email@example.com")

;; Re-export main components
(import hylang_migrations.migrations [Migration MigrationHistory MigrationRunner])
(import hylang_migrations.cli [main :as cli-main])
(import hylang_migrations.config [Config])

(setv __all__ [
  "Migration"
  "MigrationHistory" 
  "MigrationRunner"
  "Config"
  "init-config"
  "cli-main"
  "__version__"
])

;; Package initialization
(defn init []
  "Initialize the hylang-migrations package"
  ;; Ensure Hylang v1.1.0 features are available
  (import hy)
  (when (< (tuple (map int (.split hy.__version__ "."))) #(1 1 0))
    (print (.format "Warning: Hylang {} detected. Version 1.1.0+ recommended." hy.__version__)))
  None)

(init)

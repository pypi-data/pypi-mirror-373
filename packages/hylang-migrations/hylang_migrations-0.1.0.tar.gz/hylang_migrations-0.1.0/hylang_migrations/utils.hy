;;; utils.hy - Utility functions for migration tool

(import hashlib)
(import os)
(import re)
(import pathlib [Path])
(import importlib.util)

(defn calculate-checksum [content]
  "Calculate SHA256 checksum of content"
  (-> (hashlib.sha256)
      (.update (.encode content "utf-8"))
      (.hexdigest)))

(defn load-migration-file [filepath]
  "Dynamically load a migration file"
  ;; Stub - import .hy file and return migration instance
  (print f"Loading migration from: {filepath}")
  None)

(defn get-migration-files [migrations-dir]
  "Get all migration files sorted by version"
  (setv migration-pattern (re.compile r"^(\d+)_(.+)\.hy$"))
  (setv files [])
  
  (for [file (.iterdir (Path migrations-dir))]
    (when (and (.is-file file)
               (.match migration-pattern file.name))
      (.append files file)))
  
  ;; Sort by version number
  (.sort files :key (fn [f] 
                      (-> (re.match migration-pattern f.name)
                          (.group 1)
                          int)))
  files)

(defn parse-migration-filename [filename]
  "Extract version and name from migration filename"
  (setv pattern (re.compile r"^(\d+)_(.+)\.hy$"))
  (setv match (.match pattern filename))
  
  (if match
    {:version (.group match 1)
     :name (.group match 2)}
    None))

(defn generate-migration-template [name]
  "Generate migration file template"
  f";;; Migration: {name}

(import migrations [Migration])

(defclass {(.title (.replace name \"_\" \"\"))} [Migration]
  \"Description of migration\"
  
  (defn __init__ [self]
    (.__init__ (super) \"VERSION\" \"{name}\"))
  
  (defn up [self]
    \"Apply migration\"
    ;; Add your forward migration logic here
    (setv self.up-sql
      [;; SQL statements
       ])
    
    (for [sql self.up-sql]
      ;; Execute SQL
      pass))
  
  (defn down [self]
    \"Rollback migration\"
    ;; Add your rollback logic here
    (setv self.down-sql
      [;; SQL statements
       ])
    
    (for [sql self.down-sql]
      ;; Execute SQL
      pass)))

;; Export migration instance
(setv migration ({(.title (.replace name \"_\" \"\"))}))")

(defn backup-database [db-path]
  "Create backup of database before migration"
  (import shutil)
  (import datetime [datetime])
  
  (setv timestamp (.strftime (datetime.now) "%Y%m%d_%H%M%S"))
  (setv backup-path f"{db-path}.backup_{timestamp}")
  
  (shutil.copy2 db-path backup-path)
  (print f"Database backed up to: {backup-path}")
  backup-path)

(defn validate-database-connection [db-path]
  "Validate database is accessible"
  (import sqlite3)
  
  (try
    (setv conn (sqlite3.connect db-path))
    (.execute conn "SELECT 1")
    (.close conn)
    True
    (except [Exception :as e]
      (print f"Database connection failed: {e}")
      False)))

(defn get-table-schema [connection table-name]
  "Get CREATE TABLE statement for a table"
  (setv cursor (.execute connection 
                         f"SELECT sql FROM sqlite_master 
                          WHERE type='table' AND name='{table-name}'"))
  (setv result (.fetchone cursor))
  (if result
    (get result 0)
    None))

(defn diff-schemas [old-schema new-schema]
  "Compare two schema definitions"
  ;; Stub - implement schema comparison
  {:added [] :removed [] :modified []})

(defn format-sql [sql]
  "Format SQL for readable output"
  (-> sql
      (.replace "(" "(\n  ")
      (.replace "," ",\n  ")
      (.replace ")" "\n)")))

(defn is-migration-applied [connection version]
  "Check if a migration version is already applied"
  (setv cursor (.execute connection
                         "SELECT 1 FROM migration_history WHERE version = ?"
                         [version]))
  (is-not (.fetchone cursor) None))

(defn get-latest-version [connection]
  "Get the latest applied migration version"
  (setv cursor (.execute connection
                         "SELECT version FROM migration_history 
                          ORDER BY version DESC LIMIT 1"))
  (setv result (.fetchone cursor))
  (if result
    (get result 0)
    None))

(defn transaction-wrapper [connection func]
  "Execute function within a transaction"
  (try
    (.execute connection "BEGIN")
    (setv result (func))
    (.commit connection)
    result
    (except [Exception :as e]
      (.rollback connection)
      (raise e))))

;;; migrations.hy - Core migration engine for SQLite schema management
;;; Uses SQLObject for ORM integration

(import sqlobject [SQLObject StringCol IntCol DateTimeCol BoolCol])
(import sqlobject.sqlbuilder [Select])
(import sqlite3)
(import datetime [datetime])
(import pathlib [Path])

;;; Migration tracking table definition
(defclass MigrationHistory [SQLObject]
  "Table to track applied migrations"
  (setv version (StringCol :length 255 :unique True :notNone True))
  (setv name (StringCol :length 255 :notNone True))
  (setv applied-at (DateTimeCol :default datetime.now :notNone True))
  (setv checksum (StringCol :length 64))  ; SHA256 of migration content
  (setv success (BoolCol :default True)))

;;; Base Migration class
(defclass Migration []
  "Base class for all migrations"
  
  (defn __init__ [self version name]
    (setv self.version version)
    (setv self.name name)
    (setv self.up-sql [])
    (setv self.down-sql []))
  
  (defn up [self]
    "Apply migration - override in subclasses"
    (raise NotImplementedError))
  
  (defn down [self]
    "Rollback migration - override in subclasses"
    (raise NotImplementedError))
  
  (defn get-checksum [self]
    "Calculate checksum of migration content"
    ;; Stub - implement SHA256 hashing
    "placeholder-checksum")
  
  (defn __repr__ [self]
    (.format "{}_{}" self.version self.name)))

;;; Migration Runner
(defclass MigrationRunner []
  "Handles migration execution and tracking"
  
  (defn __init__ [self db-path migrations-dir]
    (setv self.db-path db-path)
    (setv self.migrations-dir (Path migrations-dir))
    (setv self.connection None))
  
  (defn connect [self]
    "Establish database connection"
    (setv self.connection (sqlite3.connect self.db-path))
    ;; Initialize SQLObject connection
    ;; Stub - setup SQLObject connection string
    )
  
  (defn ensure-migration-table [self]
    "Create migration history table if not exists"
    ;; Stub - create MigrationHistory table
    (when self.connection
      (.execute self.connection
        "CREATE TABLE IF NOT EXISTS migration_history (
           id INTEGER PRIMARY KEY,
           version TEXT UNIQUE NOT NULL,
           name TEXT NOT NULL,
           applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
           checksum TEXT,
           success BOOLEAN DEFAULT 1
         )")))
  
  (defn get-applied-migrations [self]
    "Return list of applied migration versions"
    ;; Stub - query migration_history table
    [])
  
  (defn get-pending-migrations [self]
    "Return list of migrations not yet applied"
    ;; Load all migrations from directory
    (setv all-migrations (load-migrations self.migrations-dir))
    
    ;; Get applied migration versions
    (setv applied-versions (set))
    (when self.connection
      (try
        (setv cursor (.execute self.connection 
                              "SELECT version FROM migration_history"))
        (setv applied-versions (set (lfor row cursor (get row 0))))
        (except [e Exception]
          ;; Table might not exist yet
          None)))
    
    ;; Return migrations not yet applied
    (lfor m all-migrations 
          :if (not (in m.version applied-versions))
          m))
  
  (defn apply-migration [self migration]
    "Execute a single migration"
    (try
      (print (.format "Applying migration {}: {}" migration.version migration.name))
      ;; Begin transaction
      (.execute self.connection "BEGIN")
      
      ;; Set connection and run migration up method
      (when (hasattr migration "set_connection")
        (migration.set_connection self.connection))
      (migration.up)
      
      ;; Record in history
      (.execute self.connection
        "INSERT INTO migration_history (version, name, checksum) VALUES (?, ?, ?)"
        [migration.version migration.name (migration.get-checksum)])
      
      ;; Commit transaction
      (.commit self.connection)
      (print (.format "✓ Migration {} applied successfully" migration.version))
      True
      (except [e Exception]
        ;; Rollback on error
        (.rollback self.connection)
        (print (.format "✗ Migration {} failed: {}" migration.version e))
        False)))
  
  (defn rollback-migration [self migration]
    "Rollback a single migration"
    ;; Stub - execute migration.down() and update history
    (try
      (print (.format "Rolling back migration {}" migration.version))
      (migration.down)
      ;; Remove from history
      True
      (except [e Exception]
        (print (.format "✗ Rollback failed: {}" e))
        False)))
  
  (defn run-migrations [self &optional [target-version None]]
    "Run all pending migrations up to target version"
    (self.connect)
    (self.ensure-migration-table)
    
    (setv pending (self.get-pending-migrations))
    (if (not pending)
      (print "No pending migrations")
      (for [migration pending]
        (when (or (is target-version None)
                  (<= migration.version target-version))
          (self.apply-migration migration)))))
  
  (defn status [self]
    "Show migration status"
    (self.connect)
    (self.ensure-migration-table)
    
    (print "\n=== Migration Status ===")
    (setv applied (self.get-applied-migrations))
    (setv pending (self.get-pending-migrations))
    
    (print (.format "Applied migrations: {}" (len applied)))
    (for [m applied]
      (print (.format "  ✓ {}" m)))
    
    (print (.format "\nPending migrations: {}" (len pending)))
    (for [m pending]
      (print (.format "  ○ {}" m)))))

;;; Migration loader utilities
(defn load-migrations [migrations-dir]
  "Load all migration files from directory"
  (import pathlib [Path])
  (import importlib.util)
  
  (setv migrations [])
  (setv migrations-path (Path migrations-dir))
  
  (when (.exists migrations-path)
    ;; Find all .hy files in the migrations directory
    (setv migration-files (sorted (.glob migrations-path "*.hy")))
    
    (for [file migration-files]
      ;; Skip non-migration files like __init__.hy or README
      (import re)
      (when (and (re.match r"^\d+.*\.hy$" file.name)
                 (not (= file.name "__init__.hy")))
        (try
          ;; Load the migration module dynamically using standard Python import
          ;; Hy registers itself as an import hook, so .hy files work automatically
          (import importlib.util)
          (setv spec (importlib.util.spec-from-file-location 
                       (.format "migration_{}" file.stem)
                       (str file)))
          (setv module (importlib.util.module-from-spec spec))
          (spec.loader.exec_module module)
          
          ;; Get the migration instance from the module
          (if (hasattr module "migration")
            (.append migrations module.migration)
            (print (.format "Warning: {} has no 'migration' object" file.name)))
          
          (except [e Exception]
            (print (.format "Warning: Could not load migration {}: {}" file.name e))))))
  
  ;; Return sorted by version
  (sorted migrations :key (fn [m] m.version))))

(defn create-migration [version name]
  "Generate a new migration file template"
  (setv timestamp (.strftime (datetime.now) "%Y%m%d%H%M%S"))
  (setv filename (.format "{}_{}.hy" timestamp name))
  
  ;; Stub - create migration file with template
  (print (.format "Created migration: {}" filename)))

;;; Validation utilities
(defn validate-migration-order [migrations]
  "Ensure migrations are in correct order"
  ;; Stub - check version ordering
  True)

(defn check-migration-conflicts [migrations]
  "Check for version conflicts"
  ;; Stub - ensure no duplicate versions
  True)

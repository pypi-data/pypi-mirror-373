;;; config.hy - Configuration management in pure Hylang v1.1.0

(require hyrule [-> ->> as->])
(import os)
(import pathlib [Path])
(import configparser [ConfigParser])

;;; Default configuration values
(setv DEFAULT-CONFIG {
  :database {
    :path "database.db"
    :type "sqlite"
    :connection-string None
  }
  :migrations {
    :directory "migrations"
    :table-name "migration_history"
    :auto-transaction True
    :verify-checksums True
  }
  :sqlobject {
    :debug False
    :cache True
    :lazy-update True
  }
  :logging {
    :level "INFO"
    :format "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    :file None
  }
})

;;; Configuration class
(defclass Config []
  "Configuration management for migrations"
  
  (defn __init__ [self &optional [config-file None]]
    (setv self.config (dict DEFAULT-CONFIG))
    (setv self.config-file config-file)
    (when config-file
      (self.load-from-file config-file)))
  
  (defn load-from-file [self filepath]
    "Load configuration from file"
    (let [path (Path filepath)]
      (when (path.exists)
        (cond
          ;; Handle .hy config files (Hylang format)
          (= path.suffix ".hy")
           (self.load-hy-config path)
          
          ;; Handle .ini config files
          (or (= path.suffix ".ini") 
               (= path.suffix ""))
           (self.load-ini-config path)
          
          ;; Handle .migrations file (default format)
          (= path.name ".migrations")
           (self.load-migrations-config path)))))
  
  (defn load-hy-config [self filepath]
    "Load Hylang format configuration"
    (try
      (let [content (filepath.read-text)
            ;; Safely evaluate the Hylang config
            config-dict (eval (read-str content))]
        (self.merge-config config-dict))
      (except [e Exception]
        (print (.format "Error loading Hylang config: {}" e)))))
  
  (defn load-ini-config [self filepath]
    "Load INI format configuration"
    (let [parser (ConfigParser)]
      (parser.read (str filepath))
      (for [section (parser.sections)]
        (when (in section self.config)
          (for [#(key value) (parser.items section)]
            (setv (get (get self.config section) 
                      (.replace key "-" "_"))
                  (self.parse-value value)))))))
  
  (defn load-migrations-config [self filepath]
    "Load .migrations configuration file"
    (let [content (filepath.read-text)]
      (cond
        ;; Try to parse as Hylang dict
        [(.startswith content "{")
         (self.load-hy-config filepath)]
        
        ;; Otherwise parse as INI
        [True
         (self.load-ini-config filepath)])))
  
  (defn merge-config [self new-config]
    "Merge new configuration with existing"
    (for [#(section values) (new-config.items)]
      (if (in section self.config)
        ((.get self.config section).update values)
        (setv (get self.config section) values))))
  
  (defn parse-value [self value]
    "Parse configuration value from string"
    (cond
      (= value "true") True
      (= value "false") False
      (= value "none") None
      (value.isdigit) (int value)
      (try (float value) (except [ValueError] False)) (float value)
      True value))
  
  (defn get [self path &optional [default None]]
    "Get configuration value by dotted path"
    (let [parts (.split path ".")
          value self.config]
      (for [part parts]
        (if (and (not (none? value)) (in part value))
          (setv value (get value part))
          (return default)))
      value))
  
  (defn set [self path value]
    "Set configuration value by dotted path"
    (let [parts (.split path ".")
          target self.config]
      (for [part (cut parts 0 -1)]
        (when (not (in part target))
          (setv (get target part) {}))
        (setv target (get target part)))
      (setv (get target (get parts -1)) value)))
  
  (defn get-connection-string [self]
    "Build SQLObject connection string"
    (let [db-type (self.get "database.type" "sqlite")
          db-path (self.get "database.path" "database.db")]
      (cond
        (= db-type "sqlite")
         (.format "sqlite:{}" db-path)
        
        (self.get "database.connection_string")
         (self.get "database.connection_string")
        
        True
         (raise (ValueError (.format "Unsupported database type: {}" db-type))))))
  
  (defn init-sqlobject [self]
    "Initialize SQLObject with configuration"
    (import sqlobject)
    (let [conn-string (self.get-connection-string)]
      (sqlobject.connectionForURI conn-string)))
  
  (defn save [self &optional [filepath None]]
    "Save configuration to file"
    (let [path (Path (or filepath self.config-file ".migrations"))]
      (if (or (= path.suffix ".hy") (= path.name ".migrations"))
        ;; Save as Hylang format
        (path.write-text (repr self.config))
        ;; Save as INI format
        (let [parser (ConfigParser)]
          (for [#(section values) (self.config.items)]
            (parser.add-section section)
            (for [#(key value) (values.items)]
              (parser.set section key (str value))))
          (with [f (open (str path) "w")]
            (parser.write f))))))
  
  (defn __repr__ [self]
    (.format "<Config: {}>" (or self.config-file "default")))

;;; Global configuration instance
(setv _global-config None)

(defn init-config [&optional [config-file None]]
  "Initialize global configuration"
  (global _global-config)
  (setv _global-config (Config :config-file config-file))
  _global-config)

(defn get-config []
  "Get global configuration instance"
  (global _global-config)
  (when (none? _global-config)
    (init-config))
  _global-config)

(defn load-config [filepath]
  "Load configuration from file"
  (let [config (Config)]
    (config.load-from-file filepath)
    config))

;;; Environment variable support
(defn load-from-env [config]
  "Load configuration from environment variables"
  ;; Database settings
  (when (os.getenv "DB_PATH")
    (config.set "database.path" (os.getenv "DB_PATH")))
  (when (os.getenv "DB_TYPE")
    (config.set "database.type" (os.getenv "DB_TYPE")))
  
  ;; Migration settings
  (when (os.getenv "MIGRATIONS_DIR")
    (config.set "migrations.directory" (os.getenv "MIGRATIONS_DIR")))
  (when (os.getenv "MIGRATIONS_TABLE")
    (config.set "migrations.table_name" (os.getenv "MIGRATIONS_TABLE")))
  
  ;; SQLObject settings
  (when (os.getenv "SQLOBJECT_DEBUG")
    (config.set "sqlobject.debug" 
                (= (os.getenv "SQLOBJECT_DEBUG") "true")))
  
  config)

;;; Export main components
(setv __all__ ["Config" "init_config" "get_config" "load_config" "load_from_env"]))

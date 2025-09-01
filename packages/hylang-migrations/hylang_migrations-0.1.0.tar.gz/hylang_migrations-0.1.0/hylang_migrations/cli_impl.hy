;;; CLI implementation in Hylang - called by Python wrapper
;;; This provides backward compatibility with the original Hylang implementation

(import argparse)
(import sys)
(import pathlib [Path])
(import datetime [datetime])

(defn parse-args []
  "Parse command-line arguments"
  ;; This is now handled by the Python Click wrapper
  ;; Kept for backward compatibility
  None)

(defn init-project [migrations-dir db-path]
  "Initialize migration system in a project"
  ;; Create migrations directory
  (.mkdir (Path migrations-dir) :parents True :exist-ok True)
  
  ;; Create initial __init__.hy
  (setv init-file (/ (Path migrations-dir) "__init__.hy"))
  (when (not (.exists init-file))
    (.write-text init-file ";;; Migrations package\n"))
  
  True)

(defn create-migration [name migrations-dir]
  "Create a new migration file"
  (setv timestamp (.strftime (datetime.now) "%Y%m%d%H%M%S"))
  (setv filename (.format "{}_{}.hy" timestamp name))
  (setv filepath (/ (Path migrations-dir) filename))
  
  ;; Generate migration template
  (setv class-name (.title (.replace name "_" "")))
  (setv template (.format ";;; Migration: {}
;;; Version: {}

(defclass {} []
  \"Migration: {}\"
  
  (defn __init__ [self]
    (setv self.version \"{}\")
    (setv self.name \"{}\"))
  
  (defn up [self connection]
    \"Apply migration\"
    ;; TODO: Add your forward migration logic here
    (.execute connection
      \"-- Add your SQL here\")
    (print (.format \"  ✅ Applied migration {}: {}\" self.version self.name)))
  
  (defn down [self connection]
    \"Rollback migration\"
    ;; TODO: Add your rollback logic here
    (.execute connection
      \"-- Add your rollback SQL here\")
    (print (.format \"  ✅ Rolled back migration {}: {}\" self.version self.name)))
  
  (defn get-checksum [self]
    \"Calculate checksum\"
    (import hashlib)
    (-> (hashlib.sha256)
        (.update (.encode (+ self.version self.name) \"utf-8\"))
        (.hexdigest))))

;; Export migration instance
(setv migration ({}))"
    name timestamp class-name name timestamp name class-name))
  
  (.write-text filepath template)
  {:success True :filepath (str filepath) :version timestamp :name name})
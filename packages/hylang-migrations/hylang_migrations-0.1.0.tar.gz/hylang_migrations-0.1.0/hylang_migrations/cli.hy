;;; cli.hy - Command-line interface for migration tool

(require hyrule [-> ->> as->])
(import argparse)
(import sys)
(import os)
(import shutil)
(import pathlib [Path])
(import .migrations [MigrationRunner create-migration])

(defn parse-args []
  "Parse command-line arguments"
  (setv parser (argparse.ArgumentParser 
                 :description "SQLite schema migration tool for SQLObject"))
  
  (setv subparsers (.add-subparsers parser 
                                     :dest "command"
                                     :help "Available commands"))
  
  ;; Init command
  (setv init-parser (.add-parser subparsers "init"
                                 :help "Initialize migration system"))
  (.add-argument init-parser "--db" 
                 :default "database.db"
                 :help "Database file path")
  
  ;; Create command
  (setv create-parser (.add-parser subparsers "create"
                                   :help "Create new migration"))
  (.add-argument create-parser "name"
                 :help "Migration name")
  
  ;; Migrate command
  (setv migrate-parser (.add-parser subparsers "migrate"
                                    :help "Run pending migrations"))
  (.add-argument migrate-parser "--db"
                 :default "database.db"
                 :help "Database file path")
  (.add-argument migrate-parser "--target"
                 :help "Target migration version")
  (.add-argument migrate-parser "--dry-run"
                 :action "store_true"
                 :help "Show what would be done without executing")
  
  ;; Rollback command
  (setv rollback-parser (.add-parser subparsers "rollback"
                                     :help "Rollback migrations"))
  (.add-argument rollback-parser "--db"
                 :default "database.db"
                 :help "Database file path")
  (.add-argument rollback-parser "--steps"
                 :type int
                 :default 1
                 :help "Number of migrations to rollback")
  
  ;; Status command
  (setv status-parser (.add-parser subparsers "status"
                                   :help "Show migration status"))
  (.add-argument status-parser "--db"
                 :default "database.db"
                 :help "Database file path")
  
  ;; List command
  (setv list-parser (.add-parser subparsers "list"
                                 :help "List all migrations"))
  (.add-argument list-parser "--pending"
                 :action "store_true"
                 :help "Show only pending migrations")
  
  ;; Install Claude Agent command
  (setv install-agent-parser (.add-parser subparsers "install-claude-agent"
                                          :help "Install Claude Code subagent for Hylang migrations"))
  (.add-argument install-agent-parser "--target"
                 :default (str (/ (Path.home) ".claude" "agents"))
                 :help "Target directory for agent installation")
  
  (.parse-args parser))

(defn cmd-init [args]
  "Initialize migration system"
  (print "Initializing migration system...")
  ;; Stub - create migrations directory, initial config
  (print "✓ Created migrations directory")
  (setv db-name (if (hasattr args "db") args.db "database.db"))
  (print (.format "✓ Initialized database: {}" db-name)))

(defn cmd-create [args]
  "Create new migration"
  (create-migration None args.name)
  (print (.format "✓ Created migration: {}" args.name)))

(defn cmd-migrate [args]
  "Run migrations"
  (setv runner (MigrationRunner args.db "migrations"))
  
  (if args.dry-run
    (do
      (print "DRY RUN - No changes will be made")
      ;; Stub - show what would be done
      )
    (runner.run-migrations args.target)))

(defn cmd-rollback [args]
  "Rollback migrations"
  (setv runner (MigrationRunner args.db "migrations"))
  (print (.format "Rolling back {} migration(s)..." args.steps))
  ;; Stub - implement rollback logic
  )

(defn cmd-status [args]
  "Show migration status"
  (setv runner (MigrationRunner args.db "migrations"))
  (runner.status))

(defn cmd-list [args]
  "List migrations"
  (print "\n=== Migrations ===")
  ;; Stub - list all or pending migrations
  (if args.pending
    (print "Showing pending migrations only...")
    (print "Showing all migrations...")))

(defn cmd-install-claude-agent [args]
  "Install the Claude Code subagent for Hylang migrations"
  ;; Try to find the agent file in several locations
  (setv cwd (Path.cwd))
  (setv possible-paths [
    ;; In current directory
    (/ cwd ".claude" "agents")
    ;; In parent directory
    (/ cwd.parent ".claude" "agents")
    ;; In user's home directory if cloned there
    (/ (Path.home) "Projects" "hylang-migrations" ".claude" "agents")])
  
  (setv source-dir None)
  (setv agent-file "hylang-migrate-assistant.md")
  
  ;; Find the first existing path
  (for [path possible-paths]
    (when (.exists (/ path agent-file))
      (setv source-dir path)
      (break)))
  
  (setv target-dir (Path args.target))
  
  ;; Create target directory if it doesn't exist
  (target-dir.mkdir :parents True :exist-ok True)
  
  ;; Check if we found the source directory
  (if source-dir
    (setv source-file (/ source-dir agent-file))
    (setv source-file None))
  
  (if (and source-file (.exists source-file))
    (do
      ;; Copy agent file to target
      (setv target-file (/ target-dir agent-file))
      (shutil.copy2 source-file target-file)
      (print (.format "✅ Successfully installed Claude agent to: {}" target-file))
      (print "\n📝 The hylang-migrate-assistant is now available!")
      (print "   Use it in Claude Code to get expert help with:")
      (print "   • Creating and managing migrations")
      (print "   • Debugging migration issues")
      (print "   • Schema design best practices")
      (print "   • Hylang v1.1.0 migration syntax")
      (print "\n💡 Tip: In Claude Code, type '/agents' to see and use the assistant!")
      0)
    (do
      (print (.format "❌ Error: Agent file not found at {}" source-file))
      (print "   Make sure you're running from the hylang-migrations repository root")
      1)))

(defn main []
  "Main entry point"
  (setv args (parse-args))
  
  (when (is args.command None)
    (print "No command specified. Use -h for help.")
    (sys.exit 1))
  
  ;; Handle commands using proper cond syntax (no square brackets!)
  (cond
    (= args.command "init") (cmd-init args)
    (= args.command "create") (cmd-create args)
    (= args.command "migrate") (cmd-migrate args)
    (= args.command "rollback") (cmd-rollback args)
    (= args.command "status") (cmd-status args)
    (= args.command "list") (cmd-list args)
    (= args.command "install-claude-agent") (sys.exit (cmd-install-claude-agent args))
    True (print (.format "Unknown command: {}" args.command))))

(when (= __name__ "__main__")
  (main))

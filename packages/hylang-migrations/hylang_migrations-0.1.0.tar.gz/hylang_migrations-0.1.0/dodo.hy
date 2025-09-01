#!/usr/bin/env hy
;;; Build and deployment tasks for hylang-migrations package
;;; Uses doit task automation for packaging and PyPI distribution

(import doit)
(import os)
(import sys)
(import shutil)
(import subprocess)

(defn run-command [cmd]
  "Run a shell command and return the result"
  (subprocess.run cmd :shell True :check True))

(defn task-clean []
  "Clean build artifacts and cache"
  {"actions" [(fn []
                (for [dir ["build" "dist" "*.egg-info" "__pycache__" ".pytest_cache" 
                          "src/*.egg-info" "src/hylang_migrations.egg-info"]]
                  (when (os.path.exists dir)
                    (if (os.path.isdir dir)
                      (shutil.rmtree dir)
                      (os.remove dir))))
                ;; Clean test databases
                (for [db ["test.db" "test_cli.db" "test_migration.db" "demo/demo.db"]]
                  (when (os.path.exists db)
                    (os.remove db)))
                (print "Cleaned build artifacts and test databases"))]
   "verbosity" 2
   "doc" "Remove build artifacts, dist, egg-info, cache directories, and test databases"})

(defn task-lint []
  "Run code quality checks on Hy files"
  {"actions" [(fn []
                (print "Checking Hy syntax...")
                ;; Check main source files
                (for [file (os.listdir "src/hylang_migrations")]
                  (when (.endswith file ".hy")
                    (let [filepath (os.path.join "src/hylang_migrations" file)]
                      (try
                        (with [f (open filepath "r")]
                          (import hy)
                          (hy.read-many (.read f)))
                        (print (.format "  ✓ {}" filepath))
                        (except [e Exception]
                          (print (.format "  ✗ {}: {}" filepath e))
                          (raise e))))))
                ;; Check migration files
                (for [file (os.listdir "migrations")]
                  (when (.endswith file ".hy")
                    (let [filepath (os.path.join "migrations" file)]
                      (try
                        (with [f (open filepath "r")]
                          (import hy)
                          (hy.read-many (.read f)))
                        (print (.format "  ✓ {}" filepath))
                        (except [e Exception]
                          (print (.format "  ✗ {}: {}" filepath e))
                          (raise e))))))
                (print "All Hy files passed syntax check"))]
   "verbosity" 2
   "doc" "Check Hy syntax in all package and migration files"})

(defn task-test []
  "Run tests"
  {"actions" [(fn []
                (print "Running tests...")
                ;; Test migration system
                (try
                  (run-command "hy test_migrations.hy")
                  (print "✓ Migration tests passed")
                  (except [e Exception]
                    (print (.format "✗ Migration tests failed: {}" e))))
                
                ;; Test CLI
                (try
                  (run-command "hylang-migrate --help")
                  (print "✓ CLI test passed")
                  (except [e Exception]
                    (print (.format "✗ CLI test failed: {}" e)))))]
   "task_dep" ["lint"]
   "verbosity" 2
   "doc" "Run all test files"})

(defn task-build []
  "Build distribution packages"
  {"actions" [
     (fn [] (print "Building distribution packages..."))
     "python3 -m pip install --upgrade build"
     "python3 -m build"
     (fn [] (print "Build complete - check dist/ directory"))]
   "task_dep" ["clean" "lint"]
   "targets" ["dist/*.whl" "dist/*.tar.gz"]
   "verbosity" 2
   "doc" "Build wheel and source distribution"})

(defn task-install []
  "Install package in development mode"
  {"actions" [
     "python3 -m pip install -e ."
     (fn [] (print "Package installed in development mode"))]
   "verbosity" 2
   "doc" "Install the package in editable/development mode"})

(defn task-install-prod []
  "Install package from built distribution"
  {"actions" [
     (fn []
       (if (os.path.exists "dist")
         (do
           (run-command "python3 -m pip uninstall -y hylang-migrations")
           (run-command "python3 -m pip install dist/*.whl")
           (print "Package installed from distribution"))
         (print "No dist/ directory found. Run 'doit build' first")))]
   "task_dep" ["build"]
   "verbosity" 2
   "doc" "Install the package from the built wheel"})

(defn task-demo []
  "Run demonstration of migration system"
  {"actions" [
     (fn [] (print "\n" "=" 70))
     (fn [] (print "Running Hylang Migrations Demo..."))
     (fn [] (print "=" 70 "\n"))
     "cd demo && hy run_demo.hy"
     (fn [] (print "\n" "=" 70))
     (fn [] (print "Demo complete! Check demo/demo.db for results"))
     (fn [] (print "=" 70))]
   "verbosity" 2
   "doc" "Run the complete migration system demonstration"})

(defn task-check-deps []
  "Check and install dependencies"
  {"actions" [
     "python3 -m pip install --upgrade pip"
     "python3 -m pip install hy>=1.0.0"
     "python3 -m pip install sqlobject"
     "python3 -m pip install build twine"
     "python3 -m pip install doit"
     (fn [] (print "Dependencies checked and installed"))]
   "verbosity" 2
   "doc" "Ensure all required dependencies are installed"})

(defn task-docs []
  "Generate or update documentation"
  {"actions" [
     (fn []
       (print "Checking documentation files...")
       (if (os.path.exists "README.md")
         (print "✓ README.md found")
         (print "✗ README.md not found")))
     (fn []
       (if (os.path.exists "INSTALL.md")
         (print "✓ INSTALL.md found")
         (print "✗ INSTALL.md not found")))
     (fn []
       (if (os.path.exists "LICENSE")
         (print "✓ LICENSE found")
         (print "✗ LICENSE not found")))
     (fn []
       (if (os.path.exists ".claude/agents")
         (print "✓ Claude agents documentation found")
         (print "✗ Claude agents documentation not found")))]
   "verbosity" 2
   "doc" "Check documentation files"})

(defn task-version []
  "Show package version"
  {"actions" [
     (fn []
       (try
         (import tomllib)
         (with [f (open "pyproject.toml" "rb")]
           (let [config (tomllib.load f)]
             (print (.format "Package version: {}" (get-in config ["project" "version"])))))
         (except [ImportError]
           ;; Python < 3.11 doesn't have tomllib
           (try
             (import toml)
             (let [config (toml.load "pyproject.toml")]
               (print (.format "Package version: {}" (get-in config ["project" "version"]))))
             (except [ImportError]
               (print "Install toml: pip install toml")
               (print "Version is defined in pyproject.toml"))))))]
   "verbosity" 2
   "doc" "Display the current package version"})

(defn task-upload-test []
  "Upload package to TestPyPI"
  {"actions" [
     (fn [] (print "Uploading to TestPyPI..."))
     "python3 -m twine upload --repository testpypi dist/*"
     (fn [] (print "Upload to TestPyPI complete"))
     (fn [] (print "Install from TestPyPI with:"))
     (fn [] (print "  pip install -i https://test.pypi.org/simple/ hylang-migrations"))]
   "task_dep" ["build"]
   "verbosity" 2
   "doc" "Upload distribution to TestPyPI (test repository)"})

(defn task-upload []
  "Upload package to PyPI"
  {"actions" [
     (fn [] 
       (print "=" 70)
       (print "WARNING: This will upload to the real PyPI!")
       (print "Make sure you have:")
       (print "  1. Updated the version in pyproject.toml")
       (print "  2. Tested the package thoroughly") 
       (print "  3. Updated the README and documentation")
       (print "  4. Set up PyPI credentials (~/.pypirc or keyring)")
       (print "=" 70)
       (input "Press Enter to continue or Ctrl+C to cancel..."))
     "python3 -m twine upload dist/*"
     (fn [] (print "Upload to PyPI complete"))
     (fn [] (print "Install from PyPI with:"))
     (fn [] (print "  pip install hylang-migrations"))]
   "task_dep" ["build"]
   "verbosity" 2
   "doc" "Upload distribution to PyPI (PRODUCTION - use with caution)"})

(defn task-dev []
  "Set up development environment"
  {"actions" [
     (fn [] (print "Setting up development environment..."))
     "task_dep" ["check-deps" "install" "lint"]
     (fn [] (print "\nDevelopment environment ready!"))
     (fn [] (print "Run 'doit list' to see available tasks"))]
   "verbosity" 2
   "doc" "Complete development environment setup"})

(defn task-release []
  "Prepare a new release"
  {"actions" [
     (fn []
       (print "Release checklist:"))
     (fn [] (print "  [ ] Update version in pyproject.toml"))
     (fn [] (print "  [ ] Update CHANGELOG (if exists)"))
     (fn [] (print "  [ ] Run all tests (doit test)"))
     (fn [] (print "  [ ] Run demo (doit demo)"))
     (fn [] (print "  [ ] Update documentation"))
     (fn [] (print "  [ ] Commit all changes"))
     (fn [] (print "  [ ] Tag the release (git tag -a v0.1.0 -m 'Release v0.1.0')"))
     (fn [] (print "  [ ] Push tag (git push origin v0.1.0)"))
     (fn [] (print "\nWhen ready, run:"))
     (fn [] (print "  1. doit build        # Build distributions"))
     (fn [] (print "  2. doit upload-test  # Test on TestPyPI"))
     (fn [] (print "  3. doit upload       # Upload to PyPI"))]
   "verbosity" 2
   "doc" "Show release preparation checklist"})

(defn task-parenthesis []
  "Check parenthesis balance in Hy files"
  {"actions" [
     (fn [] (print "Checking parenthesis balance..."))
     "python3 tools/lisp_parenthesis_analyzer.py src/hylang_migrations/migrations.hy"
     "python3 tools/lisp_parenthesis_analyzer.py src/hylang_migrations/cli.hy"
     "python3 tools/lisp_parenthesis_analyzer.py src/hylang_migrations/config.hy"]
   "verbosity" 2
   "doc" "Run parenthesis analyzer on main source files"})

(defn task-status []
  "Show migration status for test database"
  {"actions" [
     "hylang-migrate status --db test.db"]
   "verbosity" 2
   "doc" "Display migration status for test database"})

(defn task-migrate []
  "Run migrations on test database"
  {"actions" [
     "hylang-migrate migrate --db test.db"]
   "verbosity" 2
   "doc" "Apply pending migrations to test database"})

(setv DOIT_CONFIG {"default_tasks" ["build"]})
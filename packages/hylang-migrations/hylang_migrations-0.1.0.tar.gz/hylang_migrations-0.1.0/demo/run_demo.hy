#!/usr/bin/env hy
;;; Complete demo of the Hylang migrations tool
;;; Shows initialization, migration, status, and data insertion

(import sys)
(import os)
(import sqlite3)
(import pathlib [Path])

;; Add parent directory to path to import the migrations module
(sys.path.insert 0 (str (/ (Path.cwd) ".." "src")))

;; Import the migration module directly, bypassing __init__.hy
(import importlib)
(setv migrations-module (importlib.import-module "hylang_migrations.migrations"))
(setv MigrationRunner migrations-module.MigrationRunner)

(print "\n" "=" 70)
(print "HYLANG MIGRATIONS DEMO")
(print "=" 70 "\n")

(setv db-path "demo.db")
(setv migrations-dir "migrations")

;; Clean up any existing demo database
(when (.exists (Path db-path))
  (os.remove db-path)
  (print "🗑️  Cleaned up existing demo database\n"))

;; Initialize the migration runner
(print "📦 Initializing migration system...")
(setv runner (MigrationRunner db-path migrations-dir))

;; Show initial status
(print "\n📊 Initial migration status:")
(runner.status)

;; Run all migrations
(print "\n🚀 Running migrations...")
(runner.run-migrations None)

;; Show status after migrations
(print "\n📊 Status after migrations:")
(runner.status)

;; Insert some demo data
(print "\n💾 Inserting demo data...")
(setv conn (sqlite3.connect db-path))
(setv cursor (.cursor conn))

;; Insert users
(.execute cursor "
  INSERT INTO users (username, email, password_hash) VALUES
  ('alice', 'alice@example.com', 'hashed_password_1'),
  ('bob', 'bob@example.com', 'hashed_password_2'),
  ('charlie', 'charlie@example.com', 'hashed_password_3')")

;; Insert user profiles
(.execute cursor "
  INSERT INTO user_profiles (user_id, full_name, bio, location) VALUES
  (1, 'Alice Johnson', 'Software engineer and Lisp enthusiast', 'San Francisco'),
  (2, 'Bob Smith', 'Database architect', 'New York'),
  (3, 'Charlie Brown', 'Full-stack developer', 'Austin')")

;; Insert posts
(.execute cursor "
  INSERT INTO posts (author_id, title, slug, content, status) VALUES
  (1, 'Getting Started with Hylang', 'getting-started-hylang', 
   'Hylang is a Lisp dialect that runs on Python...', 'published'),
  (1, 'Building a Migration System', 'building-migration-system',
   'Today we will build a database migration system...', 'published'),
  (2, 'Database Design Best Practices', 'database-design-best-practices',
   'When designing databases, consider these principles...', 'draft')")

;; Insert comments
(.execute cursor "
  INSERT INTO comments (post_id, author_id, content) VALUES
  (1, 2, 'Great introduction to Hylang!'),
  (1, 3, 'Very helpful, thanks for sharing'),
  (2, 2, 'This migration system looks really useful')")

(.commit conn)
(print "✅ Demo data inserted successfully")

;; Query and display the data
(print "\n📈 Database contents:")
(print "\n👥 Users:")
(.execute cursor "SELECT username, email FROM users")
(for [row (cursor.fetchall)]
  (print (.format "  - {}: {}" (get row 0) (get row 1))))

(print "\n📝 Posts:")
(.execute cursor "
  SELECT p.title, u.username, p.status, 
         (SELECT COUNT(*) FROM comments WHERE post_id = p.id) as comment_count
  FROM posts p
  JOIN users u ON p.author_id = u.id")
(for [row (cursor.fetchall)]
  (print (.format "  - '{}' by {} [{}] - {} comments" 
                  (get row 0) (get row 1) (get row 2) (get row 3))))

(print "\n💬 Comments:")
(.execute cursor "
  SELECT c.content, u.username, p.title
  FROM comments c
  JOIN users u ON c.author_id = u.id
  JOIN posts p ON c.post_id = p.id")
(for [row (cursor.fetchall)]
  (print (.format "  - '{}' by {} on '{}'" 
                  (get row 0) (get row 1) (get row 2))))

;; Show schema info
(print "\n🗂️  Database schema:")
(.execute cursor "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
(setv tables (cursor.fetchall))
(for [table tables]
  (setv table-name (get table 0))
  (print (.format "\n  Table: {}" table-name))
  (.execute cursor (.format "PRAGMA table_info({})" table-name))
  (for [col (cursor.fetchall)]
    (print (.format "    - {} {} {}" 
                    (get col 1)  ; column name
                    (get col 2)  ; data type
                    (if (get col 3) "NOT NULL" "")))))

;; Show indexes
(print "\n🔍 Indexes:")
(.execute cursor "SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
(for [idx (cursor.fetchall)]
  (print (.format "  - {} on {}" (get idx 0) (get idx 1))))

;; Clean up
(.close conn)

(print "\n" "=" 70)
(print "✨ Demo completed successfully!")
(print (.format "📁 Database saved as: {}" db-path))
(print "=" 70 "\n")
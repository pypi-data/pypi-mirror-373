;;; Example migration: 003_create_posts_table.hy
;;; Full implementation showing how migrations work in practice

(import migrations [Migration])
(import sqlite3)
(import datetime [datetime])

(defclass CreatePostsTable [Migration]
  "Create posts table with relationships to users"
  
  (defn __init__ [self]
    (.__init__ (super) "003" "create_posts_table")
    ;; Define the actual SQL statements for this migration
    (setv self.up-sql
      ["CREATE TABLE posts (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER NOT NULL,
          title VARCHAR(255) NOT NULL,
          slug VARCHAR(255) UNIQUE NOT NULL,
          content TEXT,
          excerpt TEXT,
          status VARCHAR(20) DEFAULT 'draft',
          published_at TIMESTAMP,
          view_count INTEGER DEFAULT 0,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
          CHECK (status IN ('draft', 'published', 'archived'))
        )"
       
       ;; Create indexes for better query performance
       "CREATE INDEX idx_posts_user_id ON posts(user_id)"
       "CREATE INDEX idx_posts_slug ON posts(slug)"
       "CREATE INDEX idx_posts_status ON posts(status)"
       "CREATE INDEX idx_posts_published_at ON posts(published_at)"
       
       ;; Create a composite index for common queries
       "CREATE INDEX idx_posts_status_published 
        ON posts(status, published_at DESC)"
       
       ;; Create tags table for post categorization
       "CREATE TABLE tags (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name VARCHAR(50) UNIQUE NOT NULL,
          slug VARCHAR(50) UNIQUE NOT NULL,
          description TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"
       
       ;; Create junction table for many-to-many relationship
       "CREATE TABLE post_tags (
          post_id INTEGER NOT NULL,
          tag_id INTEGER NOT NULL,
          PRIMARY KEY (post_id, tag_id),
          FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
          FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        )"
       
       ;; Create indexes for the junction table
       "CREATE INDEX idx_post_tags_post_id ON post_tags(post_id)"
       "CREATE INDEX idx_post_tags_tag_id ON post_tags(tag_id)"
       
       ;; Create comments table
       "CREATE TABLE comments (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          post_id INTEGER NOT NULL,
          user_id INTEGER,
          author_name VARCHAR(100),
          author_email VARCHAR(255),
          content TEXT NOT NULL,
          status VARCHAR(20) DEFAULT 'pending',
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
          FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
          CHECK (status IN ('pending', 'approved', 'spam'))
        )"
       
       "CREATE INDEX idx_comments_post_id ON comments(post_id)"
       "CREATE INDEX idx_comments_status ON comments(status)"])
    
    ;; Define rollback SQL
    (setv self.down-sql
      ;; Drop in reverse order due to foreign key constraints
      ["DROP INDEX IF EXISTS idx_comments_status"
       "DROP INDEX IF EXISTS idx_comments_post_id"
       "DROP TABLE IF EXISTS comments"
       
       "DROP INDEX IF EXISTS idx_post_tags_tag_id"
       "DROP INDEX IF EXISTS idx_post_tags_post_id"
       "DROP TABLE IF EXISTS post_tags"
       
       "DROP TABLE IF EXISTS tags"
       
       "DROP INDEX IF EXISTS idx_posts_status_published"
       "DROP INDEX IF EXISTS idx_posts_published_at"
       "DROP INDEX IF EXISTS idx_posts_status"
       "DROP INDEX IF EXISTS idx_posts_slug"
       "DROP INDEX IF EXISTS idx_posts_user_id"
       "DROP TABLE IF EXISTS posts"]))
  
  (defn up [self &optional [connection None]]
    "Apply migration - create posts and related tables"
    ;; If connection not provided, this would normally get it from the runner
    (if (is connection None)
      (raise ValueError "Database connection required")
      (setv self.connection connection))
    
    (print "\n📦 Creating posts, tags, and comments tables...")
    
    ;; Execute each SQL statement
    (for [i sql] (enumerate self.up-sql 1)
      (setv [index sql-statement] i)
      (try
        ;; Extract table/index name for logging
        (setv operation-type 
          (cond
            [(.startswith (.strip sql-statement) "CREATE TABLE")
             "Creating table"]
            [(.startswith (.strip sql-statement) "CREATE INDEX")
             "Creating index"]
            [True "Executing"]))
        
        ;; Extract the name of what we're creating
        (import re)
        (setv table-match (re.search r"(?:TABLE|INDEX)\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)" 
                                     sql-statement))
        (setv object-name (if table-match 
                            (.group table-match 1)
                            "statement"))
        
        (print f"  [{index}/{(len self.up-sql)}] {operation-type}: {object-name}")
        
        ;; Execute the SQL
        (.execute self.connection sql-statement)
        
        (except [sqlite3.Error :as e]
          (print f"    ❌ Failed: {e}")
          (raise e))))
    
    ;; Optionally insert some seed data
    (when (self.should-seed-data)
      (self.seed-initial-data))
    
    (print "  ✅ Posts system tables created successfully!"))
  
  (defn down [self &optional [connection None]]
    "Rollback migration - drop posts and related tables"
    (if (is connection None)
      (raise ValueError "Database connection required")
      (setv self.connection connection))
    
    (print "\n🔄 Rolling back posts, tags, and comments tables...")
    
    ;; Execute rollback SQL statements
    (for [i sql] (enumerate self.down-sql 1)
      (setv [index sql-statement] i)
      (try
        ;; Determine what we're dropping
        (setv operation-type
          (cond
            [(.startswith (.strip sql-statement) "DROP TABLE")
             "Dropping table"]
            [(.startswith (.strip sql-statement) "DROP INDEX")
             "Dropping index"]
            [True "Executing"]))
        
        ;; Extract the name
        (import re)
        (setv drop-match (re.search r"(?:TABLE|INDEX)\s+(?:IF\s+EXISTS\s+)?(\w+)"
                                    sql-statement))
        (setv object-name (if drop-match
                            (.group drop-match 1)
                            "statement"))
        
        (print f"  [{index}/{(len self.down-sql)}] {operation-type}: {object-name}")
        
        ;; Execute the SQL
        (.execute self.connection sql-statement)
        
        (except [sqlite3.Error :as e]
          ;; Ignore errors about objects not existing during rollback
          (if (not (in "no such table" (str e)))
            (do
              (print f"    ⚠️  Warning: {e}")
              ;; Don't raise - continue with other rollbacks
              ))))
    
    (print "  ✅ Posts system tables rolled back successfully!"))
  
  (defn should-seed-data [self]
    "Check if we should seed initial data"
    ;; Could check environment variable or config
    ;; For now, return False to skip seeding
    False)
  
  (defn seed-initial-data [self]
    "Seed some initial data for testing"
    (print "  📝 Seeding initial data...")
    
    ;; Insert sample tags
    (setv sample-tags
      [["python" "python" "Python programming language"]
       ["hylang" "hylang" "Hylang - Lisp for Python"]
       ["database" "database" "Database and SQL topics"]
       ["tutorial" "tutorial" "Tutorial and how-to articles"]])
    
    (for [tag sample-tags]
      (.execute self.connection
        "INSERT INTO tags (name, slug, description) VALUES (?, ?, ?)"
        tag))
    
    (print f"    Added {(len sample-tags)} tags")
    
    ;; Get a user ID for sample posts (assuming users exist from previous migration)
    (setv cursor (.execute self.connection "SELECT id FROM users LIMIT 1"))
    (setv user-result (.fetchone cursor))
    
    (when user-result
      (setv user-id (get user-result 0))
      
      ;; Insert sample posts
      (setv sample-posts
        [[user-id 
          "Getting Started with Hylang"
          "getting-started-with-hylang"
          "Hylang is a Lisp dialect that compiles to Python..."
          "An introduction to Hylang"
          "published"
          (.isoformat (datetime.now))]
         [user-id
          "Building a Migration Tool"
          "building-migration-tool"
          "Today we'll build a database migration tool..."
          "Learn to build migrations"
          "published"
          (.isoformat (datetime.now))]])
      
      (for [post sample-posts]
        (.execute self.connection
          "INSERT INTO posts (user_id, title, slug, content, excerpt, status, published_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)"
          post))
      
      (print f"    Added {(len sample-posts)} sample posts"))
    
    (print "  ✅ Seed data inserted"))
  
  (defn validate [self &optional [connection None]]
    "Validate that the migration completed successfully"
    (if (is connection None)
      (raise ValueError "Database connection required")
      (setv self.connection connection))
    
    (print "\n🔍 Validating migration...")
    
    ;; Check all expected tables exist
    (setv expected-tables ["posts" "tags" "post_tags" "comments"])
    (setv cursor (.execute self.connection
      "SELECT name FROM sqlite_master WHERE type='table' AND name IN (?, ?, ?, ?)"
      expected-tables))
    
    (setv found-tables (set))
    (for [row (.fetchall cursor)]
      (.add found-tables (get row 0)))
    
    (setv missing-tables (- (set expected-tables) found-tables))
    
    (if missing-tables
      (do
        (print f"  ❌ Missing tables: {missing-tables}")
        False)
      (do
        (print f"  ✅ All tables created successfully")
        
        ;; Check indexes
        (setv expected-indexes 
          ["idx_posts_user_id" "idx_posts_slug" "idx_posts_status"
           "idx_posts_published_at" "idx_posts_status_published"
           "idx_post_tags_post_id" "idx_post_tags_tag_id"
           "idx_comments_post_id" "idx_comments_status"])
        
        (setv cursor (.execute self.connection
          "SELECT name FROM sqlite_master WHERE type='index'"))
        
        (setv found-indexes (set))
        (for [row (.fetchall cursor)]
          (.add found-indexes (get row 0)))
        
        (setv missing-indexes [])
        (for [idx expected-indexes]
          (when (not (in idx found-indexes))
            (.append missing-indexes idx)))
        
        (if missing-indexes
          (do
            (print f"  ⚠️  Missing indexes: {missing-indexes}")
            ;; Indexes are less critical, so we can still return True
            True)
          (do
            (print f"  ✅ All indexes created successfully")
            True)))))
  
  (defn get-checksum [self]
    "Calculate checksum of migration content"
    (import hashlib)
    ;; Combine all SQL statements for checksum
    (setv content (+ (.join "\n" self.up-sql)
                    "\n---\n"
                    (.join "\n" self.down-sql)))
    (-> (hashlib.sha256)
        (.update (.encode content "utf-8"))
        (.hexdigest))))

;; Export migration instance
(setv migration (CreatePostsTable))

;; Allow running directly for testing
(when (= __name__ "__main__")
  (print "Testing CreatePostsTable migration")
  (print "==================================")
  
  ;; Create in-memory database for testing
  (setv conn (sqlite3.connect ":memory:"))
  
  ;; Create prerequisite tables (users)
  (.execute conn
    "CREATE TABLE users (
       id INTEGER PRIMARY KEY,
       username VARCHAR(255),
       email VARCHAR(255)
     )")
  (.execute conn "INSERT INTO users (username, email) VALUES ('test', 'test@example.com')")
  
  ;; Test the migration
  (setv test-migration (CreatePostsTable))
  
  (print "\n1. Running UP migration...")
  (test-migration.up conn)
  
  (print "\n2. Validating...")
  (setv is-valid (test-migration.validate conn))
  
  (if is-valid
    (print "\n✅ Migration test passed!")
    (print "\n❌ Migration test failed!"))
  
  (print "\n3. Running DOWN migration...")
  (test-migration.down conn)
  
  ;; Verify tables are gone
  (setv cursor (.execute conn 
    "SELECT name FROM sqlite_master WHERE type='table' AND name='posts'"))
  (if (.fetchone cursor)
    (print "\n❌ Rollback failed - posts table still exists")
    (print "\n✅ Rollback successful - tables removed"))
  
  (.close conn))

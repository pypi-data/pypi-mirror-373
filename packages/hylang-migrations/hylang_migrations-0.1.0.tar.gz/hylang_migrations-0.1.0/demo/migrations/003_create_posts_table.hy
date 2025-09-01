;;; Third migration - Create posts table
;;; Demonstrates many-to-one relationships and triggers

(defclass Migration003 []
  "Create posts table with author relationship"
  
  (defn __init__ [self]
    (setv self.version "003")
    (setv self.name "create_posts_table")
    (setv self.connection None))
  
  (defn set-connection [self conn]
    "Set database connection"
    (setv self.connection conn))
  
  (defn up [self]
    "Create posts table with author relationship"
    (when self.connection
      (setv cursor (.cursor self.connection))
      
      ;; Create posts table
      (.execute cursor "
        CREATE TABLE IF NOT EXISTS posts (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          author_id INTEGER NOT NULL,
          title VARCHAR(500) NOT NULL,
          slug VARCHAR(500) UNIQUE NOT NULL,
          content TEXT,
          status VARCHAR(50) DEFAULT 'draft',
          published_at TIMESTAMP,
          view_count INTEGER DEFAULT 0,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
        )")
      
      ;; Create indexes for common queries
      (.execute cursor "CREATE INDEX IF NOT EXISTS idx_posts_author ON posts(author_id)")
      (.execute cursor "CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status)")
      (.execute cursor "CREATE INDEX IF NOT EXISTS idx_posts_published ON posts(published_at)")
      (.execute cursor "CREATE INDEX IF NOT EXISTS idx_posts_slug ON posts(slug)")
      
      ;; Create trigger to update updated_at timestamp
      (.execute cursor "
        CREATE TRIGGER IF NOT EXISTS update_posts_timestamp 
        AFTER UPDATE ON posts
        BEGIN
          UPDATE posts SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END")
      
      (print "  ✓ Created posts table with indexes and triggers")))
  
  (defn down [self]
    "Drop posts table and related objects"
    (when self.connection
      (setv cursor (.cursor self.connection))
      
      ;; Drop trigger
      (.execute cursor "DROP TRIGGER IF EXISTS update_posts_timestamp")
      
      ;; Drop indexes
      (.execute cursor "DROP INDEX IF EXISTS idx_posts_slug")
      (.execute cursor "DROP INDEX IF EXISTS idx_posts_published")
      (.execute cursor "DROP INDEX IF EXISTS idx_posts_status")
      (.execute cursor "DROP INDEX IF EXISTS idx_posts_author")
      
      ;; Drop table
      (.execute cursor "DROP TABLE IF EXISTS posts")
      
      (print "  ✓ Dropped posts table and related objects")))
  
  (defn get-checksum [self]
    "Return a checksum of the migration"
    "003-posts-v1"))

;; Create migration instance
(setv migration (Migration003))
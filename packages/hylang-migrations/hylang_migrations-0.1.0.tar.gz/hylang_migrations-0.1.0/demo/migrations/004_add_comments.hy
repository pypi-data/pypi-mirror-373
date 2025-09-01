;;; Fourth migration - Add comments system
;;; Demonstrates self-referential relationships (nested comments)

(defclass Migration004 []
  "Add comments table for posts"
  
  (defn __init__ [self]
    (setv self.version "004")
    (setv self.name "add_comments")
    (setv self.connection None))
  
  (defn set-connection [self conn]
    "Set database connection"
    (setv self.connection conn))
  
  (defn up [self]
    "Create comments table with nested comment support"
    (when self.connection
      (setv cursor (.cursor self.connection))
      
      ;; Create comments table
      (.execute cursor "
        CREATE TABLE IF NOT EXISTS comments (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          post_id INTEGER NOT NULL,
          author_id INTEGER NOT NULL,
          parent_id INTEGER,
          content TEXT NOT NULL,
          is_edited BOOLEAN DEFAULT 0,
          is_deleted BOOLEAN DEFAULT 0,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
          FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
          FOREIGN KEY (parent_id) REFERENCES comments(id) ON DELETE CASCADE
        )")
      
      ;; Create indexes
      (.execute cursor "CREATE INDEX IF NOT EXISTS idx_comments_post ON comments(post_id)")
      (.execute cursor "CREATE INDEX IF NOT EXISTS idx_comments_author ON comments(author_id)")
      (.execute cursor "CREATE INDEX IF NOT EXISTS idx_comments_parent ON comments(parent_id)")
      
      ;; Add comment count to posts
      (.execute cursor "ALTER TABLE posts ADD COLUMN comment_count INTEGER DEFAULT 0")
      
      ;; Create trigger to update comment count
      (.execute cursor "
        CREATE TRIGGER IF NOT EXISTS increment_comment_count
        AFTER INSERT ON comments
        WHEN NEW.is_deleted = 0
        BEGIN
          UPDATE posts SET comment_count = comment_count + 1 WHERE id = NEW.post_id;
        END")
      
      (.execute cursor "
        CREATE TRIGGER IF NOT EXISTS decrement_comment_count
        AFTER UPDATE ON comments
        WHEN OLD.is_deleted = 0 AND NEW.is_deleted = 1
        BEGIN
          UPDATE posts SET comment_count = comment_count - 1 WHERE id = NEW.post_id;
        END")
      
      (print "  ✓ Created comments table with triggers")))
  
  (defn down [self]
    "Drop comments table and triggers"
    (when self.connection
      (setv cursor (.cursor self.connection))
      
      ;; Drop triggers
      (.execute cursor "DROP TRIGGER IF EXISTS increment_comment_count")
      (.execute cursor "DROP TRIGGER IF EXISTS decrement_comment_count")
      
      ;; Drop indexes
      (.execute cursor "DROP INDEX IF EXISTS idx_comments_parent")
      (.execute cursor "DROP INDEX IF EXISTS idx_comments_author")
      (.execute cursor "DROP INDEX IF EXISTS idx_comments_post")
      
      ;; Drop table
      (.execute cursor "DROP TABLE IF EXISTS comments")
      
      (print "  ✓ Dropped comments table and triggers")))
  
  (defn get-checksum [self]
    "Return a checksum of the migration"
    "004-comments-v1"))

;; Create migration instance
(setv migration (Migration004))
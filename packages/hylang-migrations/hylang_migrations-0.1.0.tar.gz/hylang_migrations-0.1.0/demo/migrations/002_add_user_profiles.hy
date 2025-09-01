;;; Second migration - Add user profiles
;;; Demonstrates foreign key relationships

(defclass Migration002 []
  "Add user profiles table"
  
  (defn __init__ [self]
    (setv self.version "002")
    (setv self.name "add_user_profiles")
    (setv self.connection None))
  
  (defn set-connection [self conn]
    "Set database connection"
    (setv self.connection conn))
  
  (defn up [self]
    "Create user_profiles table linked to users"
    (when self.connection
      (setv cursor (.cursor self.connection))
      
      ;; Create user_profiles table
      (.execute cursor "
        CREATE TABLE IF NOT EXISTS user_profiles (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER UNIQUE NOT NULL,
          full_name VARCHAR(255),
          bio TEXT,
          avatar_url VARCHAR(500),
          location VARCHAR(255),
          website VARCHAR(500),
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )")
      
      ;; Add profile_completed column to users table
      (.execute cursor "ALTER TABLE users ADD COLUMN profile_completed BOOLEAN DEFAULT 0")
      
      ;; Create index on foreign key
      (.execute cursor "CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON user_profiles(user_id)")
      
      (print "  ✓ Created user_profiles table and updated users table")))
  
  (defn down [self]
    "Drop user_profiles table and remove column from users"
    (when self.connection
      (setv cursor (.cursor self.connection))
      
      ;; SQLite doesn't support dropping columns easily, so we need to recreate the table
      (.execute cursor "DROP INDEX IF EXISTS idx_profiles_user_id")
      (.execute cursor "DROP TABLE IF EXISTS user_profiles")
      
      ;; Note: In production, you'd want to preserve data when dropping columns
      (print "  ✓ Dropped user_profiles table")))
  
  (defn get-checksum [self]
    "Return a checksum of the migration"
    "002-profiles-v1"))

;; Create migration instance  
(setv migration (Migration002))
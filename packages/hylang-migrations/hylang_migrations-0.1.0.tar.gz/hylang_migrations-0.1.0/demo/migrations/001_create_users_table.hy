;;; First migration - Create users table
;;; Demonstrates basic table creation with indexes

(defclass Migration001 []
  "Create initial users table"
  
  (defn __init__ [self]
    (setv self.version "001")
    (setv self.name "create_users_table")
    (setv self.connection None))
  
  (defn set-connection [self conn]
    "Set database connection"
    (setv self.connection conn))
  
  (defn up [self]
    "Create users table with indexes"
    (when self.connection
      (setv cursor (.cursor self.connection))
      
      ;; Create users table
      (.execute cursor "
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          username VARCHAR(255) UNIQUE NOT NULL,
          email VARCHAR(255) UNIQUE NOT NULL,
          password_hash VARCHAR(255) NOT NULL,
          is_active BOOLEAN DEFAULT 1,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )")
      
      ;; Create indexes for performance
      (.execute cursor "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
      (.execute cursor "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
      (.execute cursor "CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active)")
      
      (print "  ✓ Created users table with indexes")))
  
  (defn down [self]
    "Drop users table and indexes"
    (when self.connection
      (setv cursor (.cursor self.connection))
      (.execute cursor "DROP INDEX IF EXISTS idx_users_active")
      (.execute cursor "DROP INDEX IF EXISTS idx_users_username")
      (.execute cursor "DROP INDEX IF EXISTS idx_users_email")
      (.execute cursor "DROP TABLE IF EXISTS users")
      (print "  ✓ Dropped users table")))
  
  (defn get-checksum [self]
    "Return a checksum of the migration"
    "001-users-v1"))

;; Create migration instance
(setv migration (Migration001))
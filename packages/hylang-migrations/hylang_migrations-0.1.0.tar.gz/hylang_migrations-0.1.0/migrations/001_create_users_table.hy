;;; Example migration file: 001_create_users_table.hy

(import migrations [Migration])
(import sqlobject [SQLObject StringCol IntCol DateTimeCol BoolCol])

(defclass CreateUsersTable [Migration]
  "Create initial users table"
  
  (defn __init__ [self]
    (.__init__ (super) "001" "create_users_table"))
  
  (defn up [self]
    "Create users table"
    ;; Using raw SQL for schema changes
    (setv self.up-sql
      ["CREATE TABLE users (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         username VARCHAR(255) UNIQUE NOT NULL,
         email VARCHAR(255) UNIQUE NOT NULL,
         password_hash VARCHAR(255) NOT NULL,
         is_active BOOLEAN DEFAULT 1,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
         updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
       )"
       
       "CREATE INDEX idx_users_email ON users(email)"
       "CREATE INDEX idx_users_username ON users(username)"])
    
    ;; Execute SQL statements
    (for [sql self.up-sql]
      ;; Stub - execute via connection
      (print (.format "Executing: {}..." (get (.split sql "\n") 0)))))
  
  (defn down [self]
    "Drop users table"
    (setv self.down-sql
      ["DROP INDEX IF EXISTS idx_users_username"
       "DROP INDEX IF EXISTS idx_users_email" 
       "DROP TABLE IF EXISTS users"])
    
    ;; Execute rollback SQL
    (for [sql self.down-sql]
      ;; Stub - execute via connection
      (print (.format "Executing: {}" sql)))))

;; Export migration instance
(setv migration (CreateUsersTable))

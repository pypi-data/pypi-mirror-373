;;; Example migration file: 002_add_user_profile.hy

(import migrations [Migration])

(defclass AddUserProfile [Migration]
  "Add user profile table and link to users"
  
  (defn __init__ [self]
    (.__init__ (super) "002" "add_user_profile"))
  
  (defn up [self]
    "Create user_profiles table"
    (setv self.up-sql
      ["CREATE TABLE user_profiles (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         user_id INTEGER UNIQUE NOT NULL,
         full_name VARCHAR(255),
         bio TEXT,
         avatar_url VARCHAR(500),
         date_of_birth DATE,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
         updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
         FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
       )"
       
       "CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id)"])
    
    ;; Execute migration
    (for [sql self.up-sql]
      ;; Stub - execute via connection
      (print f"Executing: {(.split sql \newline) [0]}...")))
  
  (defn down [self]
    "Drop user_profiles table"
    (setv self.down-sql
      ["DROP INDEX IF EXISTS idx_user_profiles_user_id"
       "DROP TABLE IF EXISTS user_profiles"])
    
    ;; Execute rollback
    (for [sql self.down-sql]
      ;; Stub - execute via connection
      (print f"Executing: {sql}"))))

;; Export migration instance
(setv migration (AddUserProfile))

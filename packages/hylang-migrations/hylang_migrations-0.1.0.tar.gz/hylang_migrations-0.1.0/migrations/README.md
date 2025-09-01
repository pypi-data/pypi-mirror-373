# Complete Migration Example: Posts System

This directory contains a fully implemented migration example showing how to create a blog posts system with tags and comments.

## Files Overview

### 1. Migration File: `003_create_posts_table.hy`

A complete migration implementation that creates:
- **posts** table - Main blog posts with title, content, status, etc.
- **tags** table - Categories for organizing posts
- **post_tags** table - Many-to-many relationship between posts and tags
- **comments** table - User comments on posts
- Multiple indexes for performance optimization
- Foreign key constraints for data integrity

Key features of this migration:
- Full `up()` method with SQL execution
- Complete `down()` method for rollback
- `validate()` method to verify migration success
- `seed_initial_data()` for optional test data
- Checksum calculation for integrity
- Detailed progress logging
- Transaction safety

### 2. SQLObject Models: `post_models.hy`

Corresponding SQLObject models that work with the migrated schema:
- **Post** class with publishing, archiving, and view tracking
- **Tag** class with slug generation and merging capability
- **Comment** class with moderation workflow
- Rich relationships between models
- Helper methods for common queries
- JSON serialization support

### 3. Migration Runner: `run_migration.hy`

A standalone script showing how to execute migrations:
- Database connection management
- Transaction handling
- Migration history tracking
- Dry-run mode for previewing changes
- Rollback support
- Status reporting
- Error handling and recovery

## Usage Examples

### Running the Migration

```bash
# Execute the migration
hy run_migration.hy

# Preview changes without executing (dry run)
hy run_migration.hy --dry-run

# Check migration status
hy run_migration.hy --status

# Rollback the migration
hy run_migration.hy --rollback
```

### Using the Models

```hylang
;; Import the models
(import post_models [Post Tag Comment])
(import models [User])

;; Create a blog post
(setv user (first (User.select)))
(setv post (Post :user user
                 :title "Introduction to Hylang"
                 :slug "intro-to-hylang"
                 :content "Hylang is a Lisp dialect..."
                 :status "draft"))

;; Add tags
(post.add-tags ["hylang" "lisp" "tutorial"])

;; Publish the post
(post.publish)

;; Add a comment
(setv comment (Comment :post post
                      :content "Great article!"
                      :author-name "Reader"))
(comment.approve)

;; Query published posts
(setv published-posts (Post.get-published :limit 10))

;; Get posts by tag
(setv hylang-posts (get-posts-by-tag "hylang"))

;; Search posts
(setv results (Post.search "lisp"))
```

## Migration SQL Structure

The migration creates this schema:

```sql
-- Posts table
CREATE TABLE posts (
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
);

-- Tags table
CREATE TABLE tags (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name VARCHAR(50) UNIQUE NOT NULL,
  slug VARCHAR(50) UNIQUE NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Junction table for many-to-many
CREATE TABLE post_tags (
  post_id INTEGER NOT NULL,
  tag_id INTEGER NOT NULL,
  PRIMARY KEY (post_id, tag_id),
  FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
  FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Comments table
CREATE TABLE comments (
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
);
```

## Testing the Migration

You can test the migration in isolation:

```bash
# Run the migration file directly (uses in-memory database)
hy migrations/003_create_posts_table.hy
```

This will:
1. Create an in-memory SQLite database
2. Set up prerequisite tables
3. Run the UP migration
4. Validate the results
5. Run the DOWN migration
6. Verify cleanup

## Key Implementation Details

### Transaction Safety
All migrations run within transactions. If any step fails, the entire migration is rolled back.

### Progress Tracking
The migration provides detailed progress output:
```
📦 Creating posts, tags, and comments tables...
  [1/13] Creating table: posts
  [2/13] Creating index: idx_posts_user_id
  [3/13] Creating index: idx_posts_slug
  ...
  ✅ Posts system tables created successfully!
```

### Validation
After execution, the migration validates:
- All expected tables exist
- All indexes are created
- Foreign keys are properly set up

### Checksum Verification
Each migration generates a SHA256 checksum of its SQL content, stored in the migration history for integrity verification.

### Error Handling
Comprehensive error handling includes:
- Detailed error messages
- Automatic rollback on failure
- Recording of failed migrations in history
- Safe handling of missing prerequisites

## Integration with Main System

This migration integrates with the main migration system:

1. Place in `migrations/` directory
2. Run via CLI: `hy cli.hy migrate`
3. Check status: `hy cli.hy status`
4. Models automatically work with migrated schema

## Best Practices Demonstrated

1. **Idempotency**: Migration can be run multiple times safely
2. **Reversibility**: Complete rollback implementation
3. **Validation**: Built-in verification of results
4. **Documentation**: Clear comments and descriptions
5. **Error Recovery**: Graceful handling of failures
6. **Performance**: Appropriate indexes for common queries
7. **Data Integrity**: Foreign keys and check constraints
8. **Modularity**: Separate models from migrations

## Extending This Example

To add more features:

1. **Add columns**: Create new migration (004_add_post_metadata.hy)
2. **Add tables**: Follow the same pattern with up/down methods
3. **Add indexes**: Include in up_sql with corresponding drops
4. **Data migrations**: Add data transformation logic after schema changes
5. **Complex changes**: Break into multiple smaller migrations

This example provides a complete template for building production-ready database migrations in Hylang with SQLite and SQLObject.

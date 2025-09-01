#!/usr/bin/env hy
;;; __main__.hy - Entry point for running as module
;;; Allows running with: python -m hylang_migrations

(import .cli [main])

(when (= __name__ "__main__")
  (main))

#!/usr/bin/env python3
"""
Advanced Parenthesis Analyzer for Lisp-like Languages
Provides deep scope tracking and intelligent fix suggestions
"""

import re
import json
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

class ScopeType(Enum):
    """Types of scopes in Lisp-like languages"""
    DEFCLASS = "defclass"
    DEFN = "defn"
    DEFMACRO = "defmacro"
    LET = "let"
    SETV = "setv"
    IF = "if"
    WHEN = "when"
    UNLESS = "unless"
    COND = "cond"
    TRY = "try"
    EXCEPT = "except"
    FINALLY = "finally"
    WITH = "with"
    DO = "do"
    IMPORT = "import"
    CALL = "call"
    METHOD = "method"
    LIST = "list"
    DICT = "dict"
    EXPR = "expr"
    FOR = "for"
    LFOR = "lfor"

@dataclass
class Scope:
    """Represents a scope in the code"""
    type: ScopeType
    name: str
    line: int
    column: int
    depth: int
    content_preview: str = ""
    
    def __str__(self):
        return f"{self.type.value} {self.name}" if self.name else self.type.value

@dataclass
class ParenthesisIssue:
    """Represents a parenthesis imbalance issue"""
    line: int
    column: int
    issue_type: str  # "unclosed", "extra", "mismatch"
    scope: Optional[Scope] = None
    suggestion: str = ""
    context: str = ""

@dataclass
class ScopeNode:
    """Node for building scope trees"""
    scope: Scope
    children: List['ScopeNode'] = field(default_factory=list)
    parent: Optional['ScopeNode'] = None

class LispParenthesisAnalyzer:
    """Advanced analyzer for Lisp parenthesis balance"""
    
    def __init__(self, dialect: str = "hy"):
        self.dialect = dialect
        self.stack: List[Scope] = []
        self.issues: List[ParenthesisIssue] = []
        self.scope_log: List[str] = []
        self.depth = 0
        self.lines: List[str] = []
        
        # Dialect-specific keywords
        self.keywords = self._get_dialect_keywords()
    
    def _get_dialect_keywords(self) -> Dict[str, ScopeType]:
        """Get keywords for the specific Lisp dialect"""
        if self.dialect == "hy":
            return {
                "defclass": ScopeType.DEFCLASS,
                "defn": ScopeType.DEFN,
                "defmacro": ScopeType.DEFMACRO,
                "setv": ScopeType.SETV,
                "let": ScopeType.LET,
                "if": ScopeType.IF,
                "when": ScopeType.WHEN,
                "unless": ScopeType.UNLESS,
                "cond": ScopeType.COND,
                "try": ScopeType.TRY,
                "except": ScopeType.EXCEPT,
                "finally": ScopeType.FINALLY,
                "with": ScopeType.WITH,
                "do": ScopeType.DO,
                "import": ScopeType.IMPORT,
                "for": ScopeType.FOR,
                "lfor": ScopeType.LFOR,
            }
        elif self.dialect == "clojure":
            return {
                "defn": ScopeType.DEFN,
                "def": ScopeType.SETV,
                "let": ScopeType.LET,
                "if": ScopeType.IF,
                "when": ScopeType.WHEN,
                "cond": ScopeType.COND,
                "try": ScopeType.TRY,
                "catch": ScopeType.EXCEPT,
                "finally": ScopeType.FINALLY,
                "do": ScopeType.DO,
                "for": ScopeType.FOR,
            }
        # Add other dialects as needed
        return {}
    
    def analyze_file(self, filepath: str) -> Dict[str, Any]:
        """Analyze a file and return structured results"""
        with open(filepath, 'r') as f:
            self.lines = f.readlines()
        
        # Reset state
        self.stack = []
        self.issues = []
        self.scope_log = []
        self.depth = 0
        
        # Analyze each line
        for line_num, line in enumerate(self.lines, 1):
            self._analyze_line(line, line_num)
        
        # Check for unclosed scopes
        for scope in self.stack:
            self.issues.append(ParenthesisIssue(
                line=scope.line,
                column=scope.column,
                issue_type="unclosed",
                scope=scope,
                suggestion=f"Add {')' * len(self.stack)} at end of file to close remaining scopes",
                context=self._get_context(scope.line)
            ))
        
        return self._generate_report()
    
    def _analyze_line(self, line: str, line_num: int):
        """Analyze a single line for parentheses"""
        in_string = False
        in_comment = False
        escape_next = False
        
        for col, char in enumerate(line):
            # Handle escape sequences
            if escape_next:
                escape_next = False
                continue
            
            if char == '\\' and in_string:
                escape_next = True
                continue
            
            # Handle strings
            if char == '"' and not in_comment:
                in_string = not in_string
                continue
            
            # Handle comments
            if char == ';' and not in_string:
                in_comment = True
                break  # Rest of line is comment
            
            # Skip if in string
            if in_string:
                continue
            
            # Handle opening parenthesis
            if char == '(':
                self._handle_open_paren(line, line_num, col)
            
            # Handle closing parenthesis
            elif char == ')':
                self._handle_close_paren(line_num, col)
            
            # Handle square brackets (for Hy/Clojure)
            elif char == '[':
                self._handle_open_bracket(line, line_num, col)
            elif char == ']':
                self._handle_close_bracket(line_num, col)
    
    def _handle_open_paren(self, line: str, line_num: int, col: int):
        """Handle an opening parenthesis"""
        self.depth += 1
        
        # Identify the scope type
        remaining = line[col+1:].lstrip()
        scope_type = ScopeType.EXPR
        name = ""
        
        # Check for known keywords
        for keyword, stype in self.keywords.items():
            if remaining.startswith(keyword):
                scope_type = stype
                # Try to extract name for certain constructs
                if stype in [ScopeType.DEFCLASS, ScopeType.DEFN, ScopeType.DEFMACRO]:
                    match = re.match(f'{keyword}\\s+(\\S+)', remaining)
                    if match:
                        name = match.group(1).strip('[]')
                elif stype == ScopeType.SETV:
                    match = re.match(r'setv\s+(\S+)', remaining)
                    if match:
                        name = match.group(1)
                break
        
        # Check for method calls
        if scope_type == ScopeType.EXPR and remaining.startswith('.'):
            match = re.match(r'\.(\S+)', remaining)
            if match:
                scope_type = ScopeType.METHOD
                name = match.group(1)
        
        # Create and push scope
        scope = Scope(
            type=scope_type,
            name=name,
            line=line_num,
            column=col,
            depth=self.depth,
            content_preview=remaining[:30] if remaining else ""
        )
        
        self.stack.append(scope)
        self.scope_log.append(f"Line {line_num:4}, Col {col:3}, Depth {self.depth:2}: OPEN  {scope}")
    
    def _handle_close_paren(self, line_num: int, col: int):
        """Handle a closing parenthesis"""
        if not self.stack:
            self.issues.append(ParenthesisIssue(
                line=line_num,
                column=col,
                issue_type="extra",
                suggestion="Remove this closing parenthesis or find its missing opening",
                context=self._get_context(line_num)
            ))
            return
        
        scope = self.stack.pop()
        self.depth -= 1
        self.scope_log.append(
            f"Line {line_num:4}, Col {col:3}, Depth {self.depth+1:2}: CLOSE {scope} (opened at line {scope.line})"
        )
    
    def _handle_open_bracket(self, line: str, line_num: int, col: int):
        """Handle opening square bracket (for vectors/bindings)"""
        # In Hy, square brackets are used for function arguments and let bindings
        pass  # Can be extended if needed
    
    def _handle_close_bracket(self, line_num: int, col: int):
        """Handle closing square bracket"""
        pass  # Can be extended if needed
    
    def _get_context(self, line_num: int, context_lines: int = 2) -> str:
        """Get context around a line"""
        start = max(0, line_num - context_lines - 1)
        end = min(len(self.lines), line_num + context_lines)
        
        context = []
        for i in range(start, end):
            prefix = ">>> " if i == line_num - 1 else "    "
            context.append(f"{i+1:4}: {prefix}{self.lines[i].rstrip()}")
        
        return "\n".join(context)
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate a structured report"""
        content = ''.join(self.lines)
        
        # Count parentheses outside of strings and comments
        clean_content = self._remove_strings_and_comments(content)
        open_count = clean_content.count('(')
        close_count = clean_content.count(')')
        
        return {
            "file_stats": {
                "total_lines": len(self.lines),
                "open_parens": open_count,
                "close_parens": close_count,
                "difference": open_count - close_count,
                "final_depth": len(self.stack)
            },
            "issues": [
                {
                    "line": issue.line,
                    "column": issue.column,
                    "type": issue.issue_type,
                    "scope": str(issue.scope) if issue.scope else None,
                    "suggestion": issue.suggestion,
                    "context": issue.context
                }
                for issue in self.issues
            ],
            "unclosed_scopes": [
                {
                    "type": scope.type.value,
                    "name": scope.name,
                    "line": scope.line,
                    "column": scope.column,
                    "depth": scope.depth,
                    "preview": scope.content_preview
                }
                for scope in self.stack
            ],
            "scope_summary": self._generate_scope_summary(),
            "scope_tree": self.generate_scope_tree(),
            "suggested_fixes": self._generate_fixes()
        }
    
    def _remove_strings_and_comments(self, content: str) -> str:
        """Remove strings and comments from content for accurate paren counting"""
        result = []
        in_string = False
        in_comment = False
        escape_next = False
        
        for char in content:
            if escape_next:
                escape_next = False
                result.append(' ')
                continue
            
            if char == '\\' and in_string:
                escape_next = True
                result.append(' ')
                continue
            
            if char == '"' and not in_comment:
                in_string = not in_string
                result.append(' ')
                continue
            
            if char == ';' and not in_string:
                in_comment = True
            
            if char == '\n':
                in_comment = False
            
            if in_string or in_comment:
                result.append(' ')
            else:
                result.append(char)
        
        return ''.join(result)
    
    def _generate_scope_summary(self) -> List[str]:
        """Generate a summary of important scopes"""
        summary = []
        important_types = [ScopeType.DEFCLASS, ScopeType.DEFN, ScopeType.DEFMACRO,
                          ScopeType.TRY, ScopeType.COND, ScopeType.IF, ScopeType.WHEN,
                          ScopeType.FOR, ScopeType.LFOR, ScopeType.LET]
        
        for log_entry in self.scope_log:
            if any(t.value in log_entry for t in important_types):
                summary.append(log_entry)
        
        return summary
    
    def generate_scope_tree(self) -> str:
        """Generate an ASCII tree visualization of the scope hierarchy"""
        tree_lines = []
        
        # Build tree from scope log
        for entry in self.scope_log:
            if "OPEN" in entry:
                match = re.search(r'Depth\s+(\d+)', entry)
                if match:
                    depth = int(match.group(1))
                    scope_info = entry.split("OPEN")[1].strip()
                    indent = "  " * (depth - 1)
                    if depth == 1:
                        tree_lines.append(f"├─ {scope_info}")
                    else:
                        tree_lines.append(f"{indent}├─ {scope_info}")
        
        return "\n".join(tree_lines) if tree_lines else "No scopes found"
    
    def _generate_fixes(self) -> List[Dict[str, Any]]:
        """Generate specific fix suggestions"""
        fixes = []
        
        # For each unclosed scope, suggest where to add closing parens
        for i, scope in enumerate(self.stack):
            # Find the likely end of this scope
            end_line = self._find_scope_end(scope)
            remaining = len(self.stack) - i
            fixes.append({
                "type": "add_closing_paren",
                "scope": str(scope),
                "line": end_line,
                "description": f"Add {')' * remaining} at line {end_line} to close {scope} and {remaining-1} parent scopes",
                "code": ")" * remaining,
                "priority": "high" if scope.type in [ScopeType.DEFN, ScopeType.DEFCLASS, ScopeType.TRY] else "medium"
            })
        
        # For extra closing parens, suggest removal
        for issue in self.issues:
            if issue.issue_type == "extra":
                fixes.append({
                    "type": "remove_paren",
                    "line": issue.line,
                    "column": issue.column,
                    "description": f"Remove extra ) at line {issue.line}, column {issue.column}",
                    "priority": "high"
                })
        
        return fixes
    
    def _find_scope_end(self, scope: Scope) -> int:
        """Try to find where a scope should end"""
        # Look for the next definition at the same or lower indentation
        # or the end of file
        start_line = scope.line - 1
        if start_line < len(self.lines):
            start_indent = len(self.lines[start_line]) - len(self.lines[start_line].lstrip())
            
            for i in range(scope.line, len(self.lines)):
                line = self.lines[i]
                if line.strip():  # Non-empty line
                    current_indent = len(line) - len(line.lstrip())
                    # If we find something at same or lower indent, previous line was likely the end
                    if current_indent <= start_indent and line.strip().startswith('('):
                        return i
        
        return len(self.lines)
    
    def generate_breadcrumb(self, scope: Scope) -> str:
        """Generate a breadcrumb trail to this scope"""
        trail = []
        for s in self.stack:
            if s.depth <= scope.depth:
                trail.append(f"{s.type.value}:{s.name or 'anonymous'}")
            if s == scope:
                break
        return " > ".join(trail)
    
    def get_enhanced_context(self, line_num: int, highlight_cols: List[int] = None) -> str:
        """Get context with character highlighting"""
        context_lines = 3
        start = max(0, line_num - context_lines - 1)
        end = min(len(self.lines), line_num + context_lines)
        
        result = []
        for i in range(start, end):
            line = self.lines[i].rstrip()
            line_no = f"{i+1:4}: "
            
            if i == line_num - 1:
                # Highlight the problem line
                if highlight_cols:
                    highlighted = list(line)
                    for col_idx in highlight_cols:
                        if col_idx < len(highlighted):
                            highlighted[col_idx] = f"[{highlighted[col_idx]}]"
                    line = ''.join(highlighted)
                result.append(f"{line_no}>>> {line}")
                
                # Add pointer line
                if highlight_cols and highlight_cols[0] < len(line):
                    pointer = " " * (len(line_no) + 4 + highlight_cols[0]) + "^"
                    result.append(pointer)
            else:
                result.append(f"{line_no}    {line}")
        
        return "\n".join(result)

def main():
    """CLI interface for the analyzer"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Analyze Lisp parenthesis balance with advanced scope tracking",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s myfile.hy                    # Analyze a Hylang file
  %(prog)s myfile.clj --dialect clojure # Analyze a Clojure file
  %(prog)s myfile.hy --json             # Output as JSON
  %(prog)s myfile.hy --verbose          # Show detailed scope log
        """
    )
    parser.add_argument("file", help="File to analyze")
    parser.add_argument("--dialect", default="hy", 
                       choices=["hy", "clojure", "scheme"],
                       help="Lisp dialect (default: hy)")
    parser.add_argument("--json", action="store_true", 
                       help="Output as JSON")
    parser.add_argument("--verbose", action="store_true",
                       help="Show detailed scope log")
    parser.add_argument("--fix", action="store_true", 
                       help="Apply suggested fixes (creates backup)")
    
    args = parser.parse_args()
    
    # Check if file exists
    import os
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found")
        sys.exit(1)
    
    analyzer = LispParenthesisAnalyzer(dialect=args.dialect)
    report = analyzer.analyze_file(args.file)
    
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        # Pretty print the report
        print(f"\n{'='*80}")
        print(f"PARENTHESIS ANALYSIS REPORT: {args.file}")
        print(f"Dialect: {args.dialect.upper()}")
        print(f"{'='*80}\n")
        
        stats = report["file_stats"]
        print(f"📊 FILE STATISTICS:")
        print(f"  Total lines: {stats['total_lines']}")
        print(f"  Open parens: {stats['open_parens']}")
        print(f"  Close parens: {stats['close_parens']}")
        print(f"  Difference: {stats['difference']}")
        print(f"  Unclosed scopes: {stats['final_depth']}")
        
        # Show balance status
        if stats["difference"] == 0 and not report["issues"]:
            print(f"\n✅ PARENTHESES ARE BALANCED!")
        else:
            print(f"\n❌ PARENTHESIS IMBALANCE DETECTED!")
        
        # Show scope tree
        if report["scope_tree"]:
            print(f"\n🌳 SCOPE TREE:")
            print(report["scope_tree"])
        
        # Show issues
        if report["issues"]:
            print(f"\n⚠️  ISSUES FOUND ({len(report['issues'])}):")
            for issue in report["issues"]:
                print(f"\n  Issue: {issue['type'].upper()}")
                print(f"  Location: Line {issue['line']}, Column {issue['column']}")
                if issue['scope']:
                    print(f"  Scope: {issue['scope']}")
                print(f"  Suggestion: {issue['suggestion']}")
                if not args.verbose:
                    # Show condensed context
                    context_lines = issue['context'].split('\n')
                    for line in context_lines:
                        if '>>>' in line:
                            print(f"  {line}")
        
        # Show unclosed scopes
        if report["unclosed_scopes"]:
            print(f"\n🔓 UNCLOSED SCOPES ({len(report['unclosed_scopes'])}):")
            for scope in report["unclosed_scopes"]:
                print(f"\n  Scope: {scope['type']} {scope['name'] or ''}")
                print(f"  Opened at: Line {scope['line']}, Column {scope['column']}")
                print(f"  Depth: {scope['depth']}")
                if scope['preview']:
                    print(f"  Preview: {scope['preview'][:50]}...")
        
        # Show suggested fixes
        if report["suggested_fixes"]:
            print(f"\n🔧 SUGGESTED FIXES ({len(report['suggested_fixes'])}):")
            high_priority = [f for f in report["suggested_fixes"] if f.get('priority') == 'high']
            other = [f for f in report["suggested_fixes"] if f.get('priority') != 'high']
            
            if high_priority:
                print("\n  HIGH PRIORITY:")
                for fix in high_priority:
                    print(f"    - {fix['description']}")
                    if fix['type'] == 'add_closing_paren':
                        print(f"      Code to add: {fix['code']}")
            
            if other and args.verbose:
                print("\n  OTHER:")
                for fix in other:
                    print(f"    - {fix['description']}")
        
        # Show detailed log if verbose
        if args.verbose and analyzer.scope_log:
            print(f"\n📜 DETAILED SCOPE LOG:")
            print("-" * 80)
            for entry in analyzer.scope_log[:50]:  # Limit to first 50 for readability
                print(entry)
            if len(analyzer.scope_log) > 50:
                print(f"... and {len(analyzer.scope_log) - 50} more entries")
        
        # Summary
        print(f"\n{'='*80}")
        print(f"SUMMARY:")
        if stats["difference"] == 0 and not report["issues"]:
            print("  ✅ No parenthesis issues found!")
        else:
            if stats["difference"] > 0:
                print(f"  Need {stats['difference']} more closing parenthesis(es)")
            elif stats["difference"] < 0:
                print(f"  Have {-stats['difference']} extra closing parenthesis(es)")
            
            if report["unclosed_scopes"]:
                print(f"  {len(report['unclosed_scopes'])} scope(s) remain unclosed")
        print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
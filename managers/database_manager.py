import os
import sqlite3
import re
from typing import List, Dict, Any


class DatabaseManager:
    def __init__(self, db_file="olist.sqlite"):
        self.db_file = db_file
        if not os.path.exists(db_file):
            raise FileNotFoundError(f"Database file not found: {db_file}")
        self.schema = self._get_schema()

    def _get_schema(self) -> str:
        """Extract database schema information"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        schema_parts = []
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [f"{col[1]} ({col[2]})" for col in cursor.fetchall()]
            schema_parts.append(f"Table {table}: {', '.join(columns)}")
        conn.close()
        return "\n".join(schema_parts)

    def get_schema(self) -> str:
        """Get database schema information"""
        return self.schema

    def execute_query(self, query: str) -> List[Dict]:
        """Execute SQL query and return results as list of dictionaries"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def get_table_info(self, table_name: str) -> List[Dict]:
        """Get detailed information about a specific table"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        conn.close()

        return [{
            'cid': col[0],
            'name': col[1],
            'type': col[2],
            'notnull': col[3],
            'dflt_value': col[4],
            'pk': col[5]
        } for col in columns]

    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            return True
        except Exception:
            return False

    def dry_run(self, query: str) -> Dict[str, Any]:
        """Execute a dry run of the query for analysis - safely handle complex queries"""
        dry_query = query.strip()

        # For complex queries, use EXPLAIN QUERY PLAN instead of executing with LIMIT
        # This validates syntax without modifying the query logic
        if self._is_complex_query(dry_query):
            try:
                # Use EXPLAIN QUERY PLAN to validate syntax and analyze query plan
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                cursor.execute(f"EXPLAIN QUERY PLAN {dry_query}")
                explain_results = cursor.fetchall()
                conn.close()

                # Parse EXPLAIN output for potential issues
                analysis = self._parse_explain_output(explain_results)

                return {
                    'success': True,
                    'row_count': 0,  # No actual rows returned
                    'analysis': analysis,
                    'query_used': dry_query,
                    'sample_results': [],
                    'validation_method': 'explain'
                }

            except Exception as e:
                return {
                    'success': False,
                    'error': f"Syntax validation failed: {str(e)}",
                    'query_used': dry_query
                }

        # For simple queries, we can safely add LIMIT and execute
        else:
            if not dry_query.upper().endswith("LIMIT") and "LIMIT" not in dry_query.upper():
                dry_query += " LIMIT 10"

            try:
                results = self.execute_query(dry_query)
                row_count = len(results)

                # Analyze results for potential issues
                analysis = []

                if row_count == 0:
                    analysis.append("Empty result set - possible issue with WHERE conditions or joins")
                elif row_count > 100:  # Unexpectedly high for LIMIT 10
                    analysis.append(f"High row count ({row_count}) - possible cartesian product or missing join conditions")

                # Check for data duplication patterns
                if row_count > 1:
                    # Simple heuristic: if many identical rows, possible duplication
                    first_row = str(results[0])
                    identical_count = sum(1 for row in results if str(row) == first_row)
                    if identical_count > row_count * 0.8:  # 80% identical rows
                        analysis.append("Potential data duplication detected")

                return {
                    'success': True,
                    'row_count': row_count,
                    'analysis': analysis,
                    'query_used': dry_query,
                    'sample_results': results[:3],  # Return first 3 rows for inspection
                    'validation_method': 'execute'
                }

            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'query_used': dry_query
                }

    def _is_complex_query(self, query: str) -> bool:
        """Determine if a query is too complex for safe LIMIT modification"""
        query_upper = query.upper()

        # Complex query indicators
        complex_patterns = [
            r'WITH\s+\w+\s+AS',      # CTEs (Common Table Expressions)
            r'UNION\s+ALL',          # UNION operations
            r'INTERSECT',            # INTERSECT operations
            r'EXCEPT',               # EXCEPT operations
            r'WINDOW\s+FUNCTION',    # Window functions
            r'OVER\s*\(',            # OVER clauses
            r'GROUP\s+BY.*HAVING',   # GROUP BY with HAVING
            r'SELECT.*FROM.*\(',      # Subqueries in FROM clause
            r'WITH\s+RECURSIVE'      # Recursive CTEs
        ]

        for pattern in complex_patterns:
            if re.search(pattern, query_upper, re.IGNORECASE):
                return True

        # Check for multiple SELECT statements (indicates complex structure)
        select_count = len(re.findall(r'\bSELECT\b', query_upper))
        if select_count > 1:
            return True

        return False

    def _parse_explain_output(self, explain_results: list) -> list:
        """Parse EXPLAIN QUERY PLAN output for potential issues"""
        analysis = []

        # Convert explain results to text for analysis
        explain_text = ' '.join(str(row[0]) for row in explain_results).upper()

        # Performance issues
        if 'SCAN TABLE' in explain_text and 'INDEX' not in explain_text:
            scan_count = explain_text.count('SCAN TABLE')
            if scan_count > 2:
                analysis.append(f"Multiple full table scans detected ({scan_count}) - consider adding indexes")
            else:
                analysis.append("Full table scan detected - potential performance issue")

        # Cartesian product risk
        if 'CARTESIAN' in explain_text or 'CROSS JOIN' in explain_text:
            analysis.append("Cartesian product detected in query plan")

        # Temporary objects (potential performance hit)
        if 'TEMP B-TREE' in explain_text or 'TEMPORARY' in explain_text:
            analysis.append("Temporary table used - complex aggregation may be slow")

        # Subquery/materialization issues
        if 'MATERIALIZE' in explain_text or 'SUBQUERY' in explain_text:
            analysis.append("Subquery materialization - consider optimizing joins")

        # Sort operations
        if 'SORT' in explain_text:
            sort_count = explain_text.count('SORT')
            if sort_count > 1:
                analysis.append(f"Multiple sort operations ({sort_count}) - may impact performance")

        # If no issues found, note that the plan looks good
        if not analysis:
            analysis.append("Query plan analyzed - no obvious performance issues detected")

        return analysis
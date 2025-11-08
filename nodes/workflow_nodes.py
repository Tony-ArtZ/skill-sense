import json
import re
from typing import Dict, List, Any
from managers.prompt_manager import PromptManager


class WorkflowNodes:
    def __init__(self, ontology_manager, database_manager, llm_manager, prompt_manager):
        self.ontology_manager = ontology_manager
        self.db_manager = database_manager
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.max_retries = 8

    def validate_joins(self, sql_query: str) -> List[str]:
        """Validate join directions against ontology cardinality"""
        validation_issues = []

        # Extract JOIN clauses from SQL
        join_pattern = r'(?:LEFT|RIGHT|INNER|FULL)?\s*JOIN\s+(\w+)\s+ON\s+([\w\.]+)\s*=\s*([\w\.]+)'
        joins = re.findall(join_pattern, sql_query, re.IGNORECASE)

        # Get ontology links with cardinality
        ontology_links = self.ontology_manager.get_links_definitions()

        for join_table, left_col, right_col in joins:
            # Extract table names from columns
            left_table = left_col.split('.')[0] if '.' in left_col else None
            right_table = right_col.split('.')[0] if '.' in right_col else None

            if not left_table or not right_table:
                continue

            # Find matching ontology link
            for link in ontology_links:
                if join_table in [link.get('from_object'), link.get('to_object')]:
                    cardinality = link.get('cardinality', 'unknown')

                    # Basic validation for many-to-one relationships
                    if cardinality == 'many_to_one':
                        # For many-to-one, the 'many' side should typically be the left table in the join
                        if (link.get('from_object') == join_table and
                            link.get('to_object') in [left_table, right_table]):
                            validation_issues.append(
                                f"Join direction for {link['join']} may be incorrect. "
                                f"Expected many-to-one relationship with {link['from_object']} as primary table."
                            )

        return validation_issues

    def validate_sql_structure(self, sql_query: str) -> List[str]:
        """Validate SQL structure for common issues"""
        issues = []

        # Check for basic SQL syntax patterns
        sql_upper = sql_query.upper()

        # 1. Check for SELECT without FROM (basic syntax)
        if "SELECT" in sql_upper and "FROM" not in sql_upper:
            issues.append("SELECT statement without FROM clause")

        # 2. Check for potential cartesian products (JOIN without ON)
        if "JOIN" in sql_upper and "ON" not in sql_upper:
            issues.append("JOIN detected without ON condition - possible cartesian product")

        # 3. Check for GROUP BY without aggregation
        if "GROUP BY" in sql_upper:
            has_aggregation = any(func in sql_upper for func in ["SUM(", "COUNT(", "AVG(", "MAX(", "MIN("])
            if not has_aggregation:
                issues.append("GROUP BY used without aggregation functions")

        # 4. Check for ORDER BY on non-selected columns
        order_by_match = re.search(r'ORDER BY\s+([\w\s,]+)', sql_upper)
        if order_by_match:
            order_columns = [col.strip() for col in order_by_match.group(1).split(',')]
            # Extract selected columns (simplified)
            select_match = re.search(r'SELECT\s+(.*?)\s+FROM', sql_upper, re.DOTALL)
            if select_match:
                select_columns = [col.strip().split(' ')[0] for col in select_match.group(1).split(',')]
                for order_col in order_columns:
                    if order_col not in select_columns and not any(order_col in col for col in select_columns):
                        issues.append(f"ORDER BY on column '{order_col}' not in SELECT list")

        # 5. Check for potentially dangerous wildcards
        if "SELECT *" in sql_upper and ("JOIN" in sql_upper or "WHERE" in sql_upper):
            issues.append("SELECT * used with JOINs or WHERE - consider explicit column selection")

        return issues

    def track_error_pattern(self, state: Dict[str, Any], error_message: str) -> Dict[str, Any]:
        """Track error patterns across retry attempts"""
        error_history = state.get("error_history", [])

        # Add current error with timestamp
        error_entry = {
            "retry_count": state.get("retry_count", 0),
            "error": error_message,
            "sql_query": state.get("sql_query", ""),
            "timestamp": "current"  # Could use actual timestamp if needed
        }

        error_history.append(error_entry)

        # Keep only last 5 errors to avoid bloat
        if len(error_history) > 5:
            error_history = error_history[-5:]

        # Analyze patterns
        patterns = self._analyze_error_patterns(error_history)

        return {
            "error_history": error_history,
            "patterns": patterns,
            "suggestion": self._get_pattern_suggestion(patterns)
        }

    def _analyze_error_patterns(self, error_history: List[Dict]) -> Dict[str, Any]:
        """Analyze error patterns for common issues"""
        patterns = {
            "repeated_errors": [],
            "error_types": {},
            "trending_issues": []
        }

        # Count error types
        for entry in error_history:
            error_type = self._categorize_error(entry["error"])
            patterns["error_types"][error_type] = patterns["error_types"].get(error_type, 0) + 1

        # Find repeated errors
        if len(error_history) >= 2:
            recent_errors = [entry["error"] for entry in error_history[-2:]]
            if len(set(recent_errors)) == 1:  # Same error twice
                patterns["repeated_errors"].append(recent_errors[0])

        # Check for trending issues (errors getting worse)
        if len(error_history) >= 3:
            recent_errors = error_history[-3:]
            if ("join" in recent_errors[-1]["error"].lower() and
                "join" not in recent_errors[-3]["error"].lower()):
                patterns["trending_issues"].append("Join issues appearing")

        return patterns

    def _categorize_error(self, error_message: str) -> str:
        """Categorize errors by type"""
        error_lower = error_message.lower()

        if any(word in error_lower for word in ["join", "cartesian", "duplicate"]):
            return "join_related"
        elif any(word in error_lower for word in ["column", "table", "no such", "doesn't exist"]):
            return "schema_related"
        elif any(word in error_lower for word in ["syntax", "parse", "near"]):
            return "syntax_related"
        elif any(word in error_lower for word in ["aggregate", "group by", "sum", "count"]):
            return "aggregation_related"
        elif any(word in error_lower for word in ["empty", "no rows", "zero"]):
            return "result_related"
        else:
            return "other"

    def _get_pattern_suggestion(self, patterns: Dict[str, Any]) -> str:
        """Get suggestion based on error patterns"""
        suggestions = []

        if patterns["repeated_errors"]:
            suggestions.append(f"Repeated error: {patterns['repeated_errors'][0]}. Consider fundamental approach change.")

        if patterns["error_types"].get("join_related", 0) >= 2:
            suggestions.append("Multiple join-related errors. Review join conditions and cardinality.")

        if patterns["error_types"].get("schema_related", 0) >= 2:
            suggestions.append("Multiple schema-related errors. Verify table and column names.")

        if patterns["trending_issues"]:
            suggestions.append(f"Trending issue: {patterns['trending_issues'][0]}")

        return "; ".join(suggestions) if suggestions else "No specific pattern detected."

    def get_anti_pattern_fixes(self, sql_query: str, validation_issues: List[str]) -> List[str]:
        """Get automatic fix suggestions for common SQL anti-patterns"""
        fixes = []

        # Anti-pattern library
        anti_patterns = {
            "cartesian_product": {
                "patterns": [r"JOIN.* WITHOUT ON", r"FROM.*,\s*.*WHERE.*JOIN.*"],
                "fix": "Add proper JOIN conditions with ON clause to avoid cartesian products"
            },
            "select_star_join": {
                "patterns": [r"SELECT \*.*JOIN"],
                "fix": "Replace SELECT * with explicit column names to avoid ambiguity"
            },
            "group_by_no_agg": {
                "patterns": [r"GROUP BY.*(?!(SUM|COUNT|AVG|MAX|MIN)\()"],
                "fix": "Add aggregation functions (SUM, COUNT, AVG, etc.) when using GROUP BY"
            },
            "order_by_not_selected": {
                "patterns": [r"ORDER BY.*(?=.*\bFROM\b)(?=.*\bSELECT\b)(?!.*\bGROUP BY\b)"],
                "fix": "Include ORDER BY columns in SELECT list or remove them from ORDER BY"
            },
            "missing_where": {
                "patterns": [r"SELECT.*FROM.*JOIN.*WHERE"],
                "fix": "Add WHERE conditions to filter results appropriately"
            },
            "wrong_join_direction": {
                "patterns": [r"JOIN.*ON.*=.*\.customer_id"],
                "fix": "For many-to-one relationships, join from the 'many' table to the 'one' table"
            },
            "date_boundary_issue": {
                "patterns": [r">\s*180", r"<\s*cutoff_date"],
                "fix": "Use consistent date filtering: >= 180 for inclusive boundary"
            }
        }

        sql_upper = sql_query.upper()

        # Check each anti-pattern
        for pattern_name, pattern_info in anti_patterns.items():
            for pattern in pattern_info["patterns"]:
                if re.search(pattern, sql_upper, re.IGNORECASE):
                    fixes.append(f"Anti-pattern detected: {pattern_name}. {pattern_info['fix']}")

        # Add specific fixes based on validation issues
        for issue in validation_issues:
            if "cartesian product" in issue.lower():
                fixes.append("Fix cartesian product: Add missing JOIN conditions or proper WHERE clauses")
            elif "join direction" in issue.lower():
                fixes.append("Fix join direction: Verify cardinality and join order in ontology")
            elif "empty result" in issue.lower():
                fixes.append("Fix empty results: Check WHERE conditions and JOIN logic")

        return fixes[:3]  # Return top 3 fixes to avoid overwhelming

    def route_query(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Route query based on complexity"""
        print("---NODE: ROUTE QUERY---")

        chain = self.prompt_manager.create_chain(
            "route_query",
            self.llm_manager.get_llm()
        )

        result = chain.invoke({
            "ontology": self.ontology_manager.get_ontology_text(),
            "query": state["query"]
        })
        print(f"Routing decision: {result['route']}")
        return {"route": result['route']}

    def map_to_ontology(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Map query to ontology components"""
        print("---NODE: MAP TO ONTOLOGY---")

        chain = self.prompt_manager.create_chain(
            "map_to_ontology",
            self.llm_manager.get_llm()
        )

        ontology_map = chain.invoke({
            "ontology": self.ontology_manager.get_ontology_text(),
            "query": state["query"]
        })
        print(f"Ontology mapping: {ontology_map}")
        return {"ontology_map": ontology_map}

    def generate_plan(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate step-by-step plan for complex queries"""
        print("---NODE: GENERATE PLAN---")

        chain = self.prompt_manager.create_chain(
            "generate_plan",
            self.llm_manager.get_llm("planning")
        )

        plan = chain.invoke({
            "ontology": self.ontology_manager.get_ontology_for_planning(),
            "query": state["query"]
        })
        print(f"Generated Plan:\n{plan}")
        return {"plan": plan}

    def generate_sql(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SQL query based on plan and ontology mapping"""
        print("---NODE: GENERATE SQL---")

        plan_text = state.get("plan", "No specific plan needed - generate direct SQL query.")
        reflection = state.get("reflection", {}).get("corrections", "None")

        chain = self.prompt_manager.create_chain(
            "generate_sql",
            self.llm_manager.get_llm()
        )

        sql_query = chain.invoke({
            "schema": self.db_manager.schema,
            "ontology_map": state["ontology_map"],
            "plan": plan_text,
            "query": state["query"],
            "reflection": reflection
        })

        # Clean the SQL output
        cleaned_sql = sql_query.strip().replace("```sql", "").replace("```", "")
        print(f"Generated SQL: {cleaned_sql}")
        return {"sql_query": cleaned_sql}

    def reflect(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Reflect on generated SQL for correctness"""
        print("---NODE: REFLECT ON SQL---")

        retry_count = state.get("retry_count", 0)
        sql_query = state["sql_query"]

        # Enhanced validation: Multiple validation layers
        validation_notes = []

        # 1. Validate SQL structure
        structure_issues = self.validate_sql_structure(sql_query)
        validation_notes.extend(structure_issues)

        # 2. Validate join directions
        join_issues = self.validate_joins(sql_query)
        validation_notes.extend(join_issues)

        # 3. Perform dry run analysis
        dry_run_result = self.db_manager.dry_run(sql_query)
        if dry_run_result['success']:
            validation_notes.extend(dry_run_result['analysis'])
        else:
            validation_notes.append(f"Dry run failed: {dry_run_result['error']}")

        # 4. Get anti-pattern fixes
        anti_pattern_fixes = self.get_anti_pattern_fixes(sql_query, validation_notes)

        # 5. Add retry context
        retry_context = ""
        if retry_count > 5:
            retry_context = "This is retry #{}/{}. Provide detailed fix examples and focus on join cardinality and data duplication issues.".format(retry_count, self.max_retries)
        elif retry_count > 2:
            retry_context = "This is retry #{}. Pay special attention to join directions and WHERE conditions.".format(retry_count)

        chain = self.prompt_manager.create_chain(
            "reflect",
            self.llm_manager.get_llm("reflection")
        )

        reflection = chain.invoke({
            "query": state["query"],
            "sql_query": sql_query,
            "schema": self.db_manager.schema,
            "ontology": self.ontology_manager.get_ontology_text(),
            "plan": state.get("plan", ""),
            "validation_notes": "; ".join(validation_notes),
            "anti_pattern_fixes": "; ".join(anti_pattern_fixes),
            "retry_context": retry_context
        })

        print(f"Reflection result: {reflection}")

        # Fallback logic: If dry run succeeded and reflection indicates query is fundamentally sound,
        # override the correctness decision to prevent false negatives
        if (dry_run_result['success'] and
            reflection.get('should_retry') == False and
            reflection.get('correct') == False):

            # Check if the corrections indicate the query is fundamentally sound
            corrections = reflection.get('corrections', '').lower()
            sound_indicators = ['fundamentally sound', 'will produce correct results', 'no fundamental flaws', 'logically correct', 'syntactically correct', 'fundamentally correct', 'correct and will produce', 'no changes are necessary', 'no major issues', 'appears to be correct']

            if any(indicator in corrections for indicator in sound_indicators):
                print("Fallback: Query appears fundamentally sound despite reflection flagging as incorrect. Overriding to correct: true")
                reflection['correct'] = True

        return {"reflection": reflection, "retry_count": retry_count + 1}

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SQL query"""
        print(f"---NODE: EXECUTE SQL---\n{state['sql_query']}")
        try:
            results = self.db_manager.execute_query(state["sql_query"])
            print(f"Execution successful: {len(results)} rows returned")
            return {"results": results, "error": None}
        except Exception as e:
            print(f"Execution Error: {e}")
            return {"results": [], "error": str(e)}

    def summarize_results(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize query results based on size"""
        print("---NODE: SUMMARIZE RESULTS---")
        results = state["results"]
        query = state["query"]
        result_count = len(results)
        print(f"Result count: {result_count} rows")

        # Handle large result sets
        if result_count > 1000:
            print(f"Large result set detected ({result_count} rows). Using strategic summarization.")
            return self.summarize_large_results(state)
        else:
            return self.summarize_small_results(state)

    def summarize_large_results(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize large result sets using database-level aggregation"""
        results = state["results"]
        query = state["query"]
        result_count = len(results)

        print(f"Generating summary SQL for {result_count} rows...")

        # Create a summary prompt that generates summary SQL
        chain = self.prompt_manager.create_chain(
            "summarize_large_results",
            self.llm_manager.get_llm()
        )

        try:
            summary_sql = chain.invoke({
                "query": query,
                "result_count": result_count
            })

            # Clean the SQL output
            summary_sql = summary_sql.strip().replace("```sql", "").replace("```", "")
            print(f"Generated summary SQL: {summary_sql}")

            # Execute the summary query
            summary_results = self.db_manager.execute_query(summary_sql)
            summary_count = len(summary_results)

            print(f"Summary query executed: {summary_count} rows returned")

            if summary_count > 0 and summary_count < 100:
                # Use summary results for final answer
                return self.generate_final_answer({
                    "query": query,
                    "results": summary_results
                })
            else:
                # Fallback to statistical summary
                return self.generate_statistical_summary(state)

        except Exception as e:
            print(f"Summary SQL generation failed: {e}")
            return self.generate_statistical_summary(state)

    def summarize_small_results(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize small result sets using existing approach"""
        chain = self.prompt_manager.create_chain(
            "summarize_small_results",
            self.llm_manager.get_llm()
        )

        answer = chain.invoke({
            "query": state["query"],
            "results": json.dumps(state["results"])
        })
        return {"answer": answer}

    def generate_final_answer(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final natural language answer"""
        chain = self.prompt_manager.create_chain(
            "generate_final_answer",
            self.llm_manager.get_llm()
        )

        answer = chain.invoke({
            "query": state["query"],
            "results": json.dumps(state["results"])
        })
        return {"answer": answer}

    def generate_statistical_summary(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a statistical summary when SQL generation fails"""
        results = state["results"]
        result_count = len(results)

        # Extract basic statistics from the results
        if isinstance(results[0], dict):
            numeric_columns = []
            for key, value in results[0].items():
                if isinstance(value, (int, float)):
                    numeric_columns.append(key)

            if numeric_columns:
                output = [f"**Summary of {result_count:,} results**"]
                output.append("")

                for col in numeric_columns[:5]:  # Limit to first 5 numeric columns
                    values = [row.get(col) for row in results if row.get(col) is not None]
                    if values:
                        avg = sum(values) / len(values)
                        min_val = min(values)
                        max_val = max(values)
                        output.append(f"- {col}: Avg={avg:.2f}, Min={min_val}, Max={max_val}")

                return {"answer": "\n".join(output)}

        return {"answer": f"Found {result_count:,} results. Dataset too large for detailed summarization."}

    def handle_error(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle various types of errors"""
        print("---NODE: HANDLE ERROR---")

        # Track error patterns
        error_message = ""
        if state.get("reflection") and not state["reflection"].get("correct", True):
            error_message = state["reflection"].get("corrections", "SQL validation failed")
        else:
            error_message = state.get("error", "Unknown error occurred")

        error_analysis = self.track_error_pattern(state, error_message)

        # Check if this is a reflection error (SQL validation failed)
        reflection = state.get("reflection", {})
        if reflection and not reflection.get("correct", True):
            # This is a validation error from the reflection node
            corrections = reflection.get("corrections", "No specific corrections provided.")
            pattern_suggestion = error_analysis.get("suggestion", "")

            answer = f"I'm sorry, I was unable to generate a valid SQL query for your request.\n\nThe system identified the following issues:\n{corrections}\n\nError Pattern Analysis:\n{pattern_suggestion}\n\nThis could be due to:\n- Missing or incomplete schema information\n- Ambiguous query requirements\n- Fundamental data limitations\n\nPlease try rephrasing your query or providing more specific requirements."
        else:
            # This is a regular execution error
            error = state.get("error", "Unknown error occurred")
            pattern_suggestion = error_analysis.get("suggestion", "")

            answer = f"I encountered an error while executing your query:\n\n{error}\n\nError Pattern Analysis:\n{pattern_suggestion}\n\nThis could be due to:\n- Invalid SQL syntax\n- Database connection issues\n- Missing tables or columns\n\nPlease check your query and try again."

        # Include error analysis in state for debugging
        state["error_analysis"] = error_analysis

        return {"answer": answer}
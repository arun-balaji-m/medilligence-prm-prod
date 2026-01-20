from quick_business_engine.app.services.ai_service import AIService
from quick_business_engine.app.database import execute_query, get_db, registry_collection
from quick_business_engine.app.models.database_models import QueryRequest, QueryResponse
from quick_business_engine.app.config import get_settings
from sqlalchemy import text
import time
import csv
import io
from typing import List, Dict, Any

settings = get_settings()
ai_service = AIService()


class AssessmentService:
    """Main service for handling natural language to SQL queries"""

    @staticmethod
    def process_natural_language_query(query_request: QueryRequest) -> QueryResponse:
        """
        Main workflow: Natural Language -> SQL -> Results
        """
        start_time = time.time()

        try:
            # Step 1: Get all schemas from ChromaDB for Llama
            all_schemas = AssessmentService._get_all_schemas()

            if not all_schemas:
                return QueryResponse(
                    success=False,
                    error="No tables found in registry. Please add table schemas to the registry first."
                )

            # Step 2: Tier 1a - Semantic Search
            semantic_results = ai_service.semantic_search(
                query_request.query,
                top_k=settings.TOP_K_TABLES
            )

            # Step 2: Tier 1b - Llama Selection
            llama_results = ai_service.llama_table_selector(
                query_request.query,
                all_schemas
            )

            # Step 3: Merge and rank to get top 3 tables
            top_tables = ai_service.merge_and_rank_tables(
                semantic_results,
                llama_results
            )

            if not top_tables:
                return QueryResponse(
                    success=False,
                    error="No relevant tables found for your query"
                )

            # Step 4: Tier 2 - Generate SQL with OpenAI
            sql_query = ai_service.generate_sql_query(
                query_request.query,
                top_tables
            )

            print(sql_query)

            # Step 5: Validate SQL
            is_valid, validation_msg = ai_service.validate_sql_query(sql_query)
            if not is_valid:
                return QueryResponse(
                    success=False,
                    error=f"Invalid query: {validation_msg}",
                    sql_query=sql_query
                )

            # Step 6: Execute query (preview only)
            preview_query = f"{sql_query} LIMIT {settings.MAX_ROWS_PREVIEW}"

            with get_db() as db:
                result = db.execute(text(preview_query))
                rows = result.fetchall()
                columns = list(result.keys())

                # Get total count (without limit)
                count_query = f"SELECT COUNT(*) as total FROM ({sql_query}) as subquery"
                total_result = db.execute(text(count_query))
                total_rows = total_result.fetchone()[0]

                # Format preview data
                preview_data = [
                    {col: AssessmentService._serialize_value(row[i])
                     for i, col in enumerate(columns)}
                    for row in rows
                ]

            execution_time = time.time() - start_time

            return QueryResponse(
                success=True,
                sql_query=sql_query,
                preview_data=preview_data,
                total_rows=total_rows,
                columns=columns,
                execution_time=round(execution_time, 2),
                tables_used=[t['table_name'] for t in top_tables]
            )

        except Exception as e:
            return QueryResponse(
                success=False,
                error=str(e),
                execution_time=round(time.time() - start_time, 2)
            )

    @staticmethod
    def export_query_to_csv(sql_query: str) -> str:
        """
        Export full query results to CSV (with row limit)
        """
        try:
            # Add safety limit
            export_query = f"{sql_query} LIMIT {settings.MAX_ROWS_EXPORT}"

            with get_db() as db:
                result = db.execute(text(export_query))
                rows = result.fetchall()
                columns = list(result.keys())

            # Create CSV in memory
            output = io.StringIO()
            writer = csv.writer(output)

            # Write header
            writer.writerow(columns)

            # Write rows
            for row in rows:
                writer.writerow([
                    AssessmentService._serialize_value(val)
                    for val in row
                ])

            return output.getvalue()

        except Exception as e:
            raise Exception(f"CSV export failed: {str(e)}")

    @staticmethod
    def _get_all_schemas() -> List[str]:
        """Get all schemas from ChromaDB for Llama evaluation"""
        try:
            results = registry_collection.get(
                include=["documents"]
            )
            return results['documents'] if results['documents'] else []
        except:
            return []

    @staticmethod
    def _serialize_value(value):
        """Convert database values to JSON-serializable format"""
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return value  # JSONB already serialized
        if hasattr(value, 'isoformat'):
            return value.isoformat()  # Dates
        return str(value)
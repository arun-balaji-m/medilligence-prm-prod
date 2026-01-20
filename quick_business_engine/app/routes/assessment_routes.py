# from fastapi import APIRouter, HTTPException
# from fastapi.responses import StreamingResponse
# from quick_business_engine.app.models.database_models import QueryRequest, QueryResponse, TableSchema
# from quick_business_engine.app.services.assessment_service import AssessmentService
# from quick_business_engine.app.utils.registry_setup import add_table_to_registry, list_registered_tables
# import io
#
# router = APIRouter(prefix="/api", tags=["assessment"])
#
#
# @router.post("/query", response_model=QueryResponse)
# async def execute_natural_language_query(request: QueryRequest):
#     """
#     Convert natural language to SQL and execute
#     """
#     try:
#         response = AssessmentService.process_natural_language_query(request)
#         return response
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# @router.post("/export-csv")
# async def export_query_results(request: QueryRequest):
#     """
#     Export full query results as CSV
#     """
#     try:
#         # First, get the SQL query
#         query_response = AssessmentService.process_natural_language_query(request)
#
#         if not query_response.success:
#             raise HTTPException(status_code=400, detail=query_response.error)
#
#         # Generate CSV
#         csv_content = AssessmentService.export_query_to_csv(query_response.sql_query)
#
#         # Return as downloadable file
#         return StreamingResponse(
#             io.StringIO(csv_content),
#             media_type="text/csv",
#             headers={
#                 "Content-Disposition": "attachment; filename=query_results.csv"
#             }
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# @router.post("/registry/add-table")
# async def add_table_to_registry_endpoint(table_schema: TableSchema):
#     """
#     Add a new table schema to the registry
#     """
#     try:
#         success = add_table_to_registry(table_schema.dict())
#         if success:
#             return {"message": f"Table '{table_schema.table_name}' added successfully"}
#         else:
#             raise HTTPException(status_code=500, detail="Failed to add table")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# @router.get("/registry/tables")
# async def list_tables():
#     """
#     List all registered tables
#     """
#     try:
#         tables = list_registered_tables()
#         return {"tables": tables, "count": len(tables)}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# @router.get("/health")
# async def health_check():
#     """Health check endpoint"""
#     return {"status": "healthy", "service": "Quick Business Engine"}


from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from quick_business_engine.app.models.database_models import QueryRequest, QueryResponse, TableSchema
from quick_business_engine.app.services.assessment_service import AssessmentService
from quick_business_engine.app.utils.registry_setup import add_table_to_registry, list_registered_tables
import io

router = APIRouter(prefix="/api", tags=["assessment"])


@router.post("/query", response_model=QueryResponse)
async def execute_natural_language_query(request: QueryRequest):
    """
    Convert natural language to SQL and execute
    """
    try:
        response = AssessmentService.process_natural_language_query(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export-csv")
async def export_query_results(request: dict):
    try:
        sql_query = request.get("sql_query")

        if not sql_query:
            raise HTTPException(status_code=400, detail="SQL query is required")

        from quick_business_engine.app.services.ai_service import AIService
        is_valid, validation_msg = AIService.validate_sql_query(sql_query)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid query: {validation_msg}")

        csv_content = AssessmentService.export_query_to_csv(sql_query)

        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=query_results.csv"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/registry/add-table")
async def add_table_to_registry_endpoint(table_schema: TableSchema):
    """
    Add a new table schema to the registry
    """
    try:
        success = add_table_to_registry(table_schema.dict())
        if success:
            return {"message": f"Table '{table_schema.table_name}' added successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to add table")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/registry/tables")
async def list_tables():
    """
    List all registered tables
    """
    try:
        tables = list_registered_tables()
        return {"tables": tables, "count": len(tables)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Quick Business Engine"}
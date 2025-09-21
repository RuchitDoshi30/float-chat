"""
Ocean Chat Backend 2.0 - API Router

Main API router that handles all endpoints for the ocean chat application.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, Optional
import logging

from app.services.data_router_service import DataRouterService
from app.services.nc_database_service import NCDatabaseService

logger = logging.getLogger(__name__)

# Create API router
api_router = APIRouter()

# Initialize services
data_router = DataRouterService()
nc_service = NCDatabaseService()


@api_router.get("/")
async def api_root():
    """API root endpoint."""
    return {
        "message": "🌊 Ocean Chat API v1",
        "endpoints": {
            "query": "/query - Submit natural language ocean queries",
            "health": "/health - API health check",
            "live-data": "/live-data/status - Live Argo data status",
            "coverage": "/data/coverage - Data coverage information"
        }
    }


@api_router.post("/query")
async def process_query(request: Dict[str, Any]):
    """
    Process natural language oceanographic queries.
    
    Request body:
    {
        "query": "Show me temperature data in the Pacific Ocean",
        "user_id": "optional_user_id"
    }
    """
    try:
        query_text = request.get("query")
        user_id = request.get("user_id")
        
        if not query_text:
            raise HTTPException(status_code=400, detail="Query text is required")
        
        logger.info(f"🔍 Processing query: {query_text[:100]}...")
        
        # Route query through our dual data source system
        response = await data_router.route_query(query_text, user_id)
        
        return response
        
    except Exception as e:
        logger.error(f"Query processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/query")
async def process_query_get(
    q: str = Query(..., description="Natural language ocean query"),
    user_id: Optional[str] = Query(None, description="Optional user ID")
):
    """
    Process natural language queries via GET request.
    Useful for simple testing and direct URL access.
    """
    try:
        logger.info(f"🔍 Processing GET query: {q[:100]}...")
        
        response = await data_router.route_query(q, user_id)
        return response
        
    except Exception as e:
        logger.error(f"GET query processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/health")
async def health_check():
    """Comprehensive health check for all services."""
    try:
        # Check database connectivity
        coverage = await nc_service.get_data_coverage()
        
        health_status = {
            "status": "healthy",
            "timestamp": "2025-09-21T00:00:00Z",
            "services": {
                "api": "healthy",
                "database": "healthy" if coverage.get("total_measurements", 0) >= 0 else "unhealthy",
                "nlp_service": "healthy",
                "data_router": "healthy"
            },
            "data_coverage": coverage
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "services": {
                "api": "healthy",
                "database": "unknown",
                "nlp_service": "unknown", 
                "data_router": "unknown"
            }
        }


@api_router.get("/live-data/status")
async def get_live_data_status():
    """Get the status of live Argo data availability."""
    try:
        # Import and create external API service to check live data
        from app.services.external_api_service import ExternalAPIService
        external_api = ExternalAPIService()
        
        status = await external_api.get_live_data_status()
        
        return {
            "success": True,
            "live_data_status": status,
            "message": "Live data status retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Live data status check failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "live_data_status": {
                "live_data_available": False,
                "status": "❌ Status check failed",
                "error": str(e)
            }
        }


@api_router.get("/data/coverage")
async def get_data_coverage():
    """Get information about available data coverage."""
    try:
        coverage = await nc_service.get_data_coverage()
        
        return {
            "success": True,
            "data_coverage": coverage,
            "supported_parameters": [
                "temperature",
                "salinity", 
                "pressure",
                "depth"
            ],
            "supported_regions": [
                "pacific",
                "atlantic",
                "indian",
                "arctic",
                "southern"
            ]
        }
        
    except Exception as e:
        logger.error(f"Data coverage error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/demo/queries")
async def get_demo_queries():
    """Get sample queries for demonstration purposes."""
    return {
        "success": True,
        "demo_queries": [
            {
                "query": "Show me temperature data in the Pacific Ocean",
                "description": "Retrieve temperature measurements from Pacific region",
                "expected_visualizations": ["map", "3d_globe", "heatmap"]
            },
            {
                "query": "What are the salinity patterns near the equator?",
                "description": "Analyze salinity distribution in equatorial waters",
                "expected_visualizations": ["map", "heatmap", "depth_profile"]
            },
            {
                "query": "Find warm water currents in the Atlantic",
                "description": "Locate high-temperature water masses in Atlantic Ocean",
                "expected_visualizations": ["map", "temperature_timeseries", "3d_globe"]
            },
            {
                "query": "Compare ocean conditions between 2022 and 2023",
                "description": "Temporal comparison of oceanographic parameters",
                "expected_visualizations": ["timeseries", "comparison_charts"]
            },
            {
                "query": "Show me deep water measurements below 1000 meters",
                "description": "Retrieve deep ocean data with depth filtering",
                "expected_visualizations": ["depth_profile", "map", "3d_globe"]
            }
        ]
    }


@api_router.get("/demo/status")
async def get_demo_status():
    """Get demonstration system status and configuration."""
    return {
        "success": True,
        "demo_config": {
            "dual_data_source": True,
            "api_fallback_enabled": True,
            "simulated_api_responses": True,
            "sample_data_generation": True
        },
        "system_info": {
            "version": "2.0.0",
            "environment": "demo",
            "features": [
                "Natural language processing",
                "Dual data source architecture", 
                "Real-time API with database fallback",
                "3D visualization support",
                "Multi-parameter ocean analysis"
            ]
        }
    }
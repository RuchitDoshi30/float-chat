"""
Ocean Chat Backend 2.0 - Data Router Service

The core service that implements intelligent dual data source architecture.
Tries live APIs first, falls back to local database seamlessly.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx

from app.core.config import settings
from app.services.external_api_service import ExternalAPIService
from app.services.nc_database_service import NCDatabaseService
from app.services.nlp_service import NLPService

logger = logging.getLogger(__name__)


class DataRouterService:
    """
    Intelligent data router that seamlessly switches between live APIs and local database.
    Users never know which data source they're getting.
    """
    
    def __init__(self):
        self.external_api_service = ExternalAPIService()
        self.nc_database_service = NCDatabaseService()
        self.nlp_service = NLPService()
    
    async def route_query(self, query_text: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Main routing method - tries API first, falls back to database.
        
        Args:
            query_text: Natural language query from user
            user_id: Optional user ID for tracking
            
        Returns:
            Unified response regardless of data source
        """
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Parse natural language query
            logger.info(f"🔍 Processing query: {query_text[:100]}...")
            parsed_query = await self.nlp_service.parse_query(query_text)
            
            # Step 2: Try live API data first (Priority: Argo → ERDDAP → NOAA)
            api_response = None
            try:
                logger.info("🌐 Attempting live API data retrieval...")
                api_response = await self._try_api_source(parsed_query)
                
                if api_response and self._validate_response(api_response):
                    response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                    logger.info(f"✅ API data retrieved successfully in {response_time:.0f}ms")
                    
                    return self._format_unified_response(
                        data=api_response,
                        source="live_api",
                        query=query_text,
                        parsed_query=parsed_query,
                        response_time_ms=int(response_time)
                    )
                    
            except Exception as e:
                logger.warning(f"⚠️ API source failed: {e}")
            
            # Step 3: Fallback to local database (Secondary source)
            logger.info("💾 Falling back to local database...")
            db_response = await self._try_database_source(parsed_query)
            
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.info(f"✅ Database data retrieved successfully in {response_time:.0f}ms")
            
            return self._format_unified_response(
                data=db_response,
                source="local_database",
                query=query_text,
                parsed_query=parsed_query,
                response_time_ms=int(response_time)
            )
            
        except Exception as e:
            logger.error(f"❌ Data routing failed: {e}")
            return self._format_error_response(query_text, str(e))
    
    async def _try_api_source(self, parsed_query: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """
        Attempt to get data from external APIs with timeout.
        
        Args:
            parsed_query: Parsed query parameters
            
        Returns:
            API response data or None if failed
        """
        try:
            # Use asyncio.wait_for to enforce timeout
            api_data = await asyncio.wait_for(
                self.external_api_service.fetch_data(parsed_query),
                timeout=settings.API_TIMEOUT_SECONDS
            )
            return api_data
            
        except asyncio.TimeoutError:
            logger.warning(f"⏰ API timeout after {settings.API_TIMEOUT_SECONDS}s")
            return None
        except Exception as e:
            logger.warning(f"🚫 API error: {e}")
            return None
    
    async def _try_database_source(self, parsed_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get data from local NetCDF database.
        
        Args:
            parsed_query: Parsed query parameters
            
        Returns:
            Database response data
        """
        return await self.nc_database_service.query_data(parsed_query)
    
    def _validate_response(self, response: Any) -> bool:
        """
        Validate API response has sufficient data.
        
        Args:
            response: API response to validate
            
        Returns:
            True if response is valid and has data
        """
        if not response:
            return False
        
        if isinstance(response, list):
            return len(response) > 0
        
        if isinstance(response, dict):
            return len(response.get("data", [])) > 0
        
        return False
    
    def _format_unified_response(
        self, 
        data: Any, 
        source: str, 
        query: str, 
        parsed_query: Dict[str, Any],
        response_time_ms: int
    ) -> Dict[str, Any]:
        """
        Format response in unified structure regardless of data source.
        
        Args:
            data: Raw data from source
            source: Data source identifier
            query: Original query text
            parsed_query: Parsed query parameters
            response_time_ms: Response time in milliseconds
            
        Returns:
            Unified response structure
        """
        # Ensure data is in consistent format
        if isinstance(data, dict) and "data" in data:
            formatted_data = data["data"]
        else:
            formatted_data = data if isinstance(data, list) else [data]
        
        return {
            "success": True,
            "query": {
                "original": query,
                "parsed": parsed_query
            },
            "data": {
                "measurements": formatted_data,
                "count": len(formatted_data),
                "source": source,
                "timestamp": datetime.utcnow().isoformat()
            },
            "metadata": {
                "response_time_ms": response_time_ms,
                "data_source": source,
                "query_type": parsed_query.get("type", "unknown")
            },
            "visualization": {
                "charts": self._suggest_visualizations(formatted_data, parsed_query),
                "map_bounds": self._calculate_map_bounds(formatted_data)
            }
        }
    
    def _format_error_response(self, query: str, error: str) -> Dict[str, Any]:
        """
        Format error response.
        
        Args:
            query: Original query text
            error: Error message
            
        Returns:
            Error response structure
        """
        return {
            "success": False,
            "query": {"original": query},
            "error": {
                "message": "Unable to process query at this time",
                "details": error if settings.DEBUG else "Internal server error",
                "code": "DATA_UNAVAILABLE"
            },
            "suggestions": [
                "Try a different geographic region",
                "Specify a different time range",
                "Check your query format"
            ]
        }
    
    def _suggest_visualizations(self, data: List[Dict[str, Any]], parsed_query: Dict[str, Any]) -> List[str]:
        """
        Suggest appropriate visualizations based on data and query.
        
        Args:
            data: Response data
            parsed_query: Parsed query parameters
            
        Returns:
            List of suggested visualization types
        """
        visualizations = []
        
        if not data:
            return visualizations
        
        # Check available parameters
        sample = data[0] if data else {}
        has_temperature = "temperature" in sample
        has_salinity = "salinity" in sample
        has_depth = "depth" in sample
        has_time_series = len(data) > 1
        
        # Map visualization (always available)
        visualizations.append("map")
        
        # 3D globe if spatial data
        if "latitude" in sample and "longitude" in sample:
            visualizations.append("3d_globe")
        
        # Time series charts
        if has_time_series:
            if has_temperature:
                visualizations.append("temperature_timeseries")
            if has_salinity:
                visualizations.append("salinity_timeseries")
        
        # Depth profiles
        if has_depth and has_temperature:
            visualizations.append("temperature_depth_profile")
        
        # Heat maps for spatial data
        if len(data) > 10:
            visualizations.append("heatmap")
        
        return visualizations
    
    def _calculate_map_bounds(self, data: List[Dict[str, Any]]) -> Optional[Dict[str, float]]:
        """
        Calculate geographic bounds for map visualization.
        
        Args:
            data: Response data with lat/lon
            
        Returns:
            Map bounds or None
        """
        if not data:
            return None
        
        lats = [item.get("latitude") for item in data if item.get("latitude")]
        lons = [item.get("longitude") for item in data if item.get("longitude")]
        
        if not lats or not lons:
            return None
        
        return {
            "min_lat": min(lats),
            "max_lat": max(lats),
            "min_lon": min(lons),
            "max_lon": max(lons)
        }
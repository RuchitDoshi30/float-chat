"""
Ocean Chat Backend 2.0 - Natural Language Processing Service

Service for parsing natural language queries into structured parameters.
"""

import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import spacy

logger = logging.getLogger(__name__)


class NLPService:
    """Service for processing natural language oceanographic queries."""
    
    def __init__(self):
        # For demo purposes, we'll use simple pattern matching
        # In production, this would use trained NLP models
        self.oceanographic_terms = {
            "temperature": ["temperature", "temp", "warm", "cold", "thermal"],
            "salinity": ["salinity", "salt", "sal", "saline"],
            "depth": ["depth", "deep", "shallow", "surface", "bottom"],
            "current": ["current", "flow", "velocity", "circulation"],
            "pressure": ["pressure", "press", "atm"]
        }
        
        self.regions = {
            "pacific": {"center_lat": 0, "center_lon": -150, "bounds": [-60, 60, -180, -100]},
            "atlantic": {"center_lat": 20, "center_lon": -30, "bounds": [-60, 70, -80, 20]},
            "indian": {"center_lat": -20, "center_lon": 80, "bounds": [-60, 30, 40, 120]},
            "arctic": {"center_lat": 80, "center_lon": 0, "bounds": [66, 90, -180, 180]},
            "southern": {"center_lat": -60, "center_lon": 0, "bounds": [-90, -60, -180, 180]}
        }
    
    async def parse_query(self, query_text: str) -> Dict[str, Any]:
        """
        Parse natural language query into structured parameters.
        
        Args:
            query_text: Natural language query
            
        Returns:
            Structured query parameters
        """
        try:
            query_lower = query_text.lower()
            parsed = {
                "original_query": query_text,
                "type": "general",
                "parameters": [],
                "spatial": {},
                "temporal": {},
                "filters": {}
            }
            
            # Extract parameters of interest
            parsed["parameters"] = self._extract_parameters(query_lower)
            
            # Extract spatial information
            spatial_info = self._extract_spatial_info(query_lower)
            parsed["spatial"] = spatial_info
            
            # Extract temporal information
            temporal_info = self._extract_temporal_info(query_lower)
            parsed["temporal"] = temporal_info
            
            # Determine query type
            parsed["type"] = self._determine_query_type(parsed)
            
            # Add default spatial bounds if not specified
            if not parsed["spatial"]:
                parsed["spatial"] = self._get_default_spatial_bounds()
            
            # Add default temporal range if not specified
            if not parsed["temporal"]:
                parsed["temporal"] = self._get_default_temporal_range()
            
            # Convert to query parameters format
            query_params = self._convert_to_query_params(parsed)
            
            logger.info(f"🧠 Parsed query: {parsed['type']} query for {parsed['parameters']}")
            return query_params
            
        except Exception as e:
            logger.error(f"NLP parsing error: {e}")
            return self._get_default_query_params(query_text)
    
    def _extract_parameters(self, query_lower: str) -> List[str]:
        """Extract oceanographic parameters from query."""
        parameters = []
        
        for param, terms in self.oceanographic_terms.items():
            if any(term in query_lower for term in terms):
                parameters.append(param)
        
        # Default to temperature if no parameters specified
        if not parameters:
            parameters = ["temperature"]
        
        return parameters
    
    def _extract_spatial_info(self, query_lower: str) -> Dict[str, Any]:
        """Extract spatial information from query."""
        spatial = {}
        
        # Check for ocean regions
        for region, bounds in self.regions.items():
            if region in query_lower:
                spatial["region"] = region
                spatial["center_lat"] = bounds["center_lat"]
                spatial["center_lon"] = bounds["center_lon"]
                spatial["bounds"] = bounds["bounds"]
                break
        
        # Check for specific coordinates (simplified)
        lat_match = re.search(r'(\d+(?:\.\d+)?)\s*[°]?\s*[ns]', query_lower)
        lon_match = re.search(r'(\d+(?:\.\d+)?)\s*[°]?\s*[ew]', query_lower)
        
        if lat_match and lon_match:
            lat = float(lat_match.group(1))
            lon = float(lon_match.group(1))
            
            # Adjust for hemisphere
            if 's' in lat_match.group(0):
                lat = -lat
            if 'w' in lon_match.group(0):
                lon = -lon
            
            spatial["center_lat"] = lat
            spatial["center_lon"] = lon
            spatial["bounds"] = [lat-5, lat+5, lon-5, lon+5]
        
        # Check for directional terms
        if "north" in query_lower:
            spatial["center_lat"] = 45
        elif "south" in query_lower:
            spatial["center_lat"] = -45
        
        if "east" in query_lower:
            spatial["center_lon"] = 90
        elif "west" in query_lower:
            spatial["center_lon"] = -90
        
        return spatial
    
    def _extract_temporal_info(self, query_lower: str) -> Dict[str, Any]:
        """Extract temporal information from query."""
        temporal = {}
        
        # Check for specific years
        year_match = re.search(r'(20\d{2})', query_lower)
        if year_match:
            year = int(year_match.group(1))
            temporal["start_time"] = f"{year}-01-01"
            temporal["end_time"] = f"{year}-12-31"
        
        # Check for relative time terms
        if "recent" in query_lower or "latest" in query_lower:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            temporal["start_time"] = start_date.strftime("%Y-%m-%d")
            temporal["end_time"] = end_date.strftime("%Y-%m-%d")
        elif "last year" in query_lower:
            current_year = datetime.now().year
            temporal["start_time"] = f"{current_year-1}-01-01"
            temporal["end_time"] = f"{current_year-1}-12-31"
        
        return temporal
    
    def _determine_query_type(self, parsed: Dict[str, Any]) -> str:
        """Determine the type of query based on parsed information."""
        query_lower = parsed["original_query"].lower()
        
        if "trend" in query_lower or "change" in query_lower:
            return "trend_analysis"
        elif "compare" in query_lower or "difference" in query_lower:
            return "comparison"
        elif "pattern" in query_lower or "distribution" in query_lower:
            return "pattern_analysis"
        elif len(parsed["spatial"]) > 0:
            return "spatial_query"
        elif len(parsed["temporal"]) > 0:
            return "temporal_query"
        else:
            return "general"
    
    def _get_default_spatial_bounds(self) -> Dict[str, Any]:
        """Get default spatial bounds (global)."""
        return {
            "region": "global",
            "center_lat": 0,
            "center_lon": 0,
            "bounds": [-90, 90, -180, 180]
        }
    
    def _get_default_temporal_range(self) -> Dict[str, Any]:
        """Get default temporal range (last year)."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        return {
            "start_time": start_date.strftime("%Y-%m-%d"),
            "end_time": end_date.strftime("%Y-%m-%d")
        }
    
    def _convert_to_query_params(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Convert parsed information to query parameters format."""
        spatial = parsed.get("spatial", {})
        temporal = parsed.get("temporal", {})
        
        params = {
            "type": parsed["type"],
            "parameters": parsed["parameters"],
            "center_lat": spatial.get("center_lat", 0),
            "center_lon": spatial.get("center_lon", 0)
        }
        
        # Add spatial bounds if available
        if "bounds" in spatial:
            bounds = spatial["bounds"]
            params.update({
                "min_lat": bounds[0],
                "max_lat": bounds[1], 
                "min_lon": bounds[2],
                "max_lon": bounds[3]
            })
        
        # Add temporal bounds if available
        if "start_time" in temporal:
            params["start_time"] = temporal["start_time"]
        if "end_time" in temporal:
            params["end_time"] = temporal["end_time"]
        
        # Add depth bounds (simplified)
        if "surface" in parsed["original_query"].lower():
            params["min_depth"] = 0
            params["max_depth"] = 50
        elif "deep" in parsed["original_query"].lower():
            params["min_depth"] = 1000
            params["max_depth"] = 5000
        
        return params
    
    def _get_default_query_params(self, query_text: str) -> Dict[str, Any]:
        """Get default query parameters for fallback."""
        return {
            "type": "general",
            "parameters": ["temperature"],
            "center_lat": 0,
            "center_lon": 0,
            "min_lat": -90,
            "max_lat": 90,
            "min_lon": -180,
            "max_lon": 180,
            "start_time": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
            "end_time": datetime.now().strftime("%Y-%m-%d")
        }
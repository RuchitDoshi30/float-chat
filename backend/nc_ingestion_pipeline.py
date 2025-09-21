#!/usr/bin/env python3
"""
Ocean Chat Backend 2.0 - PostgreSQL NC File Ingestion

Adapted from user's main_ingestion.py to work with our PostgreSQL database models.
Processes NetCDF files and stores data in ocean_measurements and nc_file_metadata tables.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import xarray as xr
import pandas as pd
import json
import logging
import uuid
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

# Our database imports
from app.core.database import SessionLocal, engine
from app.models.ocean_data import OceanMeasurement, NCFileMetadata
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Configuration ---
NC_FILES_DIR = Path("data/nc_files")
PROCESSED_DIR = Path("data/processed")

# Core variables mapping (from user's script)
CORE_VARIABLES = {
    'WMO': 'PLATFORM_NUMBER',
    'JULD': 'JULD',
    'LATITUDE': 'LATITUDE',
    'LONGITUDE': 'LONGITUDE',
    'PRES': 'PRES',
    'TEMP': 'TEMP',
    'PSAL': 'PSAL',
    'PRES_QC': 'PRES_QC',
    'TEMP_QC': 'TEMP_QC',
    'PSAL_QC': 'PSAL_QC',
    'JULD_QC': 'JULD_QC',
    'POSITION_QC': 'POSITION_QC',
    'CYCLE_NUMBER': 'CYCLE_NUMBER',
    'DATA_MODE': 'DATA_MODE'
}

class NCFileIngestionProcessor:
    """Processes NetCDF files and ingests them into PostgreSQL database."""
    
    def __init__(self):
        self.db_session: Optional[Session] = None
        self.processed_files = 0
        self.total_measurements = 0
        
    def __enter__(self):
        self.db_session = SessionLocal()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db_session:
            if exc_type is None:
                self.db_session.commit()
            else:
                self.db_session.rollback()
            self.db_session.close()
    
    def process_all_nc_files(self) -> Dict[str, Any]:
        """Process all NetCDF files in the nc_files directory."""
        logger.info("🌊 Starting NC file ingestion into PostgreSQL...")
        
        if not NC_FILES_DIR.exists():
            raise FileNotFoundError(f"NC files directory not found: {NC_FILES_DIR}")
        
        nc_files = list(NC_FILES_DIR.glob("*.nc"))
        if not nc_files:
            raise FileNotFoundError(f"No .nc files found in {NC_FILES_DIR}")
        
        logger.info(f"📁 Found {len(nc_files)} NetCDF files to process")
        
        results = {
            "files_processed": 0,
            "total_measurements": 0,
            "files_details": [],
            "errors": []
        }
        
        for nc_file in nc_files:
            try:
                logger.info(f"📄 Processing {nc_file.name}...")
                
                # Extract and process file
                df, metadata = self.extract_and_transform_file(nc_file)
                
                # Store in database
                file_result = self.store_in_database(nc_file, df, metadata)
                
                results["files_details"].append(file_result)
                results["files_processed"] += 1
                results["total_measurements"] += file_result["measurements_stored"]
                
                logger.info(f"✅ {nc_file.name}: {file_result['measurements_stored']} measurements stored")
                
            except Exception as e:
                error_msg = f"❌ Failed to process {nc_file.name}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        logger.info(f"🎉 Ingestion complete! {results['files_processed']} files, {results['total_measurements']} total measurements")
        return results
    
    def extract_and_transform_file(self, file_path: Path) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Extract data from NetCDF file using user's extraction logic."""
        logger.info(f"📊 Extracting data from {file_path.name}...")
        
        try:
            ds = xr.open_dataset(file_path, decode_cf=True, mask_and_scale=True)
            
            # Build metadata (from user's script)
            metadata = {
                "file_info": {
                    "filename": file_path.name,
                    "file_path": str(file_path),
                    "file_size": file_path.stat().st_size,
                    "dimensions": {k: int(v) for k, v in ds.sizes.items()},
                    "global_attributes": {k: self._safe_to_str(v) for k, v in ds.attrs.items()},
                },
                "variables": {},
                "processing_time": datetime.now().isoformat()
            }
            
            # Extract profile data (adapted from user's script)
            profiles_data = []
            n_prof = ds.sizes.get('N_PROF', 0)
            n_levels = ds.sizes.get('N_LEVELS', 0)
            
            logger.info(f"📈 Processing {n_prof} profiles with up to {n_levels} levels each")
            
            for prof_idx in range(n_prof):
                profile_vars = self._extract_profile_variables(ds, prof_idx)
                
                # Extract level-based measurements
                for level_idx in range(n_levels):
                    level_data = profile_vars.copy()
                    level_data['PROFILE_INDEX'] = prof_idx
                    level_data['LEVEL_INDEX'] = level_idx
                    
                    # Core measurements
                    level_data.update(self._extract_level_measurements(ds, prof_idx, level_idx))
                    
                    # Only include levels with actual pressure data
                    if level_data.get('PRES') is not None:
                        profiles_data.append(level_data)
            
            # Create DataFrame and apply quality control
            df = pd.DataFrame(profiles_data)
            df = self._apply_quality_control(df)
            
            # Add variable metadata
            for var_name in CORE_VARIABLES.values():
                if var_name in ds.variables:
                    var_obj = ds[var_name]
                    metadata["variables"][var_name] = {
                        "dimensions": list(var_obj.dims),
                        "dtype": str(var_obj.dtype),
                        "attributes": {k: self._safe_to_str(v) for k, v in var_obj.attrs.items()},
                    }
            
            logger.info(f"📋 Extracted {len(df)} quality-controlled measurements")
            return df, metadata
            
        except Exception as e:
            raise Exception(f"Error extracting data from {file_path.name}: {e}")
    
    def _extract_profile_variables(self, ds: xr.Dataset, prof_idx: int) -> Dict[str, Any]:
        """Extract profile-level variables."""
        profile_vars = {}
        
        # Core identifiers and location
        if 'PLATFORM_NUMBER' in ds.variables:
            profile_vars['WMO'] = self._safe_to_str(ds['PLATFORM_NUMBER'].values[prof_idx])
        if 'JULD' in ds.variables:
            profile_vars['JULD'] = ds['JULD'].values[prof_idx]
        if 'LATITUDE' in ds.variables:
            profile_vars['LATITUDE'] = float(ds['LATITUDE'].values[prof_idx])
        if 'LONGITUDE' in ds.variables:
            profile_vars['LONGITUDE'] = float(ds['LONGITUDE'].values[prof_idx])
        if 'CYCLE_NUMBER' in ds.variables:
            profile_vars['CYCLE_NUMBER'] = int(ds['CYCLE_NUMBER'].values[prof_idx])
        if 'DATA_MODE' in ds.variables:
            profile_vars['DATA_MODE'] = self._safe_to_str(ds['DATA_MODE'].values[prof_idx])
        
        # Quality flags
        if 'JULD_QC' in ds.variables:
            profile_vars['JULD_QC'] = self._safe_to_str(ds['JULD_QC'].values[prof_idx])
        if 'POSITION_QC' in ds.variables:
            profile_vars['POSITION_QC'] = self._safe_to_str(ds['POSITION_QC'].values[prof_idx])
        
        return profile_vars
    
    def _extract_level_measurements(self, ds: xr.Dataset, prof_idx: int, level_idx: int) -> Dict[str, Any]:
        """Extract level-based measurements."""
        level_data = {}
        
        # Core measurement variables
        if 'PRES' in ds.variables:
            pres_val = ds['PRES'].values[prof_idx, level_idx]
            level_data['PRES'] = float(pres_val) if not pd.isna(pres_val) else None
        if 'TEMP' in ds.variables:
            temp_val = ds['TEMP'].values[prof_idx, level_idx]
            level_data['TEMP'] = float(temp_val) if not pd.isna(temp_val) else None
        if 'PSAL' in ds.variables:
            psal_val = ds['PSAL'].values[prof_idx, level_idx]
            level_data['PSAL'] = float(psal_val) if not pd.isna(psal_val) else None
        
        # Quality control flags
        if 'PRES_QC' in ds.variables:
            level_data['PRES_QC'] = self._safe_to_str(ds['PRES_QC'].values[prof_idx, level_idx])
        if 'TEMP_QC' in ds.variables:
            level_data['TEMP_QC'] = self._safe_to_str(ds['TEMP_QC'].values[prof_idx, level_idx])
        if 'PSAL_QC' in ds.variables:
            level_data['PSAL_QC'] = self._safe_to_str(ds['PSAL_QC'].values[prof_idx, level_idx])
        
        return level_data
    
    def _apply_quality_control(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply quality control filters (from user's script)."""
        logger.info("🔍 Applying quality control filters...")
        
        initial_count = len(df)
        
        # Quality control flags (keep only good data: '1' or '2')
        good_qc_values = ['1', '2']
        
        # Filter by position quality
        if 'POSITION_QC' in df.columns:
            df = df[df['POSITION_QC'].isin(good_qc_values)]
        
        # Filter by time quality
        if 'JULD_QC' in df.columns:
            df = df[df['JULD_QC'].isin(good_qc_values)]
        
        # Filter by measurement quality
        for var in ['PRES', 'TEMP', 'PSAL']:
            qc_col = f'{var}_QC'
            if qc_col in df.columns:
                df = df[df[qc_col].isin(good_qc_values)]
        
        # Remove records with all NaN measurements
        measurement_cols = ['PRES', 'TEMP', 'PSAL']
        available_cols = [col for col in measurement_cols if col in df.columns]
        if available_cols:
            df = df.dropna(subset=available_cols, how='all')
        
        # Remove duplicates
        if 'PROFILE_INDEX' in df.columns and 'LEVEL_INDEX' in df.columns:
            df = df.drop_duplicates(subset=['PROFILE_INDEX', 'LEVEL_INDEX'])
        
        final_count = len(df)
        filter_rate = ((initial_count - final_count) / initial_count * 100) if initial_count > 0 else 0
        logger.info(f"📊 QC filtering: {initial_count} → {final_count} records ({filter_rate:.1f}% filtered)")
        
        return df
    
    def store_in_database(self, file_path: Path, df: pd.DataFrame, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Store extracted data in PostgreSQL database."""
        logger.info(f"💾 Storing data in PostgreSQL...")
        
        # Create NC file metadata record
        nc_metadata = NCFileMetadata(
            id=uuid.uuid4(),
            filename=file_path.name,
            file_path=str(file_path),
            file_size=file_path.stat().st_size,
            total_measurements=len(df),
            variables=json.dumps(list(CORE_VARIABLES.keys())),
            ingestion_status="processing",
            ingestion_date=datetime.now(),
            created_at=datetime.now()
        )
        
        # Calculate spatial/temporal bounds
        if not df.empty:
            nc_metadata.min_latitude = float(df['LATITUDE'].min()) if 'LATITUDE' in df.columns else None
            nc_metadata.max_latitude = float(df['LATITUDE'].max()) if 'LATITUDE' in df.columns else None
            nc_metadata.min_longitude = float(df['LONGITUDE'].min()) if 'LONGITUDE' in df.columns else None
            nc_metadata.max_longitude = float(df['LONGITUDE'].max()) if 'LONGITUDE' in df.columns else None
            
            # Convert JULD to datetime for temporal bounds
            if 'JULD' in df.columns:
                try:
                    reference_date = pd.Timestamp('1950-01-01')
                    df['measurement_datetime'] = pd.to_datetime(reference_date + pd.to_timedelta(df['JULD'], unit='D'))
                    nc_metadata.start_time = df['measurement_datetime'].min()
                    nc_metadata.end_time = df['measurement_datetime'].max()
                except Exception as e:
                    logger.warning(f"Could not parse JULD times: {e}")
        
        try:
            self.db_session.add(nc_metadata)
            self.db_session.flush()  # Get the ID
            
            # Create measurement records
            measurements_stored = 0
            batch_size = 1000
            
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]
                measurement_objects = []
                
                for _, row in batch.iterrows():
                    measurement = OceanMeasurement(
                        id=uuid.uuid4(),
                        latitude=row.get('LATITUDE'),
                        longitude=row.get('LONGITUDE'),
                        depth=row.get('PRES', 0),  # Use pressure as depth
                        temperature=row.get('TEMP'),
                        salinity=row.get('PSAL'),
                        pressure=row.get('PRES'),
                        measurement_time=row.get('measurement_datetime', datetime.now()),
                        data_source=f"nc_file:{file_path.name}",
                        quality_flag=1,  # Assume good quality after filtering
                        platform_id=row.get('WMO', 'UNKNOWN'),
                        instrument_type="Argo Float",
                        created_at=datetime.now()
                    )
                    measurement_objects.append(measurement)
                
                self.db_session.bulk_save_objects(measurement_objects)
                measurements_stored += len(measurement_objects)
                
                if i % (batch_size * 5) == 0:  # Progress update every 5 batches
                    logger.info(f"📈 Stored {measurements_stored}/{len(df)} measurements...")
            
            # Update metadata with success status
            nc_metadata.ingestion_status = "completed"
            nc_metadata.total_measurements = measurements_stored
            
            logger.info(f"✅ Successfully stored {measurements_stored} measurements")
            
            return {
                "filename": file_path.name,
                "measurements_stored": measurements_stored,
                "file_size_mb": file_path.stat().st_size / (1024 * 1024),
                "spatial_bounds": {
                    "lat_range": [nc_metadata.min_latitude, nc_metadata.max_latitude],
                    "lon_range": [nc_metadata.min_longitude, nc_metadata.max_longitude]
                },
                "temporal_bounds": {
                    "start": nc_metadata.start_time.isoformat() if nc_metadata.start_time else None,
                    "end": nc_metadata.end_time.isoformat() if nc_metadata.end_time else None
                }
            }
            
        except Exception as e:
            nc_metadata.ingestion_status = "failed"
            nc_metadata.error_message = str(e)
            raise e
    
    def _safe_to_str(self, value) -> str:
        """Safely convert NetCDF values to strings (from user's script)."""
        import numpy as np
        
        if isinstance(value, (bytes, bytearray)):
            try:
                return value.decode("utf-8", errors="ignore").strip()
            except Exception:
                return str(value)
        
        if isinstance(value, (list, tuple, np.ndarray)):
            return str([self._safe_to_str(v) for v in value])
        
        if isinstance(value, np.generic):
            return str(value.item())
        
        if value is None:
            return ""
        
        return str(value)


def main():
    """Main ingestion pipeline."""
    logger.info("🌊 === Ocean Chat NC File Ingestion Pipeline ===")
    
    try:
        with NCFileIngestionProcessor() as processor:
            results = processor.process_all_nc_files()
            
            # Save processing summary
            PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
            summary_file = PROCESSED_DIR / f"ingestion_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(summary_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"📋 Processing summary saved to {summary_file}")
            logger.info("🎉 === Ingestion Pipeline Completed Successfully! ===")
            
            return results
            
    except Exception as e:
        logger.error(f"💥 Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()
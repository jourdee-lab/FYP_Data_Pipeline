#!/usr/bin/env python3
"""
Phase 6: Compute Simple Indicators from ED-Level SAS Data (1981)
==================================================================

Simplified approach: directly compute key indicators from raw SAS columns.

Inputs:
  - ED-level SAS data: data/processed/raw_ed_level/1981/sas0X_1981_ed_level.csv

Outputs:
  - Indicator table: data/processed/indicators/1981/manchester_eds_1981_indicators.csv
  - Summary: data/processed/indicators/1981/indicators_summary.txt

Author: FYP Data Pipeline
Date: 2026-01-14
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
SAS02_PATH = Path("data/processed/raw_ed_level/1981/sas02_1981_ed_level.csv")
SAS04_PATH = Path("data/processed/raw_ed_level/1981/sas04_1981_ed_level.csv")
SAS07_PATH = Path("data/processed/raw_ed_level/1981/sas07_1981_ed_level.csv")
SAS10_PATH = Path("data/processed/raw_ed_level/1981/sas10_1981_ed_level.csv")
OUTPUT_PATH = Path("data/processed/indicators/1981/manchester_eds_1981_indicators.csv")
SUMMARY_PATH = Path("data/processed/indicators/1981/indicators_summary.txt")

def main():
    """Load data and compute indicators."""
    
    logger.info("="*70)
    logger.info("PHASE 6: INDICATOR COMPUTATION (1981) - SIMPLIFIED")
    logger.info("="*70)
    
    # Load all SAS tables
    logger.info("\nLoading SAS tables...")
    sas02 = pd.read_csv(SAS02_PATH)
    sas04 = pd.read_csv(SAS04_PATH)
    sas07 = pd.read_csv(SAS07_PATH)
    sas10 = pd.read_csv(SAS10_PATH)
    
    logger.info(f"  SAS02: {sas02.shape}")
    logger.info(f"  SAS04: {sas04.shape}")
    logger.info(f"  SAS07: {sas07.shape}")
    logger.info(f"  SAS10: {sas10.shape}")
    
    # Merge all on zoneid
    logger.info("\nMerging tables on zoneid...")
    df = sas02.copy()
    df = df.merge(sas04[['zoneid'] + [c for c in sas04.columns if c != 'zoneid']], 
                  on='zoneid', how='inner')
    df = df.merge(sas07[['zoneid'] + [c for c in sas07.columns if c != 'zoneid']], 
                  on='zoneid', how='inner')
    df = df.merge(sas10[['zoneid'] + [c for c in sas10.columns if c != 'zoneid']], 
                  on='zoneid', how='inner')
    
    logger.info(f"  Merged: {df.shape[0]} EDs × {df.shape[1]} columns")
    
    # Create indicators dataframe
    indicators = pd.DataFrame({'zoneid': df['zoneid']})
    
    # ===== DEMOGRAPHICS (SAS02) =====
    logger.info("\nComputing DEMOGRAPHIC indicators...")
    indicators['TOTAL_RES_1981'] = df['81sas020050'].astype(float)
    indicators['PCT_MALE_1981'] = (df['81sas020051'] / df['81sas020050'] * 100).fillna(0)
    indicators['PCT_FEMALE_1981'] = (df['81sas020054'] / df['81sas020050'] * 100).fillna(0)
    
    # ===== ETHNIC PRESENCE (SAS04) =====
    logger.info("Computing ETHNIC PRESENCE indicators...")
    indicators['CHINESE_BORN_1981'] = df['81sas040359'].astype(float)
    indicators['CHINESE_BORN_MALE_1981'] = df['81sas040360'].astype(float)
    indicators['CHINESE_BORN_FEMALE_1981'] = df['81sas040361'].astype(float)
    indicators['PCT_CHINESE_BORN_1981'] = (df['81sas040359'] / df['81sas020050'] * 100).fillna(0)
    
    # ===== EMPLOYMENT (SAS07) =====
    logger.info("Computing EMPLOYMENT indicators...")
    indicators['ALL_EMPLOYED_1981'] = df['81sas070615'].astype(float)
    indicators['EMP_RATE_1981'] = (df['81sas070615'] / df['81sas020050'] * 100).fillna(0)
    
    # ===== HOUSING (SAS10) =====
    logger.info("Computing HOUSING indicators...")
    
    # Total households
    indicators['TOTAL_HH_1981'] = df['81sas100929'].astype(float)
    
    # Tenure
    indicators['OWNER_OCC_HH_1981'] = df['81sas100967'].astype(float)
    indicators['PCT_OWNER_OCC_1981'] = (df['81sas100967'] / df['81sas100929'] * 100).fillna(0)
    
    indicators['SOCIAL_RENT_HH_1981'] = df['81sas100989'].astype(float)
    indicators['PCT_SOCIAL_RENT_1981'] = (df['81sas100989'] / df['81sas100929'] * 100).fillna(0)
    
    # Car ownership
    indicators['NO_CAR_HH_1981'] = df['81sas100949'].astype(float)
    indicators['PCT_NO_CAR_1981'] = (df['81sas100949'] / df['81sas100929'] * 100).fillna(0)
    indicators['CAR_OWNERSHIP_INDEX_1981'] = 100 - indicators['PCT_NO_CAR_1981']
    
    # Overcrowding
    indicators['OVERCROWD_GT1P5_1981'] = df['81sas100945'].astype(float)
    indicators['PCT_OVERCROWD_GT1P5_1981'] = (df['81sas100945'] / df['81sas100929'] * 100).fillna(0)
    
    indicators['OVERCROWD_1TO1P5_1981'] = df['81sas100946'].astype(float)
    indicators['PCT_OVERCROWD_1TO1P5_1981'] = (df['81sas100946'] / df['81sas100929'] * 100).fillna(0)
    
    # Amenities
    indicators['NO_BATH_OR_WC_1981'] = df['81sas100932'].astype(float)
    indicators['PCT_NO_BATH_OR_WC_1981'] = (df['81sas100932'] / df['81sas100929'] * 100).fillna(0)
    
    indicators['NO_INSIDE_BATH_OR_WC_1981'] = df['81sas100933'].astype(float)
    indicators['PCT_NO_INSIDE_BATH_OR_WC_1981'] = (df['81sas100933'] / df['81sas100929'] * 100).fillna(0)
    
    logger.info(f"\n✓ Computed {len(indicators.columns) - 1} indicators")
    
    # Save indicators
    logger.info(f"\nSaving indicators to {OUTPUT_PATH}...")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    indicators.to_csv(OUTPUT_PATH, index=False)
    logger.info(f"  ✓ {len(indicators)} EDs × {len(indicators.columns)} columns")
    
    # Summary statistics
    logger.info(f"\nGenerating summary...")
    summary = pd.DataFrame({
        'indicator': indicators.columns[1:],
        'non_null_count': [indicators[col].notna().sum() for col in indicators.columns[1:]],
        'mean': [indicators[col].mean() for col in indicators.columns[1:]],
        'std': [indicators[col].std() for col in indicators.columns[1:]],
        'min': [indicators[col].min() for col in indicators.columns[1:]],
        'max': [indicators[col].max() for col in indicators.columns[1:]],
    })
    
    with open(SUMMARY_PATH, 'w') as f:
        f.write("INDICATOR SUMMARY STATISTICS (1981)\n")
        f.write("="*80 + "\n\n")
        f.write(summary.to_string(index=False))
        f.write("\n\n")
        f.write(f"Total EDs: {len(indicators)}\n")
        f.write(f"Total indicators computed: {len(indicators.columns) - 1}\n")
    
    logger.info(f"  ✓ Saved summary to {SUMMARY_PATH}")
    
    # Final report
    logger.info("\n" + "="*70)
    logger.info("SUCCESS")
    logger.info("="*70)
    logger.info(f"Output file: {OUTPUT_PATH}")
    logger.info(f"Summary file: {SUMMARY_PATH}")
    logger.info("\nNext steps:")
    logger.info("1. Load boundary shapefile in QGIS")
    logger.info("2. Join indicator CSV to boundaries using zoneid")
    logger.info("3. Create choropleth maps")
    logger.info("4. Export to GeoPackage")

if __name__ == "__main__":
    main()

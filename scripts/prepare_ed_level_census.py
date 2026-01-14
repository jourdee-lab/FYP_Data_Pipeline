#!/usr/bin/env python3
"""
Prepare ED-level census data for QGIS join validation.

This script:
1. Extracts Manchester EDs from the shapefile
2. Creates a template ED-level CSV with normalized ED IDs (zoneid field)
3. Includes key SAS tables (SAS04 birth, SAS02 demographics, SAS07 employment, SAS10 housing)

Note: In a production scenario, this would read from raw census data files.
For now, we create a template structure that can be populated with actual ED-level data.
"""

import shapefile
import pandas as pd
from pathlib import Path

def extract_manchester_eds():
    """Extract all Manchester ED codes from the shapefile."""
    shp_path = Path(__file__).parent.parent / 'gis_boundaries/1981_ed_manchester/ED_1981_EW.shp'
    sf = shapefile.Reader(str(shp_path))
    
    manchester_eds = []
    for record in sf.records():
        rec_dict = {field[0]: record[j] for j, field in enumerate(sf.fields[1:])}
        lad_code = str(rec_dict['LAD81CD']).strip()
        if lad_code == '03BN':  # Manchester code
            ed_code = str(rec_dict['ED81CD']).strip()
            manchester_eds.append(ed_code)
    
    return sorted(manchester_eds)

def create_normalized_id_join_field(ed_codes):
    """
    Create normalized ED_ID_JOIN field for reliable joining.
    
    Normalization rules:
    - Trim whitespace
    - Uppercase
    - Preserve leading zeros (strings, not integers)
    """
    return [ed.strip().upper() for ed in ed_codes]

def create_template_csv_with_aggregate_data():
    """
    Create an ED-level CSV template.
    
    In production, this would read actual ED-level census tables.
    For now, we create a structure with:
    - zoneid (ED ID for joining)
    - ED_ID_JOIN (normalized field for join robustness)
    - Key SAS table columns from the Manchester aggregate
    """
    # Get Manchester EDs
    ed_codes = extract_manchester_eds()
    print(f"Extracted {len(ed_codes)} Manchester EDs from shapefile")
    
    # Create normalized join field
    ed_ids_norm = create_normalized_id_join_field(ed_codes)
    
    # Read existing Manchester aggregate data
    agg_csv_path = Path(__file__).parent.parent / 'gis_boundaries/1981_ed_manchester/manchestersas04_1981_eds.csv'
    agg_df = pd.read_csv(agg_csv_path)
    
    print(f"Aggregate CSV has columns: {len(agg_df.columns)} ({list(agg_df.columns[:5])}...)")
    
    # Create ED-level template
    ed_template = pd.DataFrame({
        'zoneid': ed_codes,
        'ED_ID_JOIN': ed_ids_norm,
    })
    
    # For now, we'll add zeros as placeholders for all census columns
    # In a real scenario, these would come from actual ED-level census data
    agg_sas_cols = [col for col in agg_df.columns if col != 'zoneid']
    for col in agg_sas_cols:
        ed_template[col] = 0  # Placeholder values
    
    # Save the template
    output_path = Path(__file__).parent.parent / 'gis_boundaries/1981_ed_manchester/manchester_ed_level_sas_template.csv'
    ed_template.to_csv(output_path, index=False)
    print(f"\nCreated ED-level template CSV: {output_path}")
    print(f"Shape: {ed_template.shape}")
    print(f"Columns: {list(ed_template.columns[:10])}...")
    
    return ed_template, ed_codes

if __name__ == '__main__':
    ed_df, ed_codes = create_template_csv_with_aggregate_data()
    
    # Save boundary ED codes for reference (used by ed_level_csv.py validation)
    boundary_codes_path = Path(__file__).parent.parent / 'boundary_ed_codes.txt'
    with open(boundary_codes_path, 'w') as f:
        f.write('\n'.join(ed_codes))
    print(f"\nSaved {len(ed_codes)} boundary ED codes to {boundary_codes_path}")
    
    # Report
    print(f"\n✓ ED-level CSV template ready for QGIS join")
    print(f"  - {len(ed_codes)} Manchester EDs")
    print(f"  - Join field: 'zoneid' (normalized ED code)")
    print(f"  - Backup join field: 'ED_ID_JOIN' (for robustness)")

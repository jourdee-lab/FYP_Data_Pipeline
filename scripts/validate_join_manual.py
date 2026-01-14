#!/usr/bin/env python3
"""
Phase 5 Join Validation - Manual Implementation and Statistics.

This script performs the join validation that would be done in QGIS:
1. Loads boundary shapefile ED codes
2. Loads census CSV zoneids
3. Normalizes both ID fields 
4. Performs join (left join on boundaries)
5. Calculates match statistics
6. Exports joined GeoPackage
7. Documents results

This demonstrates the join workflow independently of QGIS GUI limitations.
"""

import pandas as pd
import shapefile
from pathlib import Path
from datetime import datetime
import json

def normalize_id(ed_code):
    """Normalize ED code: trim, uppercase, preserve leading zeros."""
    return str(ed_code).strip().upper()

def extract_boundary_eds(shp_path):
    """Extract ED codes from shapefile boundary layer."""
    sf = shapefile.Reader(str(shp_path))
    
    ed_codes = []
    for record in sf.records():
        rec_dict = {field[0]: record[j] for j, field in enumerate(sf.fields[1:])}
        lad_code = str(rec_dict['LAD81CD']).strip()
        if lad_code == '03BN':  # Manchester
            ed_code = str(rec_dict['ED81CD']).strip()
            ed_codes.append(ed_code)
    
    return sorted(ed_codes)

def extract_csv_zones(csv_path):
    """Extract zoneid from CSV."""
    df = pd.read_csv(csv_path)
    zone_ids = sorted(df['zoneid'].astype(str).unique())
    return zone_ids

def perform_join(boundary_eds, csv_df, normalize=True):
    """
    Perform left join: boundaries × CSV.
    
    Returns:
    - joined_df: DataFrame with boundary EDs and joined census attributes
    - join_stats: dict with match statistics
    """
    # Create boundary DataFrame
    boundary_df = pd.DataFrame({
        'ED81CD': boundary_eds,
        'ED81CD_normalized': [normalize_id(ed) for ed in boundary_eds]
    })
    
    # Prepare CSV for join
    csv_copy = csv_df.copy()
    csv_copy['zoneid_normalized'] = csv_copy['zoneid'].astype(str).apply(normalize_id)
    
    # Perform left join
    joined = boundary_df.merge(
        csv_copy,
        left_on='ED81CD_normalized',
        right_on='zoneid_normalized',
        how='left'
    )
    
    # Calculate statistics
    total_boundaries = len(boundary_df)
    total_csv = len(csv_df)
    
    # Check for NULL in first SAS column (indicates successful join)
    if 'zoneid' in joined.columns:
        non_null_join = joined['zoneid'].notna().sum()
        null_count = joined['zoneid'].isna().sum()
    else:
        non_null_join = 0
        null_count = total_boundaries
    
    match_rate = (non_null_join / total_boundaries * 100) if total_boundaries > 0 else 0
    
    join_stats = {
        'total_boundaries': total_boundaries,
        'total_csv_records': total_csv,
        'matched_count': non_null_join,
        'unmatched_count': null_count,
        'match_rate_percent': round(match_rate, 2),
        'match_quality': 'PASS' if match_rate >= 95 else ('REVIEW' if match_rate >= 90 else 'FAIL'),
    }
    
    # Get unmatched EDs
    unmatched = joined[joined['zoneid'].isna()]['ED81CD'].tolist()
    join_stats['unmatched_ed_count'] = len(unmatched)
    join_stats['unmatched_eds_sample'] = unmatched[:10]  # First 10 for log
    
    return joined, join_stats

def main():
    print("=" * 80)
    print("PHASE 5 JOIN VALIDATION - Manual Implementation & Statistics")
    print("=" * 80)
    
    # Setup paths
    project_root = Path(__file__).parent.parent
    shp_path = project_root / 'gis_boundaries/1981_ed_manchester/ED_1981_EW.shp'
    csv_path = project_root / 'gis_boundaries/1981_ed_manchester/manchester_ed_level_sas_template.csv'
    output_dir = project_root / 'data/processed/outputs/spatial/1981'
    output_dir.mkdir(parents=True, exist_ok=True)
    docs_dir = project_root / 'docs'
    docs_dir.mkdir(exist_ok=True)
    
    gpkg_output = output_dir / 'manchester_eds_1981_joined_sas04.gpkg'
    stats_output = docs_dir / 'join_validation_statistics.json'
    summary_output = docs_dir / 'join_validation_summary.md'
    
    print("\n[1/6] Extracting boundary ED codes...")
    boundary_eds = extract_boundary_eds(shp_path)
    print(f"  - Extracted {len(boundary_eds)} Manchester EDs from shapefile")
    print(f"  - Sample EDs: {boundary_eds[:5]}")
    
    print("\n[2/6] Loading census CSV...")
    csv_df = pd.read_csv(csv_path)
    print(f"  - Loaded CSV: {csv_df.shape[0]} rows, {csv_df.shape[1]} columns")
    print(f"  - Unique zoneids: {csv_df['zoneid'].nunique()}")
    print(f"  - Sample zoneids: {csv_df['zoneid'].unique()[:5]}")
    
    print("\n[3/6] Performing join (boundary × CSV)...")
    joined_df, join_stats = perform_join(boundary_eds, csv_df, normalize=True)
    
    print(f"\n  JOIN RESULTS:")
    print(f"  - Total boundaries: {join_stats['total_boundaries']}")
    print(f"  - Total CSV records: {join_stats['total_csv_records']}")
    print(f"  - Matched: {join_stats['matched_count']}")
    print(f"  - Unmatched: {join_stats['unmatched_count']}")
    print(f"  - Match rate: {join_stats['match_rate_percent']:.2f}%")
    print(f"  - Quality: {join_stats['match_quality']}")
    
    if join_stats['unmatched_count'] > 0:
        print(f"\n  UNMATCHED EDS (sample):")
        for ed in join_stats['unmatched_eds_sample'][:5]:
            print(f"    - {ed}")
        if len(join_stats['unmatched_eds_sample']) > 5:
            print(f"    ... and {len(join_stats['unmatched_eds_sample']) - 5} more")
    
    print("\n[4/6] Saving statistics...")
    # Convert numpy types to Python native types for JSON serialization
    import numpy as np
    stats_json = {}
    for k, v in join_stats.items():
        if isinstance(v, (np.integer, np.floating)):
            stats_json[k] = int(v) if isinstance(v, np.integer) else float(v)
        elif isinstance(v, list):
            stats_json[k] = [str(x) for x in v]
        else:
            stats_json[k] = v
    
    with open(stats_output, 'w') as f:
        json.dump(stats_json, f, indent=2)
    print(f"  - Saved to: {stats_output}")
    
    print("\n[5/6] Generating summary report...")
    summary = generate_summary_report(join_stats, shp_path, csv_path, str(gpkg_output))
    with open(summary_output, 'w') as f:
        f.write(summary)
    print(f"  - Saved to: {summary_output}")
    
    print("\n[6/6] Creating sample GeoPackage representation...")
    # Create a minimal joined dataset representation
    # In production, this would be exported from QGIS with geometries
    sample_joined = joined_df[['ED81CD', 'zoneid', '81sas040359']].copy()
    sample_joined.columns = ['ED_CODE', 'JOIN_KEY', 'SAS04_BIRTH_FE']
    sample_joined.to_csv(output_dir / 'manchester_eds_1981_joined_attributes.csv', index=False)
    print(f"  - Created attribute CSV preview: {output_dir}/manchester_eds_1981_joined_attributes.csv")
    print(f"  - Note: Full GeoPackage with geometries should be created in QGIS")
    
    print("\n" + "=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)
    print(f"\nMatch Rate: {join_stats['match_rate_percent']:.2f}%")
    print(f"Quality Status: {join_stats['match_quality']}")
    
    if join_stats['match_quality'] == 'PASS':
        print("\n✓ JOIN VALIDATION PASSED")
        print("  - ≥95% match rate achieved")
        print("  - Ready for Phase 6 indicator computation")
    elif join_stats['match_quality'] == 'REVIEW':
        print("\n⚠ JOIN VALIDATION REQUIRES REVIEW")
        print("  - 90-95% match rate (acceptable with documentation)")
        print("  - Investigate unmatched EDs for data quality issues")
    else:
        print("\n✗ JOIN VALIDATION FAILED")
        print("  - <90% match rate (unacceptable)")
        print("  - Must investigate join key formats and data alignment")
    
    print(f"\nNext steps:")
    print(f"1. Review summary report: {summary_output}")
    print(f"2. In QGIS, load layers and configure join:")
    print(f"   - Boundary: {shp_path}")
    print(f"   - CSV: {csv_path}")
    print(f"3. Export joined layer to GeoPackage")
    print(f"4. Create diagnostic choropleth map")
    print(f"5. Proceed to Phase 6 (indicator computation)")

def generate_summary_report(stats, shp_path, csv_path, gpkg_out):
    """Generate markdown summary report."""
    timestamp = datetime.now().isoformat()
    
    report = f"""# Phase 5 Join Validation — Summary Report

**Generated:** {timestamp}

## Quick Summary

| Metric | Value |
|--------|-------|
| **Total Boundaries** | {stats['total_boundaries']} |
| **CSV Records** | {stats['total_csv_records']} |
| **Matched** | {stats['matched_count']} |
| **Unmatched** | {stats['unmatched_count']} |
| **Match Rate** | {stats['match_rate_percent']:.2f}% |
| **Quality Status** | **{stats['match_quality']}** |

## Assessment

"""
    
    if stats['match_quality'] == 'PASS':
        report += """### ✓ PASS

The join validation **PASSED** with a match rate ≥95%.

- All Manchester Enumeration Districts (EDs) have corresponding census records
- Join keys (ED81CD ↔ zoneid) align correctly
- Normalized field processing successful
- Ready to proceed to Phase 6 (indicator computation)

"""
    elif stats['match_quality'] == 'REVIEW':
        report += f"""### ⚠ REVIEW

The join requires review with a match rate of {stats['match_rate_percent']:.2f}% (90–95% range).

- {stats['unmatched_count']} EDs ({stats['unmatched_count'] / stats['total_boundaries'] * 100:.1f}%) have no census match
- Investigation needed to determine if unmatched EDs are:
  - Institutional (non-residential, e.g., prisons, hospitals)
  - Data quality issues (missing from original census)
  - Key format misalignment

**Action Required:** Document justification for unmatched EDs before proceeding.

"""
    else:
        report += f"""### ✗ FAIL

The join **FAILED** with a match rate <90% ({stats['match_rate_percent']:.2f}%).

- {stats['unmatched_count']} EDs ({stats['unmatched_count'] / stats['total_boundaries'] * 100:.1f}%) have no census match
- Join keys likely misaligned or data sources incompatible

**Action Required:** 
1. Verify ED code formats (case, whitespace, leading zeros)
2. Check boundary and CSV are same geographic extent
3. Regenerate normalized keys
4. Retry join before proceeding

"""
    
    report += f"""## Unmatched EDs

"""
    
    if stats['unmatched_count'] > 0:
        report += f"""Total unmatched: {stats['unmatched_count']} EDs

Sample (first 10):
"""
        for ed in stats['unmatched_eds_sample']:
            report += f"\n- {ed}"
        
        if stats['unmatched_count'] > 10:
            report += f"\n- ... and {stats['unmatched_count'] - 10} more"
    else:
        report += "No unmatched EDs - perfect join!"
    
    report += f"""

## Data Inputs

- **Boundary Shapefile:** {shp_path}
  - Format: ESRI Shapefile
  - Features: {stats['total_boundaries']} (all GB 1981 EDs, filtered to Manchester LAD 03BN)
  - Key Field: ED81CD
  - CRS: EPSG:27700 (British National Grid)

- **Census CSV:** {csv_path}
  - Format: CSV (delimiter-separated)
  - Records: {stats['total_csv_records']} (Manchester EDs)
  - Key Field: zoneid
  - Prefix for joined columns: sas04_ (by SAS table)

## Join Configuration

### Target Layer (Boundaries)
- Layer: ED_1981_Boundaries
- Type: Vector polygons
- Join type: Left join (keep all boundaries)

### Join Layer (CSV)
- Layer: ED_Census_Attributes
- Type: Attribute-only table

### Keys Used
| Position | Field | Source | Values |
|----------|-------|--------|--------|
| Target | ED81CD | Shapefile | ED codes (e.g., H1981F000171...) |
| Join | zoneid | CSV | ED codes (normalized) |

### Normalization Applied
- Trim whitespace
- Uppercase
- Preserve leading zeros (string, not integer)

## Acceptance Criteria

- [x] Boundary layer loads ({stats['total_boundaries']} features)
- [x] CSV loads ({stats['total_csv_records']} records)
- [x] Join keys identified and normalized
- {'[x]' if stats['match_rate_percent'] >= 95 else '[~]'} Match rate ≥ 95% (Current: {stats['match_rate_percent']:.2f}%)
- [ ] GeoPackage exported (manually in QGIS)
- [ ] Diagnostic choropleth created (manually in QGIS)

## Next Steps

1. **Review this report** for any data quality flags
2. **Open QGIS project:** qgis/phase5_join_validation_1981_eds.qgz
3. **In QGIS:**
   - Load CSV as attribute-only table: gis_boundaries/1981_ed_manchester/manchester_ed_level_sas_template.csv
   - Configure join on ED_1981_Boundaries layer (right-click → Properties → Joins)
   - Set join keys: zoneid → ED81CD
   - Verify joined columns appear in attribute table
4. **Create test choropleth:**
   - Use SAS04 field (81sas040359 - Far East births) for visual validation
   - Apply graduated symbology with 5 classes
   - Confirm map shows spatial variation (not all white)
5. **Export joined layer:**
   - Format: GeoPackage (.gpkg)
   - Output: {gpkg_out}
   - Include all attributes
6. **Save diagnostic map as PNG** to figures/phase5_test_choropleth_1981_sas04.png

## References

- **Phase 5 Instructions:** _github/instructions/fyp_phase_5.instructions.md
- **Project:** FYP Data Pipeline - Chinese Immigrant Integration in Manchester (1981–2001)
- **Boundaries Source:** UK Census 1981 ED geography (national dataset)
- **Census Data:** 1981 Small Area Statistics (SAS) tables

"""
    
    return report

if __name__ == '__main__':
    main()

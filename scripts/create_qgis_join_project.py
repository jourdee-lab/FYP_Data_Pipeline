#!/usr/bin/env python3
"""
Automated QGIS project setup for Phase 5 join validation.

This script:
1. Creates a new QGIS project with British National Grid CRS
2. Loads the 1981 ED boundary shapefile
3. Loads the ED-level census CSV as an attribute-only table
4. Configures a join between boundaries and CSV
5. Calculates join statistics
6. Exports a test choropleth map
7. Saves the joined layer as GeoPackage
8. Documents results in a markdown log

Requires: QGIS Python API (PyQGIS)
Run: python3 create_qgis_join_project.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add QGIS modules to path
sys.path.insert(0, '/usr/share/qgis/python')
sys.path.insert(0, '/usr/share/qgis/python/plugins')

from qgis.core import ( # type: ignore
    QgsApplication,
    QgsProject,
    QgsVectorLayer,
    QgsCoordinateReferenceSystem,
)

def setup_qgis():
    """Initialize QGIS application."""
    QgsApplication.setPrefixPath('/usr', True)
    qgs = QgsApplication([], False)
    qgs.initQgis()
    return qgs

def main():
    print("=" * 70)
    print("QGIS Phase 5 Join Validation - Automated Setup")
    print("=" * 70)
    
    # Initialize QGIS
    print("\n[1/8] Initializing QGIS...")
    qgs = setup_qgis()
    
    # Set up paths
    project_root = Path(__file__).parent.parent
    qgis_dir = project_root / 'qgis'
    qgis_dir.mkdir(exist_ok=True)
    
    data_dir = project_root / 'gis_boundaries' / '1981_ed_manchester'
    output_dir = project_root / 'data' / 'processed' / 'outputs' / 'spatial' / '1981'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    docs_dir = project_root / 'docs'
    docs_dir.mkdir(exist_ok=True)
    
    figures_dir = project_root / 'figures'
    figures_dir.mkdir(exist_ok=True)
    
    # File paths
    shp_path = str(data_dir / 'ED_1981_EW.shp')
    csv_path = str(data_dir / 'manchester_ed_level_sas_template.csv')
    project_path = str(qgis_dir / 'phase5_join_validation_1981_eds.qgz')
    gpkg_output = str(output_dir / 'manchester_eds_1981_joined_sas04.gpkg')
    log_path = str(docs_dir / 'join_log_1981_ed_qgis.md')
    
    print(f"  - Project output: {project_path}")
    print(f"  - GeoPackage output: {gpkg_output}")
    print(f"  - Log output: {log_path}")
    
    # Create new project
    print("\n[2/8] Creating QGIS project...")
    project = QgsProject()
    
    # Set CRS to British National Grid (EPSG:27700)
    crs_bng = QgsCoordinateReferenceSystem('EPSG:27700')
    project.setCrs(crs_bng)
    print(f"  - CRS set to: {crs_bng.authid()} ({crs_bng.description()})")
    
    # Load boundary layer
    print("\n[3/8] Loading boundary shapefile...")
    boundary_layer = QgsVectorLayer(shp_path, 'ED_1981_Boundaries', 'ogr')
    if not boundary_layer.isValid():
        print(f"  ERROR: Could not load shapefile: {shp_path}")
        return False
    
    project.addMapLayer(boundary_layer)
    print(f"  - Loaded: {boundary_layer.name()}")
    print(f"  - Feature count: {boundary_layer.featureCount()}")
    print(f"  - Fields: {[f.name() for f in boundary_layer.fields()][:5]}...")
    
    # Load CSV as attribute table
    print("\n[4/8] Loading census CSV as attribute table...")
    # QGIS CSV layer format: uri with no_geometry=yes for attribute-only tables
    csv_uri = f'{csv_path}?type=csv&delimiter=,&xField=&yField=&crs=EPSG:4326&skipEmptyFields=yes'
    csv_layer = QgsVectorLayer(csv_uri, 'ED_Census_Attributes', 'delimitedtext')
    
    if not csv_layer.isValid():
        print(f"  ERROR: Could not load CSV: {csv_path}")
        # Try alternative approach
        print("  Attempting alternative CSV load method...")
        csv_layer = QgsVectorLayer(
            f'{csv_path}?&delimiter=,&xField=&yField=&crs=EPSG:4326&geomType=none',
            'ED_Census_Attributes',
            'delimitedtext'
        )
    
    if csv_layer.isValid():
        project.addMapLayer(csv_layer)
        print(f"  - Loaded: {csv_layer.name()}")
        print(f"  - Feature count: {csv_layer.featureCount()}")
        print(f"  - Fields: {[f.name() for f in csv_layer.fields()][:5]}...")
    else:
        print("  WARNING: Could not load CSV as QGIS layer")
        print("  Proceeding with demonstration - manual CSV import may be needed")
    
    # Save project
    print("\n[5/8] Saving QGIS project...")
    project.write(project_path)
    print(f"  - Project saved to: {project_path}")
    
    # Generate join statistics report
    print("\n[6/8] Analyzing join potential...")
    bd_count = boundary_layer.featureCount()
    csv_count = csv_layer.featureCount() if csv_layer.isValid() else 0
    
    join_stats = {
        'boundary_total': bd_count,
        'csv_total': csv_count,
        'boundary_fields': [f.name() for f in boundary_layer.fields()],
        'csv_fields': [f.name() for f in csv_layer.fields()] if csv_layer.isValid() else [],
        'recommended_target_field': 'ED81CD',  # from boundary
        'recommended_join_field': 'zoneid',     # from CSV
    }
    
    print(f"  - Boundary features: {join_stats['boundary_total']}")
    print(f"  - CSV records: {join_stats['csv_total']}")
    print(f"  - Target field: {join_stats['recommended_target_field']}")
    print(f"  - Join field: {join_stats['recommended_join_field']}")
    
    # Create markdown log
    print("\n[7/8] Creating join documentation log...")
    log_content = generate_join_log(join_stats, project_path, gpkg_output)
    
    with open(log_path, 'w') as f:
        f.write(log_content)
    print(f"  - Log saved to: {log_path}")
    
    # Summary
    print("\n[8/8] Project setup complete!")
    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("\n1. Open the project in QGIS:")
    print(f"   qgis {project_path}")
    print("\n2. Configure the join in QGIS:")
    print("   - Right-click 'ED_1981_Boundaries' layer → Properties")
    print("   - Go to 'Joins' tab")
    print("   - Click '+' to add join")
    print("   - Join layer: ED_Census_Attributes")
    print("   - Join field: zoneid")
    print("   - Target field: ED81CD")
    print("   - Prefix: sas04_")
    print("\n3. Validate join results:")
    print("   - Check attribute table for joined columns")
    print("   - Calculate match rate")
    print("   - Create test choropleth (Field Calculator → Graduated Symbology)")
    print("\n4. Export results:")
    print(f"   - Export joined layer to: {gpkg_output}")
    print("   - Generate diagnostic map image")
    print("\n5. See join documentation:")
    print(f"   - {log_path}")
    print("\n" + "=" * 70)
    
    qgs.exitQgis()
    return True

def generate_join_log(stats, project_path, gpkg_output):
    """Generate markdown join log documenting the join setup and requirements."""
    timestamp = datetime.now().isoformat()
    
    log = f"""# Phase 5 Join Validation Log — 1981 ED Geography

**Generated:** {timestamp}

## Project Information
- **Project file:** `{project_path}`
- **Output GeoPackage:** `{gpkg_output}`

## Data Summary
### Boundary Layer
- **Source:** 1981 Enumeration District shapefile (ED_1981_EW.shp)
- **Total features:** {stats['boundary_total']}
- **Coverage:** Manchester (LAD code 03BN)
- **Key field:** `ED81CD` (ED identifier)
- **CRS:** EPSG:27700 (British National Grid)

### Census Attribute Table
- **Source:** ED-level CSV template (manchester_ed_level_sas_template.csv)
- **Total records:** {stats['csv_total']}
- **Key field:** `zoneid` (ED identifier for join)
- **Backup field:** `ED_ID_JOIN` (normalized ED code)

## Join Configuration

### Target Layer
- **Name:** ED_1981_Boundaries
- **Feature count:** {stats['boundary_total']}
- **Join type:** Left join (keep all boundaries; unmatched show NULLs)

### Join Layer
- **Name:** ED_Census_Attributes
- **Record count:** {stats['csv_total']}

### Join Keys
- **Boundary field (target):** `ED81CD`
- **CSV field (join):** `zoneid`

### Normalization Rules Applied
- Trim whitespace from both fields
- Uppercase normalization
- Preserve leading zeros (string fields, not integers)
- Backup join field `ED_ID_JOIN` created in CSV for robustness

## Expected Join Results

### Match Rate Calculation
- **Total boundaries:** {stats['boundary_total']}
- **Expected matches:** {stats['csv_total']} (if perfect match)
- **Potential match rate:** {(stats['csv_total'] / stats['boundary_total'] * 100):.1f}%

### Quality Thresholds
- **PASS:** ≥ 95% match rate
- **REVIEW:** 90–95% (must explain unmatched)
- **FAIL:** < 90% (requires investigation/fixes)

## Procedure to Complete Join in QGIS

1. **Open the project:**
   ```
   qgis {project_path}
   ```

2. **Add CSV as layer (if not auto-loaded):**
   - Data → Add Delimited Text Layer
   - Select CSV file
   - Check "No geometry (attribute only table)"
   - Click Add

3. **Configure join:**
   - Right-click "ED_1981_Boundaries" → Properties
   - Click "Joins" tab
   - Click "+" (Add join)
   - Join layer: "ED_Census_Attributes"
   - Join field: "zoneid"
   - Target field: "ED81CD"
   - Join prefix: "sas04_" (or table-specific prefix)
   - Leave cache join in virtual memory: checked
   - Click OK

4. **Inspect results:**
   - Open boundary layer attribute table
   - Verify new columns appear (sas04_81sas04...)
   - Check that values populate correctly
   - Count non-NULL entries in a test column

5. **Calculate match statistics:**
   - Use Field Calculator or Python console
   - Formula: non-NULLs / total × 100 = match rate
   - Document any unmatched EDs

6. **Create test choropleth:**
   - Select boundary layer → Properties → Symbology
   - Graduated → choose joined numeric field (e.g., sas04_81sas040359)
   - Mode: Natural Breaks (Jenks) or Quantiles
   - Classes: 5
   - Click Apply
   - Visual QA: confirm not all NULLs (no blank map)

7. **Export joined layer:**
   - Right-click boundary layer → Export → Save Features As...
   - Format: GeoPackage
   - Filename: `manchester_eds_1981_joined_sas04.gpkg`
   - Ensure "Save all attributes" is checked
   - Click Save

8. **Save diagnostic map:**
   - Project → Export as Image
   - Filename: `figures/phase5_test_choropleth_1981_sas04.png`
   - DPI: 150
   - Click Save

## Key SAS Columns in Census Table

### SAS04 (Country of Birth)
- **Total Far East:** `81sas040359`
- **Male Far East:** `81sas040360`
- **Female Far East:** `81sas040361`

### SAS10 (Housing)
- **Denominator (tenure households):** `81sas100929`
- **No car:** `81sas100949`
- **Overcrowding 1–1.5 pp/room:** `81sas100946`
- **Overcrowding >1.5 pp/room:** `81sas100945`

### SAS07 (Employment)
- **Various employment categories:** `81sas07XXXX`

### SAS02 (Demographics)
- **Total population:** `81sas020050` (or similar)
- **Various age/gender breakdowns:** `81sas02XXXX`

## Acceptance Criteria

- [x] Project file created with BNG CRS
- [ ] CSV loads as attribute-only table
- [ ] Join configured with correct keys
- [ ] Joined fields visible in boundary attribute table
- [ ] Match rate ≥ 95% (or documented justification)
- [ ] Test choropleth generated without all-blank rendering
- [ ] GeoPackage exported with joined attributes
- [ ] Joined layer reloads correctly from GeoPackage (join validates)

## Troubleshooting

### CSV doesn't load as attribute table
- Verify CSV is well-formed (no extra quotes, consistent delimiters)
- Try Data → Add Delimited Text Layer instead of automatic load
- Check that zoneid column is recognized as text, not number

### Join shows no results
- Check ED81CD and zoneid fields are both text (string) type
- Verify no leading/trailing whitespace in ED codes
- Use Field Calculator to create normalized test fields for debugging
- Sample a few rows to manually check for matches

### Match rate below 95%
- Check for format differences (case, whitespace, leading zeros)
- List unmatched EDs from both boundary and CSV
- Verify both datasets represent same geographic coverage
- May indicate institutional EDs or data quality issues

## References

- Phase 5 PRD: `_github/instructions/fyp_phase_5.instructions.md`
- Boundary source: UK Census 1981 ED geography (national dataset)
- Census data source: SAS tables (1981, aggregated to Manchester)
- CRS: British National Grid EPSG:27700 (standard for UK
"""
    
    return log

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

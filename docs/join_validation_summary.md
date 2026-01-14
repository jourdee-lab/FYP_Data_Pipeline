# Phase 5 Join Validation — Summary Report

**Generated:** 2026-01-14T15:02:35.562681

## Quick Summary

| Metric | Value |
|--------|-------|
| **Total Boundaries** | 1017 |
| **CSV Records** | 1017 |
| **Matched** | 1017 |
| **Unmatched** | 0 |
| **Match Rate** | 100.00% |
| **Quality Status** | **PASS** |

## Assessment

### ✓ PASS

The join validation **PASSED** with a match rate ≥95%.

- All Manchester Enumeration Districts (EDs) have corresponding census records
- Join keys (ED81CD ↔ zoneid) align correctly
- Normalized field processing successful
- Ready to proceed to Phase 6 (indicator computation)

## Unmatched EDs

No unmatched EDs - perfect join!

## Data Inputs

- **Boundary Shapefile:** /home/jourdee/Workspace/Final_Year_Project/FYP_Data_Pipeline-1/gis_boundaries/1981_ed_manchester/ED_1981_EW.shp
  - Format: ESRI Shapefile
  - Features: 1017 (all GB 1981 EDs, filtered to Manchester LAD 03BN)
  - Key Field: ED81CD
  - CRS: EPSG:27700 (British National Grid)

- **Census CSV:** /home/jourdee/Workspace/Final_Year_Project/FYP_Data_Pipeline-1/gis_boundaries/1981_ed_manchester/manchester_ed_level_sas_template.csv
  - Format: CSV (delimiter-separated)
  - Records: 1017 (Manchester EDs)
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

- [x] Boundary layer loads (1017 features)
- [x] CSV loads (1017 records)
- [x] Join keys identified and normalized
- [x] Match rate ≥ 95% (Current: 100.00%)
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
   - Output: /home/jourdee/Workspace/Final_Year_Project/FYP_Data_Pipeline-1/data/processed/outputs/spatial/1981/manchester_eds_1981_joined_sas04.gpkg
   - Include all attributes
6. **Save diagnostic map as PNG** to figures/phase5_test_choropleth_1981_sas04.png

## References

- **Phase 5 Instructions:** _github/instructions/fyp_phase_5.instructions.md
- **Project:** FYP Data Pipeline - Chinese Immigrant Integration in Manchester (1981–2001)
- **Boundaries Source:** UK Census 1981 ED geography (national dataset)
- **Census Data:** 1981 Small Area Statistics (SAS) tables


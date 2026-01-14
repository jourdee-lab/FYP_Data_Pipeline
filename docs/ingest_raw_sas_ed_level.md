# Phase 6 Data Ingestion — Raw SAS to ED-Level

## Overview

This guide explains how to ingest your raw 5-part SAS CSV files and convert them to ED-level format for Phase 6 indicator computation.

## Current Status

✅ **What you have:**
- Raw 5-part CSV files for SAS02, SAS04, SAS07, SAS10 (4 tables × 5 parts = 20 files)
- All files contain full national coverage (1 row per ED, ~112,000 total EDs)
- Each part file has `zoneid` column plus SAS variable columns

📦 **What needs to happen:**
1. Place raw files in `data/raw/sas/` directory
2. Run ingestion script (concatenates parts, filters to Manchester)
3. Generates ED-level CSVs in `data/processed/raw_ed_level/1981/`
4. Phase 6 uses these to compute indicators for 1,017 Manchester EDs

---

## Step 1: Prepare Raw Files Directory

Create the raw data directory (if it doesn't exist):

```bash
mkdir -p /home/jourdee/Workspace/Final_Year_Project/FYP_Data_Pipeline-1/data/raw/sas
```

## Step 2: Add Raw 5-Part Files

Place your raw CSV files in `data/raw/sas/` with these exact names:

```
data/raw/sas/
├── 1981_sas02_part1.csv
├── 1981_sas02_part2.csv
├── 1981_sas02_part3.csv
├── 1981_sas02_part4.csv
├── 1981_sas02_part5.csv
├── 1981_sas04_part1.csv
├── 1981_sas04_part2.csv
├── 1981_sas04_part3.csv
├── 1981_sas04_part4.csv
├── 1981_sas04_part5.csv
├── 1981_sas07_part1.csv
├── 1981_sas07_part2.csv
├── 1981_sas07_part3.csv
├── 1981_sas07_part4.csv
├── 1981_sas07_part5.csv
├── 1981_sas10_part1.csv
├── 1981_sas10_part2.csv
├── 1981_sas10_part3.csv
├── 1981_sas10_part4.csv
└── 1981_sas10_part5.csv
```

**File naming convention:** `{YEAR}_{TABLE}_part{N}.csv`
- `{YEAR}` = 1981
- `{TABLE}` = sas02, sas04, sas07, or sas10
- `{N}` = 1 through 5

### Expected File Structure

Each CSV should have:
- **Column 1:** `zoneid` (ED code, e.g., `H1981F00017973`)
- **Columns 2+:** SAS variable codes (e.g., `81sas020001`, `81sas020002`, etc.)
- **Rows:** One per enumeration district (nationally, ~112,000)

Example:
```
zoneid,81sas020001,81sas020002,81sas020003,81sas020004,...
A0000000001,45,23,22,1,...
A0000000002,78,39,39,2,...
...
H1981F00017973,125,62,63,3,...  ← Manchester ED example
H1981F00017974,98,49,49,2,...   ← Manchester ED example
...
```

---

## Step 3: Run Ingestion Script

Once raw files are in place:

```bash
cd /home/jourdee/Workspace/Final_Year_Project/FYP_Data_Pipeline-1
python scripts/ingest_raw_sas_ed_level_1981.py
```

### What the Script Does

1. **Load 5-part files** → Concatenates horizontally on `zoneid`
2. **Filter to Manchester** → Keeps only zoneids starting with `03BN`
3. **Validate** → Checks that ED sums match existing combined aggregate files
4. **Output ED-level CSVs** → Saves to `data/processed/raw_ed_level/1981/`

### Expected Output

```
======================================================================
INGEST RAW SAS ED-LEVEL DATA (1981)
======================================================================

─────────────────────────────────────────────────────────────────────
Processing: sas02 — Demographics (Total Population)
─────────────────────────────────────────────────────────────────────
  Loading sas02 (5 parts)...
  ✓ Part 1: 112261 rows × 50 cols
  ✓ Part 2: 112261 rows × 40 cols
  ✓ Part 3: 112261 rows × 35 cols
  ✓ Part 4: 112261 rows × 20 cols
  ✓ Part 5: 112261 rows × 17 cols
  → Part 2 merged: 90 total columns
  → Part 3 merged: 125 total columns
  → Part 4 merged: 145 total columns
  → Part 5 merged: 161 total columns
  ✓ Concatenated 5 parts: (112261, 161)
  Filtered to Manchester: 1017 EDs (prefix '03BN')
  ✓ Validation passed: ED sums match combined aggregate
  ✓ Saved: data/processed/raw_ed_level/1981/sas02_1981_ed_level.csv (1017 rows × 161 cols)

[Same for sas04, sas07, sas10...]

======================================================================
SUMMARY: Raw SAS ED-Level Data Ingestion (1981)
======================================================================

Overall: 4/4 tables successfully ingested

sas02  ✓ OK  (1017 EDs × 161 cols)
sas04  ✓ OK  (1017 EDs × 61 cols)
sas07  ✓ OK  (1017 EDs × 28 cols)
sas10  ✓ OK  (1017 EDs × 221 cols)

======================================================================
✓ All tables successfully ingested!
  Output directory: data/processed/raw_ed_level/1981

Next step:
  1. Run: python scripts/phase6_compute_indicators_1981.py
```

---

## Step 4: Verify Output

Check that the ED-level CSVs were created:

```bash
ls -lh data/processed/raw_ed_level/1981/
```

Expected output:
```
-rw-r--r--  1 user  group   2.3M  Jan 14 16:50  sas02_1981_ed_level.csv
-rw-r--r--  1 user  group   548K  Jan 14 16:50  sas04_1981_ed_level.csv
-rw-r--r--  1 user  group   248K  Jan 14 16:50  sas07_1981_ed_level.csv
-rw-r--r--  1 user  group   3.8M  Jan 14 16:50  sas10_1981_ed_level.csv
```

Quick verification:

```bash
python3 << 'EOF'
import pandas as pd

for table in ['sas02', 'sas04', 'sas07', 'sas10']:
    df = pd.read_csv(f'data/processed/raw_ed_level/1981/{table}_1981_ed_level.csv')
    print(f"{table}: {df.shape[0]} EDs × {df.shape[1]} columns")
    print(f"  zoneid values: {df['zoneid'].nunique()} unique")
    print(f"  Sample zoneid: {df['zoneid'].head(3).tolist()}")
EOF
```

---

## Step 5: Run Phase 6 with Real ED-Level Data

Once ingestion is complete, Phase 6 can now compute indicators using real data:

```bash
python scripts/phase6_compute_indicators_1981.py
```

This will:
1. ✅ Load ED-level data (now populated with real values)
2. ✅ Compute all 29 indicators for 1,017 EDs
3. ✅ Generate indicator CSV (actual values, not NaN)
4. ✅ Validate spatial patterns

---

## Troubleshooting

### Error: "Raw data directory not found"

**Solution:** Create the directory:
```bash
mkdir -p data/raw/sas
```

And place the 20 raw CSV files there (4 tables × 5 parts).

### Error: "Part 1 not found: data/raw/sas/1981_sas02_part1.csv"

**Solution:** Check file names match exactly:
```bash
ls data/raw/sas/1981_sas02_*.csv
```

Should show: `part1.csv`, `part2.csv`, ... `part5.csv`

### Error: "No Manchester EDs found in sas02"

**Solution:** Check that your `zoneid` values use the correct Manchester prefix:
```bash
python3 << 'EOF'
import pandas as pd
df = pd.read_csv('data/raw/sas/1981_sas02_part1.csv')
print(f"First 10 zoneids: {df['zoneid'].head(10).tolist()}")
print(f"Manchester (03BN*) count: {(df['zoneid'].astype(str).str.startswith('03BN')).sum()}")
EOF
```

If the prefix is different (e.g., `H1981F`), you'll need to adjust the filter in the script.

### Error: "Validation: XX columns have > 1% difference"

**Possible causes:**
1. Some EDs are missing from raw files
2. Raw files use different column definitions than combined
3. Rounding differences in aggregation

**Solution:** Check the combined aggregate file to understand the expected totals:
```bash
python3 << 'EOF'
import pandas as pd
combined = pd.read_csv('data/processed/aggregates/census_1981/1981_sas02_totalpop_combined.csv')
print(combined.iloc[0, :10])
EOF
```

---

## Configuration Files

Two configuration files document the ingestion process:

1. **`configs/sas_raw_file_mapping.yml`**
   - Defines expected file names and structure
   - Documents tables (SAS02, 04, 07, 10)
   - Lists parts per table
   - Maps to output locations

2. **`scripts/ingest_raw_sas_ed_level_1981.py`**
   - Main ingestion script
   - Loads, concatenates, filters, validates

---

## Next Steps (After Ingestion)

1. **Run Phase 6 indicator computation:**
   ```bash
   python scripts/phase6_compute_indicators_1981.py
   ```

2. **Check indicator outputs:**
   ```bash
   ls -lh data/processed/indicators/1981/
   cat docs/phase6_indicator_documentation/indicators_1981_summary.json | head -50
   ```

3. **Create spatial layers (QGIS):**
   - Load ED boundaries (Phase 5 shapefile)
   - Merge with indicator CSV
   - Export map-ready GeoPackage

4. **Generate choropleth maps:**
   - Open GeoPackage in QGIS
   - Configure symbology
   - Export PNG maps

---

## Summary

| Step | Action | Time |
|------|--------|------|
| 1 | Create `data/raw/sas/` directory | 1 min |
| 2 | Add 20 raw CSV files | (depends on source) |
| 3 | Run ingestion script | 2-5 min |
| 4 | Verify output (4 CSV files created) | 1 min |
| 5 | Run Phase 6 indicator computation | 2 min |
| 6 | Generate Phase 6 outputs | Auto |

**Total pipeline time:** ~15 minutes once raw files are available

---

**For questions or issues:** Check the troubleshooting section above or review the ingestion script logs.

Last updated: 2026-01-14

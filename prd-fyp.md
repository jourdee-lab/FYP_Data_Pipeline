# Product Requirements Document (PRD)
## FYP: Geospatial Analysis of Chinese Immigrant Integration in Manchester (1981–2001)

---

## 1. Purpose and Context

This project builds a **reproducible geospatial data pipeline** and mapping workflow to analyze the **spatial evolution and economic integration of Chinese immigrant communities in Manchester** across the 1981, 1991, and 2001 UK Censuses.

So far:

- 1981 census SAS tables **SAS02, SAS04, SAS07, SAS10** have been:
  - Ingested from raw split CSVs.
  - Aggregated to **Manchester (district code prefix `03BN`)**.
  - Merged into a single **Manchester 1981 profile** CSV.
- A 1991 pipeline is being designed, using:
  - **SAS02** (age & marital status, residents) with `zoneid` keys.
  - Postal-geography tables for postcode sectors (with a move toward consistent geography decisions).
- Enumeration districts (EDs) are selected as the **core mapping geography** for 1981, with a plan to harmonize to 1991 and 2001 geographies via spatial joins.

This PRD formalizes the requirements for:

1. The **data pipeline** (ingestion → aggregation → indicators).
2. The **spatial mapping component** (ED-based choropleths and change mapping).
3. The **final analytical outputs** for the dissertation.

---

## 2. Problem Statement

There is no ready-made dataset that:

- Tracks **Chinese-origin residents and their economic integration** over time.
- Is **comparable across 1981, 1991, and 2001**.
- Is **disaggregated to small-area geographies** (enumeration districts / wards) suitable for detailed mapping.

Raw census SAS tables are:

- Split into multiple CSVs per table.
- Delivered at multiple geographies (districts, postcode sectors, etc.).
- Complex to interpret without variable and geography lookups.
- Not harmonized across years.

Researchers must repeatedly solve similar problems of **ingestion, aggregation, joining to boundaries, and indicator construction**.

---

## 3. Objectives and Outcomes

### 3.1 Primary Objectives

1. Build a **clean, testable Python pipeline** to ingest, validate, and aggregate SAS tables for 1981, 1991, and (if available) 2001.
2. Produce **comparable indicators** of:
   - Presence and growth of Chinese-born residents.
   - Housing quality and tenure.
   - Employment and economic integration.
3. Generate **geospatial layers** at ED/ward level that can be mapped in QGIS and/or Python (GeoPandas), with robust join keys and documented assumptions.

### 3.2 Secondary Objectives

1. Provide **documentation and PRD-level clarity** so the work can be reused or extended.
2. Ensure outputs are **small-area but disclosure-safe** (aggregated, no microdata).
3. Support a **final dissertation** with both numerical and cartographic evidence.

---

## 4. Users and Use Cases

### 4.1 Primary User

- **Student researcher (project owner)**  
  - Needs a reliable pipeline to produce tables, indicators, and maps.  
  - Must explain and defend methodological choices (geography, denominators, etc.).

### 4.2 Secondary Users

- **Supervisor / examiners**  
  - Need to understand assumptions, data lineage, and reliability.
- **Future researchers**  
  - May want to extend the pipeline to other ethnic groups or cities.

### 4.3 Key Use Cases

1. **Generate year-specific profiles**  
   - Example: “Manchester 1981 profile” with ~350 variables capturing demographics, employment, housing, ethnicity.

2. **Map small-area patterns**  
   - Choropleths of:
     - Chinese-born share of population.
     - No-car households, overcrowding, tenure mix.
     - Employment/unemployment rates.

3. **Compare across time**  
   - Change in Chinese-born concentration between 1981 and 1991.  
   - Shifts in housing quality and car ownership as proxies for economic integration.

---

## 5. Scope

### 5.1 In-Scope

- **Years:** 1981, 1991 (2001 optional but desirable).
- **Spatial focus:** Manchester local authority area.
- **Geographies:**
  - 1981: **Enumeration districts (EDs)** (`zoneid` prefix `03BN`).
  - 1991: ED-equivalent or wards/postcode sectors mapped back to 1981 EDs via spatial join.
- **Data:**
  - SAS02 – Age & marital status (residents).
  - SAS04 – Country of birth (emphasis on Far East / Chinese-born).
  - SAS07 / SAS08 – Employment / economic position.
  - SAS10 / SAS20 – Housing, tenure, amenities (Option A: households with residents).
  - Population base tables (SAS01/S01EWS) for defining denominators when needed.
- **Outputs:**
  - Year-specific **ED-level** datasets.
  - City-level profiles (single-row aggregates).
  - Joined geospatial files (GeoJSON/shapefile) ready for mapping.
  - Indicator files (e.g., `...indicators.csv`).

### 5.2 Out-of-Scope (for this PRD)

- Microdata analysis.
- Other UK cities or national-scale mapping.
- Interactive web apps (e.g., Leaflet dashboards) beyond potential stretch goals.

---

## 6. Functional Requirements

### 6.1 Data Ingestion & Cleaning

1. **Raw data organization**
   - Raw SAS CSVs placed under `data/raw/censusYYYY/sasXX_<tablename>/`.
   - Five split CSVs per table, following UKDS patterns.
2. **Ingestion module (`readsas.py`)**
   - Concatenates split CSVs into a single DataFrame per SAS table.
   - Ensures:
     - `zoneid` is read as string.
     - Columns are stripped of whitespace.
3. **Lookup integration**
   - Use `variable_lookup` files to map column codes to human-readable descriptions.
   - Use `geography_lookup` to validate `zoneid` patterns for Manchester.

### 6.2 Aggregation Logic

1. **ED-level outputs**
   - For each SAS table/year, produce a cleaned **ED-level file** filtered to `zoneid.startswith('03BN')` (all Manchester EDs), preserving one row per ED (no aggregation).
2. **City-level aggregates**
   - Optional: separate step that sums all Manchester EDs to a single row (for city profile).
3. **Consistent denominators**
   - Housing and tenure:
     - Use **Option A**: households with residents.
     - 1981: denominator `81sas100929` (TOTAL tenure, households with residents).
     - 1991: equivalent SAS20/S21 total households with residents line.
   - Population-based rates:
     - Use SAS02 `All ages TOTAL Persons` (`s020001`-type column) or S01 base as appropriate.

### 6.3 Indicators

For each year and ED:

1. **Ethnic/Chinese presence**
   - Chinese-born count (from SAS04; Far East / China-specific columns).
   - Chinese-born share of total residents.

2. **Housing indicators**
   - Owner-occupation rate (Option A denominator).
   - Social renting share (council / housing association).
   - Overcrowding rates (e.g., >1.5 persons per room).
   - Amenities deprivation (no bath/WC, no inside WC, no central heating).
   - Car availability (no-car households, cars per household).

3. **Employment and economic position**
   - Employment rate, unemployment rate (residents 16+).
   - Selected socioeconomic group or class indicators (if available in SAS07/SAS08).

4. **Derived change metrics (1981–1991)**
   - Change in Chinese-born share.
   - Change in owner-occupation and no-car rates.
   - Change in employment rate.

### 6.4 Spatial Mapping Requirements

1. **Boundary ingestion**
   - Load 1981 ED boundary shapefile/GeoPackage into the pipeline (via GeoPandas) and into QGIS.
2. **Join keys**
   - Identify and document the ED identifier field in boundaries (e.g., `EDCODE`).
   - Normalize both boundary IDs and CSV `zoneid` to a consistent, comparable format (strip, uppercase, remove prefixes if needed).
3. **Join & validation**
   - Perform a **left join** of boundaries to ED-level census data.
   - Compute:
     - Share of boundary features with non-null census data.
     - Lists of IDs present only in boundaries or only in CSV.
   - Require >95% match rate for join to be accepted; otherwise, document and fix mismatches.
4. **Map production**
   - Generate example choropleth maps (in QGIS and/or Python) for:
     - Chinese-born share.
     - No-car household rate.
     - Owner-occupation rate.
   - Export maps (PNG, high resolution) with legends, scale bar, and clear titles.

---

## 7. Non-Functional Requirements

1. **Reproducibility**
   - All steps runnable from command line (e.g., `buildall.py`) or from a single notebook per year.
   - Versioned configurations in `configs/` (`sources.yml`, `geography.yml`, `pipeline.yml`).

2. **Code quality**
   - Modular design under `src/fyppipeline/`.
   - Basic unit tests in `tests/` verifying:
     - Manchester filter (`03BN` prefix) selects expected number of zones.
     - Aggregation script shapes and key totals.

3. **Performance**
   - Should run on a standard laptop (no cluster).
   - Able to process national-level tables if needed, but optimized for Manchester subsets.

4. **Documentation**
   - Up-to-date `README.md` describing structure and workflow.
   - This PRD captured in `docs/prd.md` (or similar).

5. **Compliance & ethics**
   - No microdata, only aggregate statistics.
   - Follow UK Data Service terms for redistribution of derived aggregates.
   - Cite original datasets clearly.

---

## 8. Data Sources and Dependencies

- **1981 Census SAS tables** (UK Data Service, DOI `10.5257/census/aggregate-1981-1`).
- **1991 Census SAS tables** (SAS01+, SAS02, SAS04, SAS07/SAS08, SAS20+).
- **Variable lookup tables** for each year (code → description).
- **Geography lookup tables**:
  - 1981 EDs, zone IDs, area names, types.
  - 1991 EDs/wards/postcode sectors.
- **Boundary shapefiles/GeoPackages**:
  - 1981 Enumeration Districts for Manchester (or national 1981 EDs filtered to `03BN`).
  - 1991 ED/ward/postcode sector geographies (for harmonization).

---

## 9. Milestones and Deliverables

1. **M1 – 1981 ED pipeline complete**
   - ED-level tables for SAS02, SAS04, SAS07/SAS08, SAS10.
   - Manchester-only ED subsets saved.
   - City-level profile (single-row) confirmed.

2. **M2 – 1981 mapping validated**
   - 1981 ED boundaries loaded.
   - Successful join with >95% ID match.
   - At least three choropleths exported.

3. **M3 – 1991 ingestion and ED harmonization**
   - 1991 SAS tables ingested and ED/ward/postcode sector decisions finalized.
   - Spatial join or areal interpolation strategy chosen and documented.

4. **M4 – Longitudinal indicators**
   - 1981–1991 change metrics computed at ED/ward level.
   - Data prepared for statistical analysis and visualization.

5. **M5 – Dissertation-ready assets**
   - Clean data files (CSV + GeoJSON/shapefile).
   - Mapping figures.
   - Methods documentation and PRD updated.

---

## 10. Open Questions / Risks

1. **Exact 1991 geography choice**
   - Whether EDs, wards, or postcode sectors are most feasible and how easily they map back to 1981 EDs.
2. **Chinese-born variable consistency**
   - Ensuring comparable definitions of “Chinese/China/Far East” across 1981 and 1991 tables.
3. **Areal harmonization**
   - Potential need for areal interpolation if boundaries change significantly between years.

These should be resolved before locking the 1991 design.

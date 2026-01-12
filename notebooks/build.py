import os
import glob
import pandas as pd

base = r"D:\Workspace\Data_Pending\s02ews"  # raw string avoids escaping issues

files = sorted(glob.glob(os.path.join(base, "*.csv")))
print("CSV files found:", files)

files = [fr"{base}\s02ews{i}.csv" for i in range(1, 5)]
dfs = [pd.read_csv(fp, dtype={"zoneid": "string"}) for fp in files]
sas02_1981 = pd.concat(dfs, ignore_index=True)

# Clean column names and zoneid
sas02_1981.columns = sas02_1981.columns.str.strip()
sas02_1981["zoneid"] = sas02_1981["zoneid"].str.strip()

value_cols = [c for c in sas02_1981.columns if c != "zoneid"]
sas02_1981[value_cols] = sas02_1981[value_cols].apply(pd.to_numeric, errors="coerce")

# Specify Manchester district
MANCHESTER_DISTRICT = "03BN"
manchester_zones = sas02_1981.loc[
    sas02_1981["zoneid"].str.startswith(MANCHESTER_DISTRICT),
    "zoneid"
].unique()

print(f"Found {len(manchester_zones)} Manchester zones")
print(f"Sample zones: {sorted(manchester_zones)[:5]}")

# Aggregate all Manchester zones
manchester_agg = pd.DataFrame(
    [sas02_1981.loc[sas02_1981["zoneid"].str.startswith(MANCHESTER_DISTRICT), value_cols].sum(numeric_only=True)],
    columns=value_cols
)

manchester_agg.insert(0, "zoneid", MANCHESTER_DISTRICT)

print("\n=== Manchester City (1981) - SAS02 All Residents ===")
print(manchester_agg)

manchester_agg.to_csv("1991_sas02_totalpop_combined.csv", index=False)
print("\nFull aggregate saved to:1991_sas02_totalpop_combined.csv")
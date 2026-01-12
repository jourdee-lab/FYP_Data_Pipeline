import pandas as pd

base = r"D:\Workspace\FYP_Data_Pipeline\data\processed\aggregates\census_1981\1981_merged_1981.csv"  # raw split folder
files = sorted(glob.glob(os.path.join(base, "*.csv")))

dfs = [pd.read_csv(fp, dtype={"zoneid": "string"}) for fp in files]
sas04_eds = pd.concat(dfs, ignore_index=True)

# Clean
sas04_eds.columns = sas04_eds.columns.str.strip()
sas04_eds["zoneid"] = sas04_eds["zoneid"].str.strip()

# Filter Manchester ONLY (keep all EDs within 03BN)
sas04_eds_manchester = sas04_eds[sas04_eds["zoneid"].str.startswith("03BN")].copy()

print(f"Rows in ED-level dataset: {len(sas04_eds_manchester)}")
print(f"Unique EDs: {sas04_eds_manchester['zoneid'].nunique()}")
print(f"Sample EDs: {sorted(sas04_eds_manchester['zoneid'].unique())[:10]}")

sas04_eds_manchester.to_csv("manchestersas04_1981_eds.csv", index=False)

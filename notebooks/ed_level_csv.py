import pandas as pd
import glob
import os
from pathlib import Path

# Input: can be either
# - a local CSV file path
# - a local directory containing multiple split CSVs
# - an HTTP(S) URL to a CSV (including GitHub raw URLs)
base = "data/processed/aggregates/census_1981/1981_merged_1981.csv"

def _try_convert_github_blob_to_raw(url: str) -> str:
	# If someone accidentally pasted a GitHub 'blob' page URL, convert it to the raw URL
	if "github.com" in url and "/blob/" in url:
		return url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
	return url

base_path = str(base)
dfs = []

try:
	if base_path.startswith(("http://", "https://")):
		# convert GitHub blob pages to raw if necessary
		url = _try_convert_github_blob_to_raw(base_path)
		dfs.append(pd.read_csv(url, dtype={"zoneid": "string"}))
	else:
		p = Path(base_path)
		if p.is_file():
			dfs.append(pd.read_csv(p, dtype={"zoneid": "string"}))
		elif p.is_dir():
			files = sorted(glob.glob(os.path.join(base_path, "*.csv")))
			if not files:
				raise FileNotFoundError(
					f"No CSV files found in directory: {base_path}.\n"
					"Place split CSVs there or point `base` to the merged CSV file."
				)
			for fp in files:
				dfs.append(pd.read_csv(fp, dtype={"zoneid": "string"}))
		else:
			raise FileNotFoundError(
				f"The path provided does not exist or is not accessible: {base_path}\n"
				"Set `base` to a local CSV file, a directory of CSVs, or a raw URL."
			)
except Exception as e:
	# Surface helpful diagnostics instead of a pandas.concat ValueError
	raise RuntimeError(
		"Failed to read input CSV(s) for ED-level processing. See original error below:\n"
	) from e

if not dfs:
	raise RuntimeError(
		"No dataframes were loaded (empty list). Check that `base` points to a valid CSV file, a directory with CSVs, or a raw GitHub URL."
	)

sas04_eds = pd.concat(dfs, ignore_index=True)

# Clean
sas04_eds.columns = sas04_eds.columns.str.strip()
if "zoneid" not in sas04_eds.columns:
	raise KeyError("Expected column 'zoneid' not found in the loaded CSV(s). Check variable lookups and column names.")
sas04_eds["zoneid"] = sas04_eds["zoneid"].astype("string").str.strip()

# Filter Manchester ONLY (keep all EDs within 03BN)
sas04_eds_manchester = sas04_eds[sas04_eds["zoneid"].str.startswith("03BN")].copy()

print(f"Rows in ED-level dataset: {len(sas04_eds_manchester)}")
print(f"Unique EDs: {sas04_eds_manchester['zoneid'].nunique()}")
print(f"Sample EDs: {sorted(sas04_eds_manchester['zoneid'].unique())[:10]}")

# Paths for the comparison files (can be created externally)
boundary_file = Path("boundary_ed_codes.txt")
csv_codes_file = Path("csv_ed_codes.txt")

# If csv_ed_codes.txt doesn't exist, create it from the loaded DataFrame
if not csv_codes_file.exists():
	try:
		csv_zoneids = sorted(sas04_eds_manchester["zoneid"].dropna().unique())
		csv_codes_file.write_text("\n".join(csv_zoneids))
		print(f"Wrote {len(csv_zoneids)} zoneids to {csv_codes_file} (auto-generated from DataFrame)")
	except Exception as e:
		print(f"Could not auto-generate {csv_codes_file}: {e}")

if not boundary_file.exists():
	print(f"Warning: {boundary_file} not found. Skipping ED-code comparison.\nPlace a file with one ED code per line named '{boundary_file}' to enable comparison.")
else:
	# Read both lists
	with open(boundary_file) as f:
		boundary_eds = set([ln.strip() for ln in f.read().splitlines() if ln.strip()])

	with open(csv_codes_file) as f:
		csv_eds = set([ln.strip() for ln in f.read().splitlines() if ln.strip()])

	# Compare
	in_both = boundary_eds & csv_eds
	only_boundary = boundary_eds - csv_eds
	only_csv = csv_eds - boundary_eds

	print(f"\n✓ EDs in BOTH: {len(in_both)}")
	print(f"✗ Only in boundaries (not in CSV): {len(only_boundary)} → {sorted(list(only_boundary))[:50]}")
	print(f"✗ Only in CSV (not in boundaries): {len(only_csv)} → {sorted(list(only_csv))[:50]}")

	match_ratio = len(in_both) / max(len(boundary_eds), len(csv_eds)) * 100 if max(len(boundary_eds), len(csv_eds)) > 0 else 0.0
	print(f"\n✓ Match ratio: {match_ratio:.1f}%")

# Persist Manchester ED-level CSV
sas04_eds_manchester.to_csv("manchestersas04_1981_eds.csv", index=False)

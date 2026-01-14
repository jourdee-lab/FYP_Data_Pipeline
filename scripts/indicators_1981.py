import pandas as pd

df = pd.read_csv("https://raw.githubusercontent.com/jourdee-lab/manchester-spatial-analysis-data-lab/refs/heads/main/data/processed/aggregates/final_merged_1981.csv")
assert len(df) == 1, "Expected a single-row Manchester 1981 profile"

OWNER_COL = "81sas100967"
den = df["81sas100929"].iloc[0]
owner_num = df[OWNER_COL].iloc[0]
no_car_num = df["81sas100949"].iloc[0]
over_gt1_5_num = df["81sas100945"].iloc[0]
lack_bath_wc_num = df["81sas100932"].iloc[0]
no_inside_bath_wc_num = df["81sas100933"].iloc[0]

# 5. Compute rates (proportions 0–1)
indicators = {
    "zoneid": ["03BN"],
    "owner_occupied_rate": [owner_num / den],
    "no_car_households_rate": [no_car_num / den],
    "overcrowding_gt1_5_pproom_rate": [over_gt1_5_num / den],
    "lack_bath_wc_rate": [lack_bath_wc_num / den],
    "no_inside_bath_wc_rate": [no_inside_bath_wc_num / den],
    "amenities_deprivation_any_rate": [
        (lack_bath_wc_num + no_inside_bath_wc_num) / den
    ],
}

ind_df = pd.DataFrame(indicators)

# raw counts
ind_df["denominator_households"] = den
ind_df["owner_occupied_count"] = owner_num
ind_df["no_car_households_count"] = no_car_num
ind_df["overcrowded_gt1_5_pproom_count"] = over_gt1_5_num
ind_df["lack_bath_wc_count"] = lack_bath_wc_num
ind_df["no_inside_bath_wc_count"] = no_inside_bath_wc_num

ind_df.to_csv("1981_indicators.csv", index=False)
print("Saved 1981_indicators.csv")
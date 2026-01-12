import geopandas as gpd

boundaries = gpd.read_file(r"D:\Workspace\FYP_Data_Pipeline\gis_boundaries\1981_ed_manchester")
print(boundaries.columns)
print(boundaries.head())
print(f"CRS: {boundaries.crs}")
print(f"Number of features: {len(boundaries)}")

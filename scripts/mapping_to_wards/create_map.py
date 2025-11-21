import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import re
from shapely.geometry import Point
import numpy as np

def parse_address(text):
    if not isinstance(text, str):
        return None, None
    match = re.match(r"(\d+[A-Z\-]*)\s+(.*)", text)
    if match:
        num, name = match.groups()
        return num, name.strip().upper()
    return None, text.strip().upper()


def extract_street_info(row):
    loc = str(row.get("location2", "")).strip()
    match = re.match(r"(\d+[A-Z\-]*)\s+(.*)", loc)
    if match:
        num, street = match.groups()
        return num, street.strip().upper()
    return None, loc.strip().upper()


def find_nearest_point(row):
    subset = addresses[addresses["addr_street"] == row["ticket_street"]]
    if subset.empty:
        return None
    try:
        target_num = float(re.match(r"(\d+)", row["ticket_num"]).group(1))
        subset["num_val"] = subset["addr_num"].str.extract(r"(\d+)").astype(float)
        nearest_idx = (subset["num_val"] - target_num).abs().idxmin()
        return subset.loc[nearest_idx, "geometry"]
    except Exception:
        return subset.iloc[0]["geometry"]


if __name__ == "__main__":
    # Load shapefile
    addresses = gpd.read_file("Address_Points.shp")
    #print(addresses.head())
    #print(addresses.crs)

    # Convert MultiPoint → Point
    addresses["geometry"] = addresses["geometry"].apply(
        lambda g: g.geoms[0] if g.geom_type == "MultiPoint" else g
    )
    addresses = addresses.to_crs(epsg=4326)

    # Parse out addr_num and addr_street
    addresses[["addr_num", "addr_street"]] = addresses["ADDRESS37"].apply(
        lambda x: pd.Series(parse_address(x))
    )

    #print(addresses[["ADDRESS37", "addr_num", "addr_street"]].head())

    # Load wards (optional for visualization)
    wards = gpd.read_file("WARD.shp").to_crs(epsg=4326)
    print(wards.columns)

    # Load and combine monthly parking CSVs
    dataset_folder = "../../parkingData/"
    for i in range(1, 13):
        filename = f"{dataset_folder}Parking_Tags_Data_2024_{i:03d}.csv"
        df_part = pd.read_csv(filename)
        df = pd.concat([df, df_part], ignore_index=True) if i > 1 else df_part

    # --- DEVELOPMENT: take a reproducible random subset for plotting ---
    # This avoids expensive nearest-point matching on the full dataset while
    # developing/visualizing. Change n_sample or remove during final runs.
    n_sample = 1000
    if len(df) > n_sample:
        df = df.sample(n=n_sample, random_state=42).reset_index(drop=True)
    else:
        df = df.reset_index(drop=True)

    # Parse ticket addresses
    df[["ticket_num", "ticket_street"]] = df.apply(
        extract_street_info, axis=1, result_type="expand"
    )
    
    # 🔍 Filter to just one street for testing
    test_street = "KING ST W"       # <-- pick any street you want to test
    df = df[df["ticket_street"] == test_street].reset_index(drop=True)

    #print(f"Testing with {len(df)} tickets on {test_street}")

    # Match to nearest address point
    df["geometry"] = df.apply(find_nearest_point, axis=1)

    # Convert to GeoDataFrame
    tickets_gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
    
    tickets_with_wards = gpd.sjoin(tickets_gdf, wards, how="left", predicate="within")
    print(tickets_with_wards[["ticket_street", "AREA_L_CD"]])


    # Plot
    ax = wards.plot(color="none", edgecolor="black", figsize=(9, 9))
    tickets_gdf.plot(ax=ax, markersize=1, color="red")
    plt.show()


# def extract_street_info(row):
#     # location2 often contains "47 BORDEN ST"
#     loc = str(row.get("location2", "")).strip()
#     match = re.match(r"(\d+[A-Z\-]*)\s+(.*)", loc)
#     if match:
#         num, street = match.groups()
#         return num, street.strip().upper()
#     return None, loc.strip().upper()




# def parse_address(text):
#     if not isinstance(text, str):
#         return None, None
#     match = re.match(r"(\d+[A-Z\-]*)\s+(.*)", text)
#     if match:
#         num, name = match.groups()
#         return num, name.strip().upper()
#     return None, text.strip().upper()

#     addresses[["addr_num", "addr_street"]] = addresses["ADDRESS37"].apply(
#     lambda x: pd.Series(parse_address(x))
#     )

# def find_nearest_point(row):
#     # Filter candidate addresses by street
#     subset = addresses[addresses["addr_street"] == row["ticket_street"]]
#     if subset.empty:
#         return None
#     # Convert numbers to numeric (drop non-numeric cases)
#     try:
#         target_num = float(re.match(r"(\d+)", row["ticket_num"]).group(1))
#         subset["num_val"] = subset["addr_num"].str.extract(r"(\d+)").astype(float)
#         nearest_idx = (subset["num_val"] - target_num).abs().idxmin()
#         return subset.loc[nearest_idx, "geometry"]
#     except Exception:
#         return subset.iloc[0]["geometry"]


# if __name__ == "__main__":
#     addresses = gpd.read_file("Address_Points.shp")
#     print(addresses.head())
#     print(addresses.crs)  # check the coordinate system

#     addresses.plot(markersize=1, figsize=(8,8))

#     wards = gpd.read_file("WARD.shp").to_crs(epsg=4326)

#     ax = wards.plot(color="none", edgecolor="black", figsize=(9,9))
#     addresses.plot(ax=ax, markersize=0.5, color="red")

#     # plt.show()

#     addresses["geometry"] = addresses["geometry"].apply(
#         lambda g: g.geoms[0] if g.geom_type == "MultiPoint" else g
#     )

#     addresses = addresses.to_crs(epsg=4326)




#     # Open the dataset
#     dataset_folder = "../../parkingData/"
#     for i in range(1, 13):
#         if i < 10:
#             df_part = pd.read_csv(f"{dataset_folder}Parking_Tags_Data_2024_00{i}.csv")
#         else:
#             df_part = pd.read_csv(f"{dataset_folder}Parking_Tags_Data_2024_0{i}.csv")

#         if i == 1:
#             df = df_part
#         else:
#             df = pd.concat([df, df_part], ignore_index=True)
#     df[["ticket_num", "ticket_street"]] = df.apply(extract_street_info, axis=1, result_type="expand")
    
#     df["geometry"] = df.apply(find_nearest_point, axis=1)
    
#     tickets_gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
    
#     ax = wards.plot(color="none", edgecolor="black", figsize=(9,9))
#     tickets_gdf.plot(ax=ax, markersize=1, color="red")
#     plt.show()

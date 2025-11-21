import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import re
import numpy as np
from tqdm import tqdm

tqdm.pandas()

def extract_num_and_street(address):
    if not isinstance(address, str):
        return None, None
    match = re.match(r"(\d+)[A-Z\-]*\s+(.*)", address.strip().upper())
    if match:
        return match.groups()
    return None, address.strip().upper()


if __name__ == "__main__":
    # --- Load address points ---
    addresses = gpd.read_file("Address_Points.shp")
    addresses["geometry"] = addresses["geometry"].apply(
        lambda g: g.geoms[0] if g.geom_type == "MultiPoint" else g
    )
    addresses = addresses.to_crs(epsg=4326)
    addresses[["addr_num", "addr_street"]] = addresses["ADDRESS37"].apply(
        lambda x: pd.Series(extract_num_and_street(x))
    )
    addresses["addr_num"] = pd.to_numeric(addresses["addr_num"], errors="coerce")

    # --- Load wards shapefile ---
    wards = gpd.read_file("WARD.shp").to_crs(epsg=4326)
    print("Ward columns:", wards.columns.tolist())

    # --- Load and sample monthly CSVs ---
    dataset_folder = "../../parkingData/"
    df_list = []
    for i in tqdm(range(1, 13), desc="Loading + sampling monthly CSVs"):
        filename = f"{dataset_folder}Parking_Tags_Data_2024_{i:03d}.csv"
        df_part = pd.read_csv(filename)

        # Sample e.g. 2,000 rows per month (adjust to your system)
        n_sample = min(2000, len(df_part))
        df_part = df_part.sample(n=n_sample, random_state=42)

        df_list.append(df_part)

    df = pd.concat(df_list, ignore_index=True)
    print(f"✅ Combined sample size: {len(df):,} rows")

    # --- Extract numeric + street info ---
    df[["ticket_num", "ticket_street"]] = df["location2"].apply(
        lambda x: pd.Series(extract_num_and_street(x))
    )
    df["ticket_num"] = pd.to_numeric(df["ticket_num"], errors="coerce")

    # --- Vectorized merge (small enough now) ---
    merged = pd.merge(
        df,
        addresses[["addr_num", "addr_street", "geometry"]],
        left_on="ticket_street",
        right_on="addr_street",
        how="left",
        suffixes=("", "_addr")
    )

    merged["num_diff"] = (merged["ticket_num"] - merged["addr_num"]).abs()
    merged = (
        merged.sort_values(["tag_number_masked", "num_diff"])
              .groupby("tag_number_masked", as_index=False)
              .first()
    )

    # --- Spatial join with wards ---
    tickets_gdf = gpd.GeoDataFrame(merged, geometry="geometry", crs="EPSG:4326")
    tickets_with_wards = gpd.sjoin(tickets_gdf, wards, how="left", predicate="within")

    # --- Save sample result ---
    output_file = "../../data/processed/Parking_Tags_Data_2024_SAMPLE_with_wards.csv"
    tickets_with_wards[[
        "tag_number_masked",
        "date_of_infraction",
        "infraction_code",
        "infraction_description",
        "set_fine_amount",
        "ticket_street",
        "AREA_L_CD",
        "AREA_NAME"
    ]].to_csv(output_file, index=False)

    print(f"Saved sampled ward-joined dataset to {output_file}")

    # --- Optional plot ---
    ax = wards.plot(color="none", edgecolor="black", figsize=(9, 9))
    tickets_gdf.plot(ax=ax, markersize=2, color="red")
    plt.show()

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import re
import numpy as np
from tqdm import tqdm

tqdm.pandas()

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def extract_num_and_street(address):
    """Extract the number and street name from an address string."""
    if not isinstance(address, str):
        return None, None
    match = re.match(r"(\d+)[A-Z\-]*\s+(.*)", address.strip().upper())
    if match:
        return match.groups()
    return None, address.strip().upper()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # --- Load Address Points (Toronto) ---
    addresses = gpd.read_file("Address_Points.shp")
    addresses["geometry"] = addresses["geometry"].apply(
        lambda g: g.geoms[0] if g.geom_type == "MultiPoint" else g
    )
    addresses = addresses.to_crs(epsg=4326)

    # Extract address components
    addresses[["addr_num", "addr_street"]] = addresses["ADDRESS37"].apply(
        lambda x: pd.Series(extract_num_and_street(x))
    )
    addresses["addr_num"] = pd.to_numeric(addresses["addr_num"], errors="coerce")

    # --- Load Wards shapefile ---
    wards = gpd.read_file("WARD.shp").to_crs(epsg=4326)
    print("Ward columns:", wards.columns.tolist())

    # --- Load monthly CSVs ---
    dataset_folder = "../../parkingData/"
    df_list = []
    for i in tqdm(range(1, 13), desc="Loading monthly CSVs"):
        filename = f"{dataset_folder}Parking_Tags_Data_2024_{i:03d}.csv"
        df_list.append(pd.read_csv(filename))
    df = pd.concat(df_list, ignore_index=True)
    del df_list

    # --- Extract numeric + street info ---
    df[["ticket_num", "ticket_street"]] = df["location2"].apply(
        lambda x: pd.Series(extract_num_and_street(x))
    )
    df["ticket_num"] = pd.to_numeric(df["ticket_num"], errors="coerce")

    # --- Process streets in chunks to avoid RAM blowup ---
    results = []
    unique_streets = df["ticket_street"].dropna().unique()
    print(f"Processing {len(unique_streets)} unique streets...")

    for street in tqdm(unique_streets, desc="Matching tickets to addresses"):
        tickets_sub = df[df["ticket_street"] == street].copy()
        addr_sub = addresses[addresses["addr_street"] == street].copy()
        if addr_sub.empty:
            continue

        # Compute absolute number difference for all combinations
        tickets_sub["key"] = 1
        addr_sub["key"] = 1
        joined = tickets_sub.merge(addr_sub, on="key").drop("key", axis=1)
        joined["num_diff"] = (joined["ticket_num"] - joined["addr_num"]).abs()

        # Keep nearest address per ticket
        best = (
            joined.sort_values(["tag_number_masked", "num_diff"])
            .groupby("tag_number_masked", as_index=False)
            .first()
        )
        results.append(best)

    if len(results) == 0:
        raise RuntimeError("No addresses matched any tickets — check address formatting!")

    merged = pd.concat(results, ignore_index=True)
    print(f"Reduced to {len(merged):,} matched ticket-address pairs")

    # --- Convert to GeoDataFrame and join with wards ---
    tickets_gdf = gpd.GeoDataFrame(merged, geometry="geometry", crs="EPSG:4326")
    tickets_with_wards = gpd.sjoin(tickets_gdf, wards, how="left", predicate="within")

    # --- Save final CSV ---
    output_file = "../../parkingData/Parking_Tags_Data_2024_with_wards.csv"
    tickets_with_wards[[
        "tag_number_masked",
        "date_of_infraction",
        "infraction_code",
        "infraction_description",
        "set_fine_amount",
        "ticket_street",
        "AREA_L_CD",  # ward number
        "AREA_NAME"   # ward name
    ]].to_csv(output_file, index=False)

    print(f"✅ Saved ward-joined dataset to {output_file}")

    # --- Optional: quick plot ---
    ax = wards.plot(color="none", edgecolor="black", figsize=(9, 9))
    tickets_gdf.sample(min(5000, len(tickets_gdf))).plot(ax=ax, markersize=1, color="red")
    plt.show()

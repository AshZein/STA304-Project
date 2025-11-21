import pandas as pd
import geopandas as gpd
import cupy as cp
import re
from tqdm import tqdm
import os
# ---------------------------------------------------------------
# 1. Helpers
# ---------------------------------------------------------------

def extract_num_and_street(address):
    """Extract number and street name (both uppercased)."""
    if not isinstance(address, str):
        return None, None
    match = re.match(r"(\d+)[A-Z\-]*\s+(.*)", address.strip().upper())
    if match:
        return match.groups()
    return None, address.strip().upper()


# ---------------------------------------------------------------
# 2. GPU kernel
# ---------------------------------------------------------------

nearest_kernel = cp.RawKernel(r'''
extern "C" __global__
void nearest_address(const double* ticket_nums,
                     const double* addr_nums,
                     const int* addr_offsets,
                     const int* addr_counts,
                     int* nearest_idx,
                     int n_tickets)
{
    int i = blockDim.x * blockIdx.x + threadIdx.x;
    if (i >= n_tickets) return;

    int start = addr_offsets[i];
    int count = addr_counts[i];
    double target = ticket_nums[i];

    double best_diff = 1e12;
    int best_j = -1;

    for (int j = 0; j < count; ++j) {
        double diff = fabs(target - addr_nums[start + j]);
        if (diff < best_diff) {
            best_diff = diff;
            best_j = start + j;
        }
    }
    nearest_idx[i] = best_j;
}
''', 'nearest_address')

# ---------------------------------------------------------------
# 3. Main
# ---------------------------------------------------------------

if __name__ == "__main__":
    # Change working directory to the script's folder
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("Loading shapefiles...")
    addresses = gpd.read_file("Address_Points.shp")
    addresses["geometry"] = addresses["geometry"].apply(
        lambda g: g.geoms[0] if g.geom_type == "MultiPoint" else g
    )
    addresses = addresses.to_crs(epsg=4326)
    addresses[["addr_num", "addr_street"]] = addresses["ADDRESS37"].apply(
        lambda x: pd.Series(extract_num_and_street(x))
    )
    addresses["addr_num"] = pd.to_numeric(addresses["addr_num"], errors="coerce")

    wards = gpd.read_file("WARD.shp").to_crs(epsg=4326)

    print("📦 Loading CSVs...")
    dataset_folder = "../../parkingData/"
    dfs = []
    for i in tqdm(range(1, 13)):
        f = f"{dataset_folder}Parking_Tags_Data_2024_{i:03d}.csv"
        dfs.append(pd.read_csv(f))
    df = pd.concat(dfs, ignore_index=True)
    del dfs

    # Parse numeric + street info
    df[["ticket_num", "ticket_street"]] = df["location2"].apply(
        lambda x: pd.Series(extract_num_and_street(x))
    )
    df["ticket_num"] = pd.to_numeric(df["ticket_num"], errors="coerce")

    # Take a smaller subset for testing
    df = df.sample(100000, random_state=42).reset_index(drop=True)

    # Merge by street name (CPU)
    merged = pd.merge(
        df, addresses[["addr_num", "addr_street"]],
        left_on="ticket_street", right_on="addr_street",
        how="inner", suffixes=("", "_addr")
    ).dropna(subset=["ticket_num", "addr_num"])

    print(f"Merged dataset: {len(merged):,} rows")

    # Prepare data for GPU (flattened vectors)
    ticket_nums = cp.asarray(merged["ticket_num"].to_numpy(dtype="float64"))
    addr_nums = cp.asarray(merged["addr_num"].to_numpy(dtype="float64"))

    # For simplicity assume same number of candidate addresses per ticket
    # (in production you'd group by street and index separately)
    n_tickets = ticket_nums.shape[0]
    n_addrs = addr_nums.shape[0]

    addr_offsets = cp.zeros(n_tickets, dtype=cp.int32)
    addr_counts = cp.full(n_tickets, n_addrs, dtype=cp.int32)

    nearest_idx = cp.zeros(n_tickets, dtype=cp.int32)

    # Run CUDA kernel
    threads = 256
    blocks = (n_tickets + threads - 1) // threads

    print("⚡ Running CUDA nearest-address kernel...")
    nearest_kernel((blocks,), (threads,),
                   (ticket_nums, addr_nums,
                    addr_offsets, addr_counts,
                    nearest_idx, n_tickets))

    cp.cuda.runtime.deviceSynchronize()

    result_idx = nearest_idx.get()
    merged["nearest_addr_num"] = merged["addr_num"].iloc[result_idx].values

    print("Finished GPU nearest matching!")

    # Convert to GeoDataFrame and join with wards
    addresses["lon"] = addresses.geometry.x
    addresses["lat"] = addresses.geometry.y
    merged = pd.merge(merged, addresses[["addr_num", "addr_street", "lon", "lat"]],
                      left_on=["nearest_addr_num", "ticket_street"],
                      right_on=["addr_num", "addr_street"], how="left")
    gdf = gpd.GeoDataFrame(merged, geometry=gpd.points_from_xy(merged.lon, merged.lat), crs="EPSG:4326")

    print("Performing spatial join with wards...")
    tickets_with_wards = gpd.sjoin(gdf, wards, how="left", predicate="within")

    # Save output
    output_file = "../../parkingData/Parking_Tags_Data_2024_with_wards_GPU.csv"
    tickets_with_wards[[
        "tag_number_masked", "date_of_infraction", "infraction_code",
        "infraction_description", "set_fine_amount", "ticket_street",
        "AREA_L_CD", "AREA_NAME"
    ]].to_csv(output_file, index=False)

    print(f" Saved: {output_file}")

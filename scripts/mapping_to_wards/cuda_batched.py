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
    """Extract the number and street name (uppercase)."""
    if not isinstance(address, str):
        return None, None
    match = re.match(r"(\d+)[A-Z\-]*\s+(.*)", address.strip().upper())
    if match:
        return match.groups()
    return None, address.strip().upper()


# ---------------------------------------------------------------
# 2. CUDA kernel (one thread per ticket)
# ---------------------------------------------------------------

nearest_kernel = cp.RawKernel(r'''
extern "C" __global__
void nearest_address(const double* ticket_nums,
                     const double* addr_nums,
                     int* nearest_idx,
                     int n_tickets,
                     int n_addrs)
{
    int i = blockDim.x * blockIdx.x + threadIdx.x;
    if (i >= n_tickets) return;

    double target = ticket_nums[i];
    double best_diff = 1e12;
    int best_j = -1;

    for (int j = 0; j < n_addrs; ++j) {
        double diff = fabs(target - addr_nums[j]);
        if (diff < best_diff) {
            best_diff = diff;
            best_j = j;
        }
    }
    nearest_idx[i] = best_j;
}
''', 'nearest_address')


# ---------------------------------------------------------------
# 3. Main workflow
# ---------------------------------------------------------------


import time

if __name__ == "__main__":
    total_start = time.time()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    stage_start = time.time()
    print("Loading shapefiles...")
    addresses = gpd.read_file("Address_Points.shp")
    addresses["geometry"] = addresses["geometry"].apply(
        lambda g: g.geoms[0] if g.geom_type == "MultiPoint" else g
    )
    addresses = addresses.to_crs(epsg=4326)

    # Parse address numbers and streets
    addresses[["addr_num", "addr_street"]] = addresses["ADDRESS37"].apply(
        lambda x: pd.Series(extract_num_and_street(x))
    )
    addresses["addr_num"] = pd.to_numeric(addresses["addr_num"], errors="coerce")
    addresses = addresses.dropna(subset=["addr_num", "addr_street"])

    print(f"Loaded {len(addresses):,} address points")
    print(f"Shapefiles loaded in {time.time() - stage_start:.2f} seconds.")

    stage_start = time.time()
    wards = gpd.read_file("WARD.shp").to_crs(epsg=4326)
    print(f"Loaded {len(wards):,} wards")
    print(f"Wards loaded in {time.time() - stage_start:.2f} seconds.")

    for year in [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]:
        print(f"Processing year {year}...")
        year_time = time.time()
        stage_start = time.time()
        dataset_folder = "../../combinedYearlyParkingData"
        df = pd.read_csv(f"{dataset_folder}/{year}/parking_data_{year}.csv")
        print(f"Combined dataset: {len(df):,} rows")
        print(f"Year {year} CSV loaded in {time.time() - stage_start:.2f} seconds.")

        stage_start = time.time()
        # Parse ticket addresses
        df[["ticket_num", "ticket_street"]] = df["location2"].apply(
            lambda x: pd.Series(extract_num_and_street(x))
        )
        df["ticket_num"] = pd.to_numeric(df["ticket_num"], errors="coerce")
        df = df.dropna(subset=["ticket_num", "ticket_street"])

        # Group addresses by street (for fast lookup)
        addr_groups = {s: g for s, g in addresses.groupby("addr_street")}
        unique_streets = df["ticket_street"].dropna().unique()
        print(f"Found {len(unique_streets):,} unique streets to process")

        all_results = []

        gpu_start = time.time()
        for street in tqdm(unique_streets, desc="Processing streets"):
            tickets = df[df["ticket_street"] == street].copy()
            addrs = addr_groups.get(street)
            if addrs is None or len(addrs) == 0 or len(tickets) == 0:
                continue

            ticket_nums = cp.asarray(tickets["ticket_num"].to_numpy(dtype="float64"))
            addr_nums   = cp.asarray(addrs["addr_num"].to_numpy(dtype="float64"))
            n_tickets, n_addrs = ticket_nums.size, addr_nums.size

            nearest_idx = cp.zeros(n_tickets, dtype=cp.int32)

            threads = 256
            blocks  = (n_tickets + threads - 1) // threads

            nearest_kernel((blocks,), (threads,),
                        (ticket_nums, addr_nums,
                            nearest_idx, n_tickets, n_addrs))
            cp.cuda.runtime.deviceSynchronize()

            idx = nearest_idx.get()
            # clamp invalids
            idx = [i if 0 <= i < len(addrs) else 0 for i in idx]

            tickets["nearest_addr_num"] = addrs.iloc[idx]["addr_num"].values
            tickets["lon"] = addrs.iloc[idx].geometry.x.values
            tickets["lat"] = addrs.iloc[idx].geometry.y.values

            all_results.append(tickets)

            # Free GPU memory between streets
            del ticket_nums, addr_nums, nearest_idx
            cp.get_default_memory_pool().free_all_blocks()

        print(f"Finished GPU matching: {sum(len(r) for r in all_results):,} ticket–address pairs")
        print(f"GPU matching for year {year} took {time.time() - gpu_start:.2f} seconds.")

        stage_start = time.time()
        print("Joining with ward polygons...")
        merged = pd.concat(all_results, ignore_index=True)
        gdf = gpd.GeoDataFrame(
            merged,
            geometry=gpd.points_from_xy(merged.lon, merged.lat),
            crs="EPSG:4326"
        )

        tickets_with_wards = gpd.sjoin(gdf, wards, how="left", predicate="within")

        print(f"Spatial join for year {year} took {time.time() - stage_start:.2f} seconds.")

        # Check if all input rows are present in the result using key columns
        key_cols = ["tag_number_masked", "date_of_infraction", "infraction_code", "time_of_infraction"]
        input_keys = df[key_cols].dropna().astype(str).agg('-'.join, axis=1)
        result_keys = tickets_with_wards[key_cols].dropna().astype(str).agg('-'.join, axis=1)

        found_count = input_keys.isin(result_keys).sum()
        total_count = len(input_keys)

        print(f"Matched rows: {found_count}/{total_count}")

        stage_start = time.time()
        output_file = f"../../parkingData/wardParkingData/Parking_Tags_Data_{year}_with_wards.csv"
        tickets_with_wards[[
            "tag_number_masked",
            "date_of_infraction",
            "infraction_code",
            "infraction_description",
            "set_fine_amount",
            "time_of_infraction",
            "location1",
            "location2",
            "location3",
            "location4",
            "province",
            "city",
            "AREA_L_CD",
            "AREA_NAME"
        ]].to_csv(output_file, index=False)

        print(f"Export for year {year} took {time.time() - stage_start:.2f} seconds.")
        print(f"dataset for year {year} completed.")
        print(f"Saved processed dataset to {output_file}")
        print(f"Total time for year {year}: {time.time() - year_time:.2f} seconds.")

    print(f"Total time for all years: {time.time() - total_start:.2f} seconds.")
        

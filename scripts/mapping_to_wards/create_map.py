import pandas as pd
import geopandas as gpd
from geopy.geocoders import Nominatim

addresses = gpd.read_file("Address_Points.shp")
print(addresses.head())
print(addresses.crs)  # check the coordinate system

# # Open the dataset
# dataset_folder = "../../parkingData/"
# for i in range(1, 13):
#     if i < 10:
#         df_part = pd.read_csv(f"{dataset_folder}Parking_Tags_Data_2024_00{i}.csv")
#     else:
#         df_part = pd.read_csv(f"{dataset_folder}Parking_Tags_Data_2024_0{i}.csv")

#     if i == 1:
#         df = df_part
#     else:
#         df = pd.concat([df, df_part], ignore_index=True)
        
# # Geocode addresses to get latitude and longitude
# df["address"] = df["location1"].fillna('') + ' ' + df["location2"].fillna('') + ' ' + df["location3"].fillna('') + ' ' + df["location4"].fillna('') + ', Toronto, ON'
# df["coords"] = df["address"].apply(lambda x: geolocator.geocode(x))
# df["lat"] = df["coords"].apply(lambda x: x.latitude if x else None)
# df["lon"] = df["coords"].apply(lambda x: x.longitude if x else None)

# wards = gpd.read_file("wards.shp")
# tickets = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326")

# tickets_in_wards = gpd.sjoin(tickets, wards, how="left", predicate="within")

# tickets_by_ward = tickets_in_wards.groupby("WARD_NAME").size().reset_index(name="ticket_count")

# wards = wards.merge(tickets_by_ward, on="WARD_NAME", how="left")
# wards.plot(column="ticket_count", legend=True, cmap="Reds")

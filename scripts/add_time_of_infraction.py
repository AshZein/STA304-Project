
import pandas as pd

ward_dataset_path = "/Users/ashz/Desktop/STA304/STA304-Project/parkingDataWards/Parking_Tags_Data_2024_with_wards_GPU.csv"
time_of_infraction_dataset_path = "/Users/ashz/Desktop/STA304/STA304-Project/combinedYearlyParkingData/2024/parking_data_2024.csv"
destination_file = "/Users/ashz/Desktop/STA304/STA304-Project/parkingDataWards/wards_complete.csv"

# Load datasets
ward_df = pd.read_csv(ward_dataset_path)
time_df = pd.read_csv(time_of_infraction_dataset_path)


# Columns to join on (use only reliable keys)
join_cols = [
    "tag_number_masked",
    "date_of_infraction"
]



# Try to parse date_of_infraction to YYYY-MM-DD if not already
def format_date_col(df, col):
	# Try both formats
	df[col] = pd.to_datetime(df[col].astype(str), errors="coerce").dt.strftime("%Y-%m-%d")
	return df

ward_df = format_date_col(ward_df, "date_of_infraction")
time_df = format_date_col(time_df, "date_of_infraction")


# Ensure join columns are all strings in both DataFrames
for col in join_cols:
    ward_df[col] = ward_df[col].astype(str)
    time_df[col] = time_df[col].astype(str)

# Print sample join keys for debugging
print("Sample ward_df join keys:")
print(ward_df[join_cols].head())
print("Sample time_df join keys:")
print(time_df[join_cols].head())


# Find columns in time_df not in ward_df
missing_cols = [col for col in time_df.columns if col not in ward_df.columns]

# Merge: left join ward_df with time_df on join_cols, bring in missing columns
merged = ward_df.merge(
    time_df[join_cols + missing_cols],
    on=join_cols,
    how="left"
)


# Save to destination file
merged.to_csv(destination_file, index=False)
print(f"Merged dataset saved to {destination_file}")
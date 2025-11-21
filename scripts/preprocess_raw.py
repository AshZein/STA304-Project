import pandas as pd
import os


if __name__ == "__main__":
    os.makedirs("../sortedParkingData", exist_ok=True)
    
    for dataset_name in os.listdir("../parkingData"):
        split_name = dataset_name.split("_")
        if len(split_name) < 5:
            current_year = split_name[-1].split(".")[0]
        else:
            current_year = split_name[3]
            
        if "Parking_Tags_Data_" in dataset_name:
            dataset_path = "../parkingData/" + dataset_name
            print(f"Processing {dataset_path}...")
            
            if current_year in ["2008", "2010"]:
                df = pd.read_csv(
                    dataset_path,
                    usecols=['tag_number_masked', 'date_of_infraction', 'infraction_code', 'infraction_description', 'set_fine_amount', 'time_of_infraction', 'location1', 'location2', 'location3', 'location4', 'province'],
                    engine="python",
                    on_bad_lines='skip',
                    encoding="utf-16",
                    sep=","
                )

            else:
                df = pd.read_csv(
                    dataset_path,
                    usecols=['tag_number_masked', 'date_of_infraction', 'infraction_code', 'infraction_description', 'set_fine_amount', 'time_of_infraction', 'location1', 'location2', 'location3', 'location4', 'province'],
                    engine="python",
                    on_bad_lines='skip',
                    encoding="utf-8",
                    sep=","
                )
        
            df['date_of_infraction'] = pd.to_datetime(
                df['date_of_infraction'].astype(str),
                format="%Y%m%d",
                errors="coerce"
            )
            df = df.dropna(subset=['date_of_infraction'])

            df['year_month'] = df['date_of_infraction'].dt.strftime('%Y_%m')

            for year_month, group in df.groupby('year_month'):
                year = year_month.split("_")[0]
                os.makedirs(f"../sortedParkingData/{year}", exist_ok=True)

                output_path = f"../sortedParkingData/{year}/parking_data_{year_month}.csv"
                group = group.drop(columns=["year_month"])

                if os.path.exists(output_path):
                    group.to_csv(output_path, mode='a', header=False, index=False)
                else:
                    group.to_csv(output_path, index=False)

            # df['year'] = df['date_of_infraction'].dt.year

            # # Group by year and save each as a single file
            # for year, group in df.groupby('year'):
            #     output_path = f"./data/processed/parking_data_{year}.csv"

            #     # Drop helper column before saving
            #     group = group.drop(columns=['year'])

            #     if os.path.exists(output_path):
            #         group.to_csv(output_path, mode='a', header=False, index=False)
            #     else:
            #         group.to_csv(output_path, index=False)
import pandas as pd
import os


if __name__ == "__main__":
    os.makedirs("../data/processed", exist_ok=True)
    
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
                    usecols=["ADJUST_COLUMN_NAMES_HERE"],
                    engine="python",
                    on_bad_lines='skip',
                    encoding="utf-16"
                )
            else:
                df = pd.read_csv(
                    dataset_path,
                    usecols=["ADJUST_COLUMN_NAMES_HERE"],
                    engine="python",
                    on_bad_lines='skip',
                    encoding="utf-8"
                )
            
            
import pandas as pd
import os


if __name__ == "__main__":
    os.makedirs("../data/processed", exist_ok=True)
    
    year = 2024 # Update this variable for different years
    
    for dataset_name in os.listdir("../parkingData"):
        if "Parking_Tags_Data_2024" in dataset_name:
            dataset_path = "../parkingData/" + dataset_name
            print(f"Processing {dataset_path}...")
            
            df = pd.read_csv(dataset_path,
                             usecols=["infraction_description"])
            
import pandas as pd
import os


if __name__ == "__main__":
    os.makedirs("../data/processed", exist_ok=True)
    
    counts = {}
    
    for dataset_name in os.listdir("../parkingData"):
        if "Parking_Tags_Data_2024" in dataset_name:
            dataset_path = "../parkingData/" + dataset_name
            print(f"Processing {dataset_path}...")
            
            df = pd.read_csv(dataset_path,
                             usecols=["infraction_description"])
            infraction_counts = df["infraction_description"].value_counts()
            
            for infraction, count in infraction_counts.items():
                if infraction in counts:
                    counts[infraction] += count
                else:
                    counts[infraction] = count

    # Save the counts to a CSV file
    counts_df = pd.DataFrame(list(counts.items()), columns=["infraction_description", "Count"])
    counts_df = counts_df.sort_values(by="Count", ascending=False)
    counts_df.to_csv("../data/processed/most_common_infractions.csv", index=False)
    print("Most common infractions saved to ../data/processed/most_common_infractions.csv")
import pandas as pd
import os


if __name__ == "__main__":
    os.makedirs("../data/processed", exist_ok=True)
    
    total_fines = {}
    
    for dataset_name in os.listdir("../parkingData"):
        split_name = dataset_name.split("_")
        if len(split_name) < 5:
            current_year = split_name[-1].split(".")[0]
        else:
            current_year = split_name[3]
            
        print(f"Current year: {current_year}")
        
        if current_year not in total_fines:
            total_fines[current_year] = 0
            
        if "Parking_Tags_Data_" in dataset_name:
            dataset_path = "../parkingData/" + dataset_name
            print(f"Processing {dataset_path}...")
            
            if current_year in ["2008", "2010"]:
                df = pd.read_csv(dataset_path, engine="python", encoding="utf-16", nrows=0)
                print(df.columns.tolist())

                df = pd.read_csv(
                    dataset_path,
                    usecols=["set_fine_amount"],
                    engine="python",
                    on_bad_lines='skip',
                    encoding="utf-16"
                )
            else:
                df = pd.read_csv(dataset_path, engine="python", encoding="utf-8", nrows=0)
                print(df.columns.tolist())
            
                df = pd.read_csv(
                    dataset_path,
                    usecols=["set_fine_amount"],
                    engine="python",
                    on_bad_lines='skip',
                    encoding="latin1"
                )
                
            print(df)
            year_total = df["set_fine_amount"].sum()
            total_fines[current_year] += year_total
            
    percent_increase = {}
    sorted_years = sorted(total_fines.keys())
    for i in range(1, len(sorted_years)):
        year = sorted_years[i]
        previous_year = sorted_years[i - 1]
        increase = ((total_fines[year] - total_fines[previous_year]) / total_fines[previous_year]) * 100
        percent_increase[year] = increase
        
    # Save the total fines and percent increase to CSV files
    fines_df = pd.DataFrame(list(total_fines.items()), columns=["Year", "Total Fines"])
    fines_df["Year"] = fines_df["Year"].astype(int)
    fines_df = fines_df.sort_values(by="Year")
    # Add percent increase column (NaN for the first year)
    fines_df["Percent Increase"] = fines_df["Year"].astype(str).map(percent_increase)
    fines_df["Percent Increase"] = fines_df["Percent Increase"].round(2)
    fines_df.to_csv("../data/processed/total_fines_per_year.csv", index=False)
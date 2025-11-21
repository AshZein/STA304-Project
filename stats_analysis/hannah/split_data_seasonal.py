import pandas as pd
import glob, os

parkingData = "C:/Users/jilli/STA304/data/"

spring = ["03", "04", "05"]
summer = ["06", "07", "08"]
fall = ["09", "10", "11"]
winter = ["12", "01", "02"]

os.makedirs(parkingData + "spring", exist_ok=True)
os.makedirs(parkingData + "summer", exist_ok=True)
os.makedirs(parkingData + "fall", exist_ok=True)
os.makedirs(parkingData + "winter", exist_ok=True)

for f in glob.glob(parkingData + "processed/2013/*"):
    print(f)
    df = pd.read_csv(f)
    yr = f.split("_")[2]
    month = (f.split("_")[3]).split(".")[0]
    if month in spring:
        print(f"loading {f} to spring")
        fname = parkingData + "seasons/spring/" + f"parking_data_{yr}_spring.csv"
        if not os.path.exists(fname):
            df.to_csv(fname, index=False)
        else:
            df.to_csv(fname, mode='a', header=False, index=False)
    if month in summer:
        print(f"loading {f} to summer")
        fname = parkingData + "seasons/summer/" + f"parking_data_{yr}_summer.csv"
        if not os.path.exists(fname):
            df.to_csv(fname, index=False)
        else:
            df.to_csv(fname, mode='a', header=False, index=False)
    if month in fall:
        print(f"loading {f} to fall")
        fname = parkingData + "seasons/fall/" + f"parking_data_{yr}_fall.csv"
        if not os.path.exists(fname):
            df.to_csv(fname, index=False)
        else:
            df.to_csv(fname, mode='a', header=False, index=False)
    if month in winter:
        print(f"loading {f} to winter")
        fname = parkingData + "seasons/winter/" + f"parking_data_{yr}_winter.csv"
        if not os.path.exists(fname):
            df.to_csv(fname, index=False)
        else:
            df.to_csv(fname, mode='a', header=False, index=False)

import pandas as pd
import os

data_path = os.path.join(os.getcwd(), "00_DATA", "01_OUTS", "01_LIST_AGENCIES", "20201015_adresses_agencies.csv")
df = pd.read_csv(data_path, usecols=["name", "addresse", "street",	"code_postal", "ville"])
df.columns
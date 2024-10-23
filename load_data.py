from dotenv import load_dotenv
from pathlib import Path
import os
import pyodbc
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
env_file = BASE_DIR / ".env"
load_dotenv(env_file)

def get_data(DB,query):
    conn = pyodbc.connect(
        'DRIVER={SQL Server};'
        f'SERVER={os.getenv("SERVER")};'
        f'DATABASE={DB};'
        f'UID={os.getenv("UID")};'
        f'PWD={os.getenv("PASSWORD")}'
    )
    df = pd.read_sql(query, conn)
    conn.close()
    return df
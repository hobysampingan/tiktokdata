# cost_manager.py

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json

class CostManager:
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    SHEET_ID = "1Kuy05JjpsZPoYZI0DcdaY7G_2_i63tdJOKTy-PWH26M"  # dari URL Google Sheet
    SHEET_NAME = "Sheet1"

    def __init__(self):
        self.service_account_info = st.secrets["google_credentials"]
        self.creds = Credentials.from_service_account_info(self.service_account_info, scopes=self.SCOPES)
        self.gc = gspread.authorize(self.creds)

    def load_cost_data(self):
        sheet = self.gc.open_by_key(self.SHEET_ID).worksheet(self.SHEET_NAME)
        records = sheet.get_all_records()
        return {row["product_name"]: float(row["cost_per_unit"]) for row in records}

    def save_cost_data(self, cost_dict):
        sheet = self.gc.open_by_key(self.SHEET_ID).worksheet(self.SHEET_NAME)
        sheet.clear()
        sheet.update(values=[["product_name", "cost_per_unit"]], range_name="A1")
        rows = [[k, v] for k, v in cost_dict.items()]
        sheet.update(values=rows, range_name="A2")
import pandas as pd


class FileService:
    @staticmethod
    def read_uploaded_file(uploaded_file) -> pd.DataFrame:
        name = uploaded_file.name.lower()
        if name.endswith(".csv"):
            return pd.read_csv(uploaded_file)
        if name.endswith(".xlsx") or name.endswith(".xls"):
            return pd.read_excel(uploaded_file)
        raise ValueError("Faqat CSV yoki Excel fayllar qo'llab-quvvatlanadi.")

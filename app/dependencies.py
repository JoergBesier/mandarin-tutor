from functools import lru_cache
from google.oauth2.service_account import Credentials
import gspread, os

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

@lru_cache
def get_sheet():
    creds_path = os.getenv("SERVICE_ACCOUNT_FILE", "credentials.json")
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    gc    = gspread.authorize(creds)
    tab    = os.getenv("GOOGLE_SHEET_TAB", "")     # default first sheet
    ss = gc.open_by_key(os.getenv("GOOGLE_SHEET_ID"))
    tab    = os.getenv("GOOGLE_SHEET_TAB", "")     # default first sheet
    return ss.worksheet(tab) if tab else ss.sheet1
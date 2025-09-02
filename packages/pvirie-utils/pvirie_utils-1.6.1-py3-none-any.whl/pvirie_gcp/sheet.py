from . import gcp
from googleapiclient.discovery import build

# Access Google Sheets

def get_session(credentials=None):
    if credentials is None:
        credentials = gcp.get_credentials()
    sheets_service = build('sheets', 'v4', credentials=credentials)
    return sheets_service


class Spreadsheet:
    def __init__(self, spreadsheet_id, credentials=None):
        self.spreadsheet_id = spreadsheet_id
        self.sheet_service = get_session(credentials)

    def get(self, range):
        result = self.sheet_service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=range).execute()
        return result.get('values', [])
    
    def get_metadata(self):
        result = self.sheet_service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
        return result

    def update(self, range, values):
        body = {'values': values}
        result = self.sheet_service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id, range=range, valueInputOption='RAW', body=body).execute()
        return result

    def append(self, range, values):
        body = {'values': values}
        result = self.sheet_service.spreadsheets().values().append(spreadsheetId=self.spreadsheet_id, range=range, valueInputOption='RAW', body=body).execute()
        return result

    def clear(self, range):
        result = self.sheet_service.spreadsheets().values().clear(spreadsheetId=self.spreadsheet_id, range=range).execute()
        return result

    def batch_update(self, requests):
        body = {'requests': requests}
        result = self.sheet_service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id, body=body).execute()
        return result

    def batch_get(self, ranges):
        result = self.sheet_service.spreadsheets().values().batchGet(spreadsheetId=self.spreadsheet_id, ranges=ranges).execute()
        return result.get('valueRanges', [])
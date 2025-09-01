from gspread import Client as Client, Spreadsheet as Spreadsheet, Worksheet as Worksheet

def load_gsheets(client_email: str, private_key: str, sheet_id: str, worksheet_id: str) -> list[dict[str, str]]:
    """Loads data from a Google Sheets worksheet.

    This function retrieves data from a Google Sheets worksheet using service account credentials.
    It authorizes the client, selects the specified worksheet, and reads the worksheet data.
    The first row of the worksheet will be treated as the column names.

    Args:
        client_email (str): The client email associated with the service account.
        private_key (str): The private key used for authentication.
        sheet_id (str): The ID of the Google Sheet.
        worksheet_id (str): The ID of the worksheet within the Google Sheet.

    Returns:
        list[dict[str, str]]: A list of dictionaries containing the Google Sheets content.
    """

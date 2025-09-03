try:
    from prefect.utilities.tasks import defaults_from_attrs
    from prefect import Task

    prefect_2 = False
except Exception as e:
    prefect_2 = True

from typing import Any, List, Union
import gspread
import pathlib

if prefect_2 is False:

    class ReadGsheetRow(Task):
        def __init__(
            self,
            credentials_filename: Union[str, pathlib.Path] = None,
            sheet_key: str = None,
            worksheet_name: str = None,
            **kwargs: Any
        ):
            self.credentials_filename = credentials_filename
            self.sheet_key = sheet_key
            self.worksheet_name = worksheet_name
            super().__init__(**kwargs)

        @defaults_from_attrs("credentials_filename", "sheet_key", "worksheet_name")
        def run(
            self,
            row: int,
            credentials_filename: Union[str, pathlib.Path] = None,
            sheet_key: str = None,
            worksheet_name: str = None,
        ) -> List[Any]:
            client = gspread.service_account(filename=credentials_filename)
            google_sheet = client.open_by_key(sheet_key)
            worksheet = google_sheet.worksheet(worksheet_name)
            return worksheet.row_values(row)

else:

    class ReadGsheetRow:
        def __init__(
            self,
            credentials_filename: Union[str, pathlib.Path] = None,
            sheet_key: str = None,
            worksheet_name: str = None,
            **kwargs: Any
        ):
            self.credentials_filename = credentials_filename
            self.sheet_key = sheet_key
            self.worksheet_name = worksheet_name

        def get_rows(self, rows: int) -> List[Any]:
            client = gspread.service_account(filename=self.credentials_filename)
            google_sheet = client.open_by_key(self.sheet_key)
            worksheet = google_sheet.worksheet(self.worksheet_name)
            all_values = worksheet.get_all_values()
            if rows <= len(all_values):
                return all_values[rows - 1]
            return []

from contextlib import contextmanager
from datetime import datetime, timedelta
import os
from typing import Annotated, Type
import pytest
from google.auth import default
from googleapiclient.discovery import build
from faker import Faker
from pydantic_gsheets import GoogleWorkSheet, SheetRow,GSIndex,GSRequired,GSFormat,GSParse
from random import randint
pytestmark = pytest.mark.sheets

sheet_id = os.environ["SHEET_ID"]


creds, _ = default(scopes=["https://www.googleapis.com/auth/spreadsheets"])



class SampleData1(SheetRow):
    username: Annotated[str, GSRequired,GSIndex(0)]
    id: Annotated[int, GSRequired,GSIndex(1)]
    email: Annotated[str, GSRequired,GSIndex(2)]
    age: Annotated[int, GSIndex(3)]
    location: Annotated[str, GSIndex(4)]
    created_at: Annotated[datetime, GSRequired,GSIndex(5),GSFormat('DATE_TIME', 'dd-MM-yyyy HH:mm')]

class SampleData2(SheetRow):
    title: Annotated[str, GSRequired,GSIndex(0)]
    author: Annotated[str, GSRequired,GSIndex(1)]
    published_date: Annotated[datetime, GSRequired,GSIndex(2),GSFormat('DATE_TIME', 'dd-MM-yyyy HH:mm')]


@pytest.fixture
def sheets_service():
    return build("sheets", "v4", credentials=creds)


@contextmanager
def open_sheet(sheets_service,  sheet_name:str,model:Type[SheetRow]):
    
    existing_sheets = sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    for sheet in existing_sheets.get("sheets", []):
        if sheet.get("properties", {}).get("title") == sheet_name:
            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body={
                    "requests": [
                        {"deleteSheet": {"sheetId": sheet.get("properties", {}).get("sheetId")}}
                    ]
                }
            ).execute()
            break
    yield GoogleWorkSheet.create_sheet(model, sheets_service, sheet_id,sheet_name,skip_if_exists=False)
    existing_sheets = sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    for sheet in existing_sheets.get("sheets", []):
        if sheet.get("properties", {}).get("title") == sheet_name:
            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body={
                    "requests": [
                        {"deleteSheet": {"sheetId": sheet.get("properties", {}).get("sheetId")}}
                    ]
                }
            ).execute()
            break
    else:
        raise ValueError(f"Sheet {sheet_name} not found for cleanup.")
    
@pytest.fixture(scope="function")
def test_worksheet1(sheets_service):
    with open_sheet(sheets_service, "Test Sheet1",SampleData1) as ws:
        yield ws


@pytest.fixture(scope="function")
def test_worksheet2(sheets_service):
    with open_sheet(sheets_service, "Test Sheet2",SampleData2) as ws:
        yield ws


def test_can_read_sheet_title(sheets_service):


    meta = sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()

    assert "properties" in meta
    assert "title" in meta["properties"]

def test_can_create_worksheet(test_worksheet1):



    
    data = []
    for _ in range(randint(1, 20)):
        Faker.seed()
        fake = Faker()
        data.append(
            SampleData1(
                username=fake.name(),
                id=fake.random_int(min=1, max=1000),
                email=fake.email(),
                age=fake.random_int(min=18, max=60),
                location=fake.city(),
                created_at=fake.date_time_this_decade()
            )
        )
    test_worksheet1.saveRows(data)
    data = data.copy()  # Copy the data to avoid mutation issues
    queried_data = list(test_worksheet1.rows(refresh=True,skip_rows_missing_required=False))
    assert queried_data == data, f"Expected {data} but got {queried_data}"

def assert_rows_equal(expected: list[SampleData2], actual: list[SampleData2]):
    for e, a in zip(expected, actual):
        assert e.title == a.title
        assert e.author == a.author
        assert abs(e.published_date - a.published_date) < timedelta(seconds=1)

def test_read_and_write_same_data(test_worksheet2):

    data = []
    for _ in range(randint(1, 20)):
        Faker.seed()
        fake = Faker()
        data.append(
            SampleData2(
                title=fake.sentence(),
                author=fake.name(),
                published_date=fake.date_time_this_decade()
            )
        )
    olddata = data.copy()  # Copy the data to avoid mutation issues
    test_worksheet2.saveRows(data)
    
    queried_data = list(test_worksheet2.rows(refresh=True, skip_rows_missing_required=False))
    assert queried_data == olddata, f"Expected {data} but got {queried_data}"

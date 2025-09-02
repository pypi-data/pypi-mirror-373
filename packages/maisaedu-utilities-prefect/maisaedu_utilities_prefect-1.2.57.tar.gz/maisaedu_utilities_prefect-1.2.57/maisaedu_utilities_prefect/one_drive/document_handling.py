import pandas as pd
import requests
import os
import json

GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"


def get_secrets():
    access_token = json.load(
        open(
            "data/one_drive_refreshed_access_token.json",
        )
    )
    return access_token


def read_docs(documents):
    df = []
    for document in documents:
        df.append({
            "sheet_dataframe": pd.read_excel(
                document['document_name'], 
                sheet_name=document['spreadsheet_tab_name'], 
                keep_default_na=False,
                na_values=[""]
            ),
            "document_name": document['document_name'],
            "spreadsheet_tab_name": document['spreadsheet_tab_name']
        })

    return df

def __get_shared_files_info(headers):
    url = "/me/drive/sharedWithMe"

    response_file_info = requests.get(
        GRAPH_API_ENDPOINT + url,
        headers=headers,
    )

    values = response_file_info.json()["value"]

    return values

def __get_shared_info(headers, file_id, file_url = None):
    values = __get_shared_files_info(headers)
    shared_documents = []

    try:
        for value in values:
            listItemUniqueId = value["remoteItem"]["sharepointIds"]["listItemUniqueId"]
            web_url = value["webUrl"]
            shared_documents.append({
                "id": listItemUniqueId,
                "name": value["name"],
                "web_url": web_url
            })
            if listItemUniqueId == file_id.lower() or web_url == file_url:
                drive_id = value["remoteItem"]["parentReference"]["driveId"]
                item_id = value["id"]
                unique_id = listItemUniqueId
        return drive_id, item_id, unique_id
    except UnboundLocalError:
        exception = "No sharepoint id matched the given id from docs. Possible shared documents are:"
        for document in shared_documents:
            exception += "\n" + str(document)
        raise UnboundLocalError(exception)
    

def get_docs(access_token, files_info):
    headers = ""

    SCOPES = [
        "Files.Read.All",
        "Files.ReadWrite.All",
        "User.Read.All",
        "User.ReadWrite",
        "User.ReadWrite.All",
    ]

    save_location = os.getcwd()

    headers = {"Authorization": f'Bearer {access_token["access_token"]}'}

    documents_info = []

    # Step 1. get the file name

    for file_info in files_info["docs"]:
        file_id = file_info["id"]
        file_url = file_info["url"]
        drive_id, item_id, unique_id = __get_shared_info(headers, file_id, file_url)

        url = f"/me/drives/{drive_id}/items/{item_id}"

        response_file_info = requests.get(
            GRAPH_API_ENDPOINT + url,
            headers=headers,
            params={"select": "name"},
        )

        file_name = response_file_info.json().get("name")
        # step 2.downloading OneDrive file

        response_file_content = requests.get(
            GRAPH_API_ENDPOINT + f"{url}/content",
            headers=headers,
        )

        # step 3. Save the file
        with open(os.path.join(save_location, file_name), "wb") as _f:
            _f.write(response_file_content.content)

        documents_info.append(
            {
                "id": unique_id,
                "name": file_name,
                "url": file_url,
            }
        )
    return documents_info


def document_handling(files_info):
    token = get_secrets()

    documents_info = get_docs(token, files_info)

    documents_names = [file["name"] for file in documents_info]
    documents_list = read_docs(files_info['docs_table_info'])

    return documents_names, documents_list

def get_documents_info(files_info):
    token = get_secrets()

    documents_info = get_docs(token, files_info)

    return documents_info

def get_all_shared_documents():
    token = get_secrets()

    values = __get_shared_files_info({"Authorization": f'Bearer {token["access_token"]}'})
    shared_documents = []

    for value in values:
            shared_documents.append({
                "id": value["remoteItem"]["sharepointIds"]["listItemUniqueId"],
                "name": value["name"],
                "url": value["webUrl"]
            })

    return shared_documents

def delete_docs(documents_names):
    for document_name in documents_names:
        os.remove(document_name)

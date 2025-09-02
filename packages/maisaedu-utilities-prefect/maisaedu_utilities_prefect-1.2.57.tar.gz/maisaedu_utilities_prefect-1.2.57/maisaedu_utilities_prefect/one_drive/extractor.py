from datetime import datetime, time
import pandas as pd
from maisaedu_utilities_prefect import get_dsn
from decimal import Decimal
from .document_handling import (
    document_handling,
    get_documents_info,
    delete_docs,
)
from maisaedu_utilities_prefect.database.postgres import (
    connect,
    select,
    execute,
    insert_batch,
    detect_sql_injection
)

class Extractor():
    def __init__(self, prefect_flow_name):
        self.prefect_flow_name = prefect_flow_name
        self.__get_file_infos()
        self.__update_file_id()
        self.__get_tables_info()
        self.__get_columns_info()

    def __get_file_infos(self):
        files_info = []
        conn = connect(get_dsn())
        result = select(
            conn,
            """
                select 
                    id, name, url 
                from 
                    meta.one_drive_docs 
                where 
                    prefect_flow_name = %s 
                    and is_active
            """,
            (self.prefect_flow_name,)
        )
        for r in result:
            files_info.append(
                {
                    "id": r[0],
                    "name": r[1],
                    "url": r[2]
                }
            )
        self.files_info = files_info
        conn.close()

    def __get_tables_info(self):
        tables_info = []
        conn = connect(get_dsn())
        result = select(
            conn,
            """
                select 
                     oddt.id, oddt.table_name, spreadsheet_tab_name, deletion_clause, skip_rows, odc.name
                from 
                    meta.one_drive_docs_tables oddt
                join 
                    meta.one_drive_docs as odc on odc.id = oddt.doc_id
                where 
                    odc.is_active 
                    and oddt.is_active 
                    and odc.prefect_flow_name = %s
            """,
            (self.prefect_flow_name,)
        )
        for r in result:
            tables_info.append(
                {
                    "id": r[0],
                    "name": r[1],
                    "spreadsheet_tab_name": r[2],
                    "deletion_clause": r[3],
                    "skip_rows": r[4],
                    "document_name": r[5]
                }
            )
        self.tables_info = tables_info
        conn.close()

    def __get_columns_info(self):
        conn = connect(get_dsn())

        for idx, t in enumerate(self.tables_info):
            columns = []
            result = select(
                conn,
                """
                    select 
                        column_name, "position", type_cast 
                    from 
                        meta.one_drive_docs_tables_columns 
                    where 
                        doc_table_id = %s
                """,
                (t['id'],)
            )

            for r in result:
                columns.append(
                    {
                        "column_name": r[0],
                        "position": r[1],
                        "type_cast": r[2]
                    }
                )
            t['columns'] = columns

            self.tables_info[idx] = t

        conn.close()

    def __get_documents(self, table_info=None, process_by_sheet=False):
        documents_names, documents_list = document_handling(
            files_info={
                "docs" : self.files_info,
                "docs_table_info": [table_info] if process_by_sheet else self.tables_info
            }
        )
        self.documents_names = documents_names
        self.documents_list = documents_list
        delete_docs(documents_names)

    def __convert_date_pt_br(self, date):
        if date:
            if isinstance(date, datetime):
                return date
            
            date_string = str(date).split(" ")[0]

            if date_string != "" and date_string.lower() != "nan":
                try:
                    return pd.to_datetime(date_string, format="%d/%m/%Y", errors='raise')
                except ValueError:
                    try:
                        return pd.to_datetime(date_string, format="%Y-%m-%d", errors='raise')
                    except ValueError:
                        return None
                    
    def __convert_to_boolean(self, value):
        if value:
            value = str(value).strip().lower().replace(" ", "")
            if value == "sim" or value == "s" or value == "1":
                return True
            elif value in ["não", "nao"] or value == "n" or value == "0":
                return False
        return None
    
    def __convert_to_interval(self, value):
        try:
            if isinstance(value, time):
                return value
            else:
                return pd.Timedelta(0)
        except Exception as e:
            return pd.Timedelta(0)

    def __convert_types(self, documents_list, columns):
        for column in columns:
            if column['type_cast'] is not None:

                if column['type_cast'] == 'string':
                    documents_list.iloc[:, column['position']] = documents_list.iloc[:, column['position']].astype(str)

                if column['type_cast'] == 'string and remove dots':
                    documents_list.iloc[:, column['position']] = documents_list.iloc[:, column['position']].apply(lambda x: f'{x:.0f}'.format(x) if isinstance(x, (int, float)) else str(x))
                    documents_list.iloc[:, column['position']] = documents_list.iloc[:, column['position']].apply(lambda x: x.replace('.0', '',) if isinstance(x, str) else x)

                if column['type_cast'] == 'date - dd/mm/yyyy':
                    documents_list.iloc[:, column['position']] = documents_list.iloc[:, column['position']].apply(
                        lambda x: pd.to_datetime(x, errors='coerce', format='%d/%m/%Y') if isinstance(x, str) else x
                    )

                if column['type_cast'] == 'numeric':
                    documents_list.iloc[:, column['position']] = documents_list.iloc[:, column['position']].apply(lambda x: x if str(x).isnumeric() else None)

                if column['type_cast'] == 'decimal':
                    documents_list.iloc[:, column['position']] = documents_list.iloc[:, column['position']].apply(lambda x: Decimal(str(x).replace(',', '.')))

                if column['type_cast'] == 'date - pt-br':
                    documents_list.iloc[:, column['position']] = documents_list.iloc[:, column['position']].apply(self.__convert_date_pt_br)

                if column['type_cast'] == 'boolean':
                    documents_list.iloc[:, column['position']] = documents_list.iloc[:, column['position']].apply(self.__convert_to_boolean)

                if 'zfill' in column['type_cast']:
                    fill_length = int(column['type_cast'].split(':')[1])
                    documents_list.iloc[:, column['position']] = documents_list.iloc[:, column['position']].astype(str).str.zfill(fill_length)

                if column['type_cast'] == 'interval':
                    documents_list.iloc[:, column['position']] = documents_list.iloc[:, column['position']].apply(self.__convert_to_interval)

        documents_list.replace({pd.NA: None}, inplace=True)
        documents_list.replace({"nan": None}, inplace=True)

        return documents_list
    
    def __update_file_id(self):
        documents_info = get_documents_info(
            files_info={
                "docs" : self.files_info
            },)
        with connect(get_dsn()) as conn:
            for file in self.files_info:
                for document_info in documents_info:
                    if file['url'] == document_info['url'] and file['id'] != document_info['id']:
                        execute(
                            conn,
                            """
                                update meta.one_drive_docs
                                set id = %s
                                where url = %s
                            """,
                            params=(document_info['id'], file['url'],)
                        )
                        execute(
                            conn,
                            """
                                update meta.one_drive_docs_tables
                                set doc_id = %s
                                where doc_id = %s
                            """,
                            params=(document_info['id'], file['url'],)
                        )
                        file['id'] = document_info['id']

    def __save_records(self, conn, table_name, spreadsheet_tab_name, columns, skip_rows=0, document_name=None):

        matching_document = next(
            (document for document in self.documents_list 
            if document['document_name'] == document_name and document['spreadsheet_tab_name'] == spreadsheet_tab_name), 
            None
        )

        if matching_document:
            sheet_data = matching_document['sheet_dataframe']
        else:
            sheet_data = self.documents_list[0][spreadsheet_tab_name]

        records = []
        sheet_data = self.__convert_types(sheet_data.iloc[skip_rows:], columns)

        for record in sheet_data.values:
            data = {}

            for column in columns:
                if column['type_cast'] == 'tab name':
                    data[column['column_name']] = spreadsheet_tab_name
                elif column['type_cast'] == 'doc name':
                    data[column['column_name']] = document_name
                else:
                    data[column['column_name']] = record[column['position']]

            records.append(data)

            if len(records) >= 1000:
                insert_batch(
                    conn,
                    records,
                    table_name,
                    onconflict="",
                    page_size=1000,
                    default_commit=False,
                )
                records = []

        if len(records) > 0:
            insert_batch(
                conn,
                records,
                table_name,
                onconflict="",
                page_size=1000,
                default_commit=False,
            )

    def save_data(self, process_by_sheet=False):
        if not process_by_sheet:
            self.__get_documents()
        for table_info in self.tables_info:
            if process_by_sheet:
                self.__get_documents(table_info=table_info, process_by_sheet=True)
            conn = connect(get_dsn())

            if table_info['deletion_clause'] is None:
                deletion_clause = '1=1'
            else:
                deletion_clause = table_info['deletion_clause']

            execute(
                conn,
                f"""
                    delete from {detect_sql_injection(table_info['name'])}
                    where {detect_sql_injection(deletion_clause)}
                """,
                default_commit=False,
            )

            self.__save_records(
                conn = conn,
                table_name = table_info['name'], 
                spreadsheet_tab_name = table_info['spreadsheet_tab_name'],
                columns = table_info['columns'],
                skip_rows = table_info['skip_rows'],
                document_name = table_info['document_name']
            )

            conn.commit()
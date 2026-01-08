import os
import xlsxwriter

from typing import Any
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentAnalysisFeature


# Set the endpoint and key
endpoint = "https://<your-key>.azure.com"
api_key = "<your-key>"


def analyze_general_documents_table_data_to_excel(
    result: Any, image_file_path: str
):
    dir_path, file_name, _ = file_pather(image_file_path)
    excel_output_file_name = "{}.{}".format(file_name, "xlsx")

    workbook = xlsxwriter.Workbook(
        os.path.join(dir_path, excel_output_file_name)
    )

    tbl_worksheet = workbook.add_worksheet(name="{}".format(file_name))
    adj_row_idx = 0
    adj_col_idx = 0
    for table_idx, table in enumerate(result.tables):
        print(
            "Table # {} has {} rows and {} columns".format(
                table_idx, table.row_count, table.column_count
            )
        )

        for cell in table.cells:
            cell_content = cleansing_content(cell.content)

            row_idx = adj_row_idx + cell.row_index

            if cell.column_index > adj_col_idx:
                adj_col_idx = cell.column_index

            tbl_worksheet.write(row_idx, cell.column_index, cell_content)

        adj_row_idx = adj_row_idx + table.row_count + 1

    # Insert original image
    tbl_worksheet.insert_image(
        0, adj_col_idx + 4, image_file_path, {"x_scale": 0.5, "y_scale": 0.5}
    )
    print(os.path.join(dir_path, excel_output_file_name), ": Excel has been created.")
    workbook.close()


# Create a client
def analyze_general_documents(image_file_path: str):
    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=endpoint, credential=AzureKeyCredential(api_key)
    )
    with open(image_file_path, "rb") as f:
        poller = document_intelligence_client.begin_analyze_document(
            "prebuilt-layout",
            body=f,
            content_type="application/octet-stream",
        )
    result = poller.result()

    analyze_general_documents_table_data_to_excel(result, image_file_path)


# Cleansing the content
def cleansing_content(cell_content):
    cell_content = str(cell_content).replace(":unselected:", "")
    cell_content = str(cell_content).replace(":selected:", "")
    cell_content = cell_content.strip()
    return cell_content


# Extract the file path
def file_pather(file_path: str) -> str:
    """
    Input: file_path: dir/filename.pdf
    Output: dir, filename, pdf
    """
    top_path_without_file_name_and_extension = os.path.split(
        os.path.dirname(file_path)
    )[-1]
    file_name_without_extension = os.path.splitext(os.path.basename(file_path))[0]
    file_extension = os.path.splitext(os.path.basename(file_path))[1]

    return (
        top_path_without_file_name_and_extension,
        file_name_without_extension,
        file_extension,
    )


if __name__ == "__main__":
    image_file_path = os.path.join("data", "table-page.png")
    analyze_general_documents(image_file_path)

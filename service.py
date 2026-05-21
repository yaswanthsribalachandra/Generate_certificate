import json
import os
import subprocess

from datetime import datetime
from openpyxl import load_workbook

from blob_storage import (
    blob_service_client,
    CACHE_CONTAINER,
    CERT_CONTAINER
)


# -----------------------------------
# CONFIG
# -----------------------------------

CACHE_FILE = "applicants.json"

EXCEL_FILE = "Applicants.xlsx"

SHEET_NAME = "1st Class certificate"

OUTPUT_FOLDER = "certificates"


# -----------------------------------
# LOAD CACHE FROM AZURE BLOB
# -----------------------------------
def load_cache():

    try:

        container_client = (
            blob_service_client
            .get_container_client(
                CACHE_CONTAINER
            )
        )

        blob_client = (
            container_client
            .get_blob_client(
                CACHE_FILE
            )
        )

        downloader = (
            blob_client.download_blob()
        )

        data = downloader.readall()

        return json.loads(data)

    except Exception as e:

        print(
            "\nLOAD CACHE ERROR:",
            e
        )

        return {}


# -----------------------------------
# SEARCH APPLICANT
# -----------------------------------
def search_applicant(
    cache_data,
    application_id
):

    return cache_data.get(
        str(application_id)
    )


# -----------------------------------
# FORMAT DOB
# -----------------------------------
def format_dob(date_string):

    if not date_string:
        return ""

    try:

        date_obj = datetime.strptime(
            str(date_string),
            "%Y-%m-%d %H:%M:%S"
        )

        return date_obj.strftime(
            "%d-%m-%Y"
        )

    except:

        return str(date_string)


# -----------------------------------
# EXTRACT YEAR
# -----------------------------------
def extract_year(date_string):

    if not date_string:
        return ""

    try:

        date_obj = datetime.strptime(
            str(date_string),
            "%d.%m.%Y"
        )

        return str(date_obj.year)

    except:

        return ""


# -----------------------------------
# UPLOAD PDF TO AZURE BLOB
# -----------------------------------
def upload_pdf_to_blob(
    pdf_path,
    filename
):

    try:

        container_client = (
            blob_service_client
            .get_container_client(
                CERT_CONTAINER
            )
        )

        blob_client = (
            container_client
            .get_blob_client(
                filename
            )
        )

        with open(pdf_path, "rb") as data:

            blob_client.upload_blob(
                data,
                overwrite=True
            )

        print(
            "\nPDF Uploaded Successfully"
        )

        return blob_client.url

    except Exception as e:

        print(
            "\nUPLOAD ERROR:",
            e
        )

        return None


# -----------------------------------
# GENERATE PDF
# -----------------------------------
def generate_pdf(applicant):

    # --------------------------------
    # CREATE CERTIFICATES FOLDER
    # --------------------------------

    os.makedirs(
        OUTPUT_FOLDER,
        exist_ok=True
    )

    # --------------------------------
    # LOAD WORKBOOK
    # --------------------------------

    workbook = load_workbook(
        EXCEL_FILE
    )

    sheet = workbook[
        SHEET_NAME
    ]

    # --------------------------------
    # CLEAR OLD PLACEHOLDER DATA
    # --------------------------------

    fields = [

        "Q16", "T16",

        "E18", "N18",

        "E19", "M19",

        "O38", "O39",

        "N40", "N42",

        "O44", "O45",

        "J47", "J48"

    ]

    for field in fields:

        sheet[field] = ""

    # --------------------------------
    # FORMAT VALUES
    # --------------------------------

    application_id = applicant.get(
        "application_id",
        ""
    )

    year = extract_year(
        applicant.get(
            "date_of_exam",
            ""
        )
    )

    dob = format_dob(
        applicant.get(
            "date_of_birth",
            ""
        )
    )

    applicant_name = applicant.get(
        "name",
        "UNKNOWN"
    ).replace(" ", "_")

    current_date = datetime.now().strftime(
        "%d_%m_%Y"
    )

    # --------------------------------
    # WRITE DATA INTO CERTIFICATE
    # --------------------------------

    sheet["Q16"] = application_id

    sheet["T16"] = year

    sheet["E18"] = applicant.get(
        "name",
        ""
    )

    sheet["N18"] = applicant.get(
        "father_name",
        ""
    )

    sheet["E19"] = applicant.get(
        "age",
        ""
    )

    sheet["M19"] = applicant.get(
        "present_residing_at",
        ""
    )

    sheet["O38"] = dob

    sheet["O39"] = applicant.get(
        "place_of_birth",
        ""
    )

    sheet["N40"] = applicant.get(
        "address_part_1",
        ""
    )

    sheet["N42"] = applicant.get(
        "address_part_2",
        ""
    )

    sheet["O44"] = applicant.get(
        "nationality",
        ""
    )

    sheet["O45"] = applicant.get(
        "height",
        ""
    )

    sheet["J47"] = applicant.get(
        "identification_mark_1",
        ""
    )

    sheet["J48"] = applicant.get(
        "identification_mark_2",
        ""
    )

    # --------------------------------
    # HIDE OTHER SHEETS
    # --------------------------------

    for ws in workbook.worksheets:

        if ws.title != SHEET_NAME:

            ws.sheet_state = "hidden"

    # --------------------------------
    # FILE NAMES
    # --------------------------------

    file_name = (

        f"{application_id}_"
        f"{applicant_name}_"
        f"{current_date}"

    )

    temp_excel = f"{file_name}.xlsx"

    pdf_file = os.path.join(

        OUTPUT_FOLDER,

        f"{file_name}.pdf"

    )

    # --------------------------------
    # SAVE TEMP EXCEL
    # --------------------------------

    workbook.save(
        temp_excel
    )

    # --------------------------------
    # CONVERT EXCEL TO PDF
    # --------------------------------

    command = [

        "/Applications/LibreOffice.app/Contents/MacOS/soffice",

        "--headless",

        "--convert-to",
        "pdf",

        temp_excel

    ]

    subprocess.run(command)

    # --------------------------------
    # GENERATED PDF
    # --------------------------------

    generated_pdf = temp_excel.replace(
        ".xlsx",
        ".pdf"
    )

    # --------------------------------
    # MOVE PDF
    # --------------------------------

    if os.path.exists(generated_pdf):

        os.rename(
            generated_pdf,
            pdf_file
        )

    # --------------------------------
    # DELETE TEMP EXCEL
    # --------------------------------

    if os.path.exists(temp_excel):

        os.remove(temp_excel)

    # --------------------------------
    # UPLOAD TO AZURE
    # --------------------------------

    filename = os.path.basename(
        pdf_file
    )

    blob_url = upload_pdf_to_blob(
        pdf_file,
        filename
    )

    # --------------------------------
    # SUCCESS MESSAGE
    # --------------------------------

    print(
        "\nPDF Generated Successfully"
    )

    print(
        f"\nSaved PDF: {pdf_file}"
    )

    print(
        f"\nBlob URL: {blob_url}"
    )

    return pdf_file


# -----------------------------------
# MAIN
# -----------------------------------
def main():

    cache_data = load_cache()

    application_id = input(
        "Enter Application ID: "
    ).strip()

    applicant = search_applicant(
        cache_data,
        application_id
    )

    if applicant:

        print("\nApplicant Found")

        print(
            f"Generating PDF for "
            f"{applicant.get('name')}"
        )

        generate_pdf(
            applicant
        )

    else:

        print(
            "\nApplicant ID not found"
        )


# -----------------------------------
# RUN
# -----------------------------------
if __name__ == "__main__":

    main()
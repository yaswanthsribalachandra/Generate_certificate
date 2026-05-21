from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from service import (
    load_cache,
    search_applicant,
    generate_pdf,
    upload_pdf_to_blob
)

import os


# =========================================
# FASTAPI APP
# =========================================
app = FastAPI()


# =========================================
# CORS
# =========================================
app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =========================================
# REQUEST MODEL
# =========================================
class ApplicantRequest(BaseModel):

    application_id: str


# =========================================
# HEALTH CHECK
# =========================================
@app.get("/")
def home():

    return {
        "success": True,
        "message": "Certificate PDF API Running"
    }


# =========================================
# GET APPLICANT DETAILS
# =========================================
@app.get("/applicant/{application_id}")
def get_applicant(application_id: str):

    try:

        # LOAD CACHE FROM AZURE
        cache_data = load_cache()

        # SEARCH APPLICANT
        applicant = search_applicant(
            cache_data,
            application_id
        )

        # NOT FOUND
        if not applicant:

            return {
                "success": False,
                "message": "Applicant not found"
            }

        # RETURN APPLICANT
        return {
            "success": True,
            "data": applicant
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }


# =========================================
# GENERATE PDF
# =========================================
@app.post("/generate/{application_id}")
def generate_certificate_pdf(
    application_id: str
):

    try:

        # LOAD CACHE
        cache_data = load_cache()

        # SEARCH APPLICANT
        applicant = search_applicant(
            cache_data,
            application_id
        )

        # NOT FOUND
        if not applicant:

            return {
                "success": False,
                "message":
                "Applicant ID not found"
            }

        # =====================================
        # SAFE FILE NAME
        # =====================================
        applicant_name = (
            applicant.get("name", "Unknown")
            .replace(" ", "_")
            .replace("/", "_")
        )

        pdf_filename = (
            f"{application_id}_{applicant_name}.pdf"
        )

        # =====================================
        # CREATE CERTIFICATES FOLDER
        # =====================================
        os.makedirs(
            "certificates",
            exist_ok=True
        )

        # =====================================
        # PDF PATH
        # =====================================
        pdf_path = os.path.join(
            "certificates",
            pdf_filename
        )

        # =====================================
        # CHECK EXISTING LOCAL PDF
        # =====================================
        existing_pdf = None

        for file in os.listdir("certificates"):

            if file.startswith(
                f"{application_id}_"
            ):

                existing_pdf = file
                break

        # =====================================
        # IF PDF EXISTS
        # =====================================
        if existing_pdf:

            existing_path = os.path.join(
                "certificates",
                existing_pdf
            )

            # UPLOAD EXISTING PDF
            blob_url = upload_pdf_to_blob(
                existing_path,
                existing_pdf
            )

            return {
                "success": True,

                "message":
                "PDF already generated",

                "pdf_url":
                blob_url
            }

        # =====================================
        # GENERATE NEW PDF
        # =====================================
        print("Generating New PDF...")

        pdf_file = generate_pdf(
            applicant
        )

        # =====================================
        # CHECK PDF EXISTS
        # =====================================
        if not os.path.exists(pdf_file):

            return {
                "success": False,

                "message":
                "PDF generation failed"
            }

        # =====================================
        # GET FILE NAME
        # =====================================
        filename = os.path.basename(
            pdf_file
        )

        # =====================================
        # UPLOAD TO AZURE BLOB
        # =====================================
        blob_url = upload_pdf_to_blob(
            pdf_file,
            filename
        )

        # =====================================
        # RETURN SUCCESS
        # =====================================
        return {
            "success": True,

            "message":
            "PDF Generated Successfully",

            "pdf_url":
            blob_url
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }


# =========================================
# DOWNLOAD LOCAL PDF
# =========================================
@app.get("/download/{filename}")
def download_pdf(filename: str):

    try:

        # PDF PATH
        pdf_path = os.path.join(
            "certificates",
            filename
        )

        # CHECK FILE EXISTS
        if not os.path.exists(pdf_path):

            return {
                "success": False,
                "message": "PDF not found"
            }

        # RETURN PDF
        return FileResponse(

            path=pdf_path,

            media_type="application/pdf",

            filename=filename
        )

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }


# =========================================
# RUN SERVER
# =========================================
# uvicorn main:app --reload
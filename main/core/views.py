import logging
from uuid import uuid4
import uuid, os
from django.http import JsonResponse
from pathlib import Path
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .utils import (
    merge_pdfs,
    compress_pdfs,
    images_to_pdfs,
    pdf_to_images,
    office_to_pdf,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MEDIA_ROOT = Path(settings.MEDIA_ROOT)
MEDIA_ROOT.mkdir(exist_ok=True)

def save_temp_file(uploaded_file):
    temp_path = MEDIA_ROOT / f"{uuid.uuid4()}_{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)
    return temp_path

def build_url(path):
    return settings.MEDIA_URL + path.name


""" ---------------- Merge PDF ---------------- """
@api_view(["POST"])
def merge_pdfs_view(request):
    try:
        files = request.FILES.getlist("file")
        if not files:
            return Response({"error": "Upload at least 2 PDF files"}, status=400)

        # Save uploaded files
        input_paths = [save_temp_file(f) for f in files]

        # Merge them
        merged_pdf_bytes = merge_pdfs(input_paths)

        # Save merged pdf into MEDIA folder
        file_name = f"{uuid4()}_merged.pdf"
        save_path = os.path.join(settings.MEDIA_ROOT, file_name)

        with open(save_path, "wb") as out:
            out.write(merged_pdf_bytes)

        # Build absolute URL
        file_url = request.build_absolute_uri(settings.MEDIA_URL + file_name)

        return JsonResponse({"url": file_url})

    except Exception as e:
        logger.exception(f"Merge PDF failed: {e}")
        return Response({"error": "Internal Server Error"}, status=500)

""" ---------------- Compress PDF ---------------- """
@api_view(["POST"])
def compress_view(request):
    try:
        if "file" not in request.FILES:
            return Response({"error": "Upload a PDF"}, status=400)

        input_path = save_temp_file(request.FILES["file"])
        output = compress_pdfs(input_path)
        return Response({"url": build_url(output)})
    
    except Exception as e:
        logger.exception(f"PDF compress failed: {e}")
        return Response({"error": "Internal Server Error"}, status=500)

""" ---------------- JPG to PDF ---------------- """
@api_view(["POST"])
def images_to_pdf_view(request):
    files = request.FILES.getlist("files")
    if not files:
        return Response({"error": "Upload Image"}, status=400)

    paths = [save_temp_file(f) for f in files]
    output = images_to_pdfs(paths)
    return Response({"url": build_url(output)})

""" ---------------- PDF to Images ---------------- """
@api_view(["POST"])
def pdf_to_images_view(request):
    if "file" not in request.FILES:
        return Response({"error": "Upload PDF"}, status=400)

    input_path = save_temp_file(request.FILES["file"])
    images = pdf_to_images(input_path)
    return Response({"images": [build_url(i) for i in images]})

""" ---------------- Office to PDF ---------------- """
@api_view(["POST"])
def oofice_to_pdf_view(request):
    if "file" not in request.FILES:
        return Response({"error": "Upload doc/docx/xls/ppt file"}, status=400)

    input_path = save_temp_file(request.FILES["file"])
    output = office_to_pdf(input_path)
    return Response({"url": build_url(output)})

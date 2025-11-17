import subprocess
from pathlib import Path
from PIL import Image
import uuid
from pdf2image import convert_from_path
from pypdf import PdfWriter
import io

TMP = Path("tmp")
TMP.mkdir(exist_ok=True)

def _out(name):
    return TMP / f"{uuid.uuid4()}_{name}"

""" ---------------- Merge ---------------- """
def merge_pdfs(paths):
    merger = PdfWriter()
    
    for path in paths:
        merger.append(str(path))  # Always convert Path → string

    output_stream = io.BytesIO()
    merger.write(output_stream)
    merger.close()

    return output_stream.getvalue() 

""" ---------------- Compress ---------------- """
def compress_pdfs(path):
    output = _out("compressed.pdf")
    cmd = [
        "gs", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/ebook",
        "-dNOPAUSE", "-dQUIET", "-dBATCH",
        f"-sOutputFile={output}", str(path)
    ]
    subprocess.run(cmd, check=True)
    return output

""" ---------------- Images to PDF ---------------- """
def images_to_pdfs(paths):
    imgs = [Image.open(p).convert("RGB") for p in paths]
    output = _out("images.pdf")
    imgs[0].save(output, save_all=True, append_images=imgs[1:])
    return output

""" ---------------- PDF to Images ---------------- """
def pdf_to_images(path):
    pages = convert_from_path(str(path), dpi=200)
    outputs = []
    for i, p in enumerate(pages):
        img = _out(f"page_{i+1}.jpg")
        p.save(img, "JPEG")
        outputs.append(img)
    return outputs

""" ---------------- Office to PDF ---------------- """
def office_to_pdf(path):
    output_dir = TMP.resolve()
    subprocess.run([
        "soffice", "--headless", "--convert-to", "pdf",
        "--outdir", str(output_dir), str(path)
    ], check=True)

    output = output_dir / (path.stem + ".pdf")
    return output

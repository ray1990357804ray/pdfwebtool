import os
import tempfile
import subprocess
from flask import Flask, request, send_file, redirect, url_for, flash, render_template
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import zipfile
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key'

UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/merge", methods=["POST"])
def merge():
    files = request.files.getlist("merge_files")
    if not files or any(not allowed_file(f.filename) for f in files):
        flash("Please upload valid PDF files for merging.", "danger")
        return redirect(url_for("index"))

    merger = PdfMerger()
    for f in files:
        merger.append(f)

    output_path = os.path.join(tempfile.gettempdir(), "merged.pdf")
    merger.write(output_path)
    merger.close()

    flash("PDFs merged successfully!", "success")
    return send_file(output_path, as_attachment=True, download_name="merged.pdf")

@app.route("/split", methods=["POST"])
def split():
    file = request.files.get("split_file")
    if not file or not allowed_file(file.filename):
        flash("Please upload a valid PDF file to split.", "danger")
        return redirect(url_for("index"))

    reader = PdfReader(file)
    temp_dir = tempfile.mkdtemp()

    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)
        page_path = os.path.join(temp_dir, f"page_{i+1}.pdf")
        with open(page_path, "wb") as f:
            writer.write(f)

    zip_path = os.path.join(tempfile.gettempdir(), "split_pages.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for pdf_file in os.listdir(temp_dir):
            zipf.write(os.path.join(temp_dir, pdf_file), pdf_file)

    flash("PDF split successfully! Download the ZIP file.", "success")
    return send_file(zip_path, as_attachment=True, download_name="split_pages.zip")

@app.route("/compress", methods=["POST"])
def compress():
    file = request.files.get("compress_file")
    if not file or not allowed_file(file.filename):
        flash("Please upload a valid PDF file to compress.", "danger")
        return redirect(url_for("index"))

    input_path = os.path.join(tempfile.gettempdir(), secure_filename(file.filename))
    file.save(input_path)

    output_path = os.path.join(tempfile.gettempdir(), "compressed_" + secure_filename(file.filename))

    gs_cmd = [
    "gs",
    "-sDEVICE=pdfwrite",
    "-dCompatibilityLevel=1.4",
    "-dPDFSETTINGS=/screen",
    "-dNOPAUSE",
    "-dQUIET",
    "-dBATCH",
    f"-sOutputFile={output_path}",
    input_path
]


    try:
        subprocess.run(gs_cmd, check=True)
        flash("PDF compressed successfully!", "success")
        return send_file(output_path, as_attachment=True, download_name="compressed_" + secure_filename(file.filename))
    except subprocess.CalledProcessError:
        flash("Compression failed. Make sure Ghostscript is installed.", "danger")
        return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
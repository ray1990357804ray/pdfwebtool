import os
import subprocess
from flask import Flask, render_template, request, send_file, redirect, url_for
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/merge', methods=['POST'])
def merge():
    files = request.files.getlist('merge_files')
    merger = PdfMerger()
    for file in files:
        filename = secure_filename(file.filename)
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)
        merger.append(path)
    output_path = os.path.join(RESULT_FOLDER, 'merged.pdf')
    merger.write(output_path)
    merger.close()
    return send_file(output_path, as_attachment=True)

@app.route('/split', methods=['POST'])
def split():
    file = request.files['split_file']
    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    reader = PdfReader(input_path)
    output_dir = os.path.join(RESULT_FOLDER, 'split_pages')
    os.makedirs(output_dir, exist_ok=True)

    zip_path = os.path.join(RESULT_FOLDER, 'split_pages.zip')

    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)
        out_path = os.path.join(output_dir, f'page_{i + 1}.pdf')
        with open(out_path, 'wb') as f:
            writer.write(f)

    # Zip the folder
    import zipfile
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for pdf in os.listdir(output_dir):
            zipf.write(os.path.join(output_dir, pdf), pdf)

    return send_file(zip_path, as_attachment=True)

@app.route('/compress', methods=['POST'])
def compress():
    file = request.files['compress_file']
    quality = request.form['quality']
    input_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
    file.save(input_path)

    output_path = os.path.join(RESULT_FOLDER, 'compressed.pdf')

    gs_executable = 'gswin64c' if os.name == 'nt' else 'gs'  # Make sure it's in PATH

    try:
        subprocess.run([
            gs_executable,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS={quality}",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={output_path}",
            input_path
        ], check=True)
    except Exception as e:
        return f"Ghostscript error: {e}", 500

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

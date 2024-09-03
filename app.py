from flask import Flask, render_template, request, send_file, flash, send_from_directory
import os
import sys
from ens_to_vtk import ens_to_vtk
from werkzeug.utils import secure_filename
import zipfile
import shutil

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Necesario para usar flash

# Configuración
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'ens', 'case', 'geo'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Asegúrate de que las carpetas existan
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        input_files = []
        
        # Handle .case and .geo files
        for file_key in ['case_file', 'geo_file']:
            if file_key not in request.files:
                flash(f'No {file_key.split("_")[0].upper()} file part')
                return render_template('upload.html')
            file = request.files[file_key]
            if file.filename == '':
                flash(f'No selected {file_key.split("_")[0].upper()} file')
                return render_template('upload.html')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                input_files.append(file_path)
        
        # Handle multiple .ens files
        if 'ens_files' not in request.files:
            flash('No ENS files part')
            return render_template('upload.html')
        ens_files = request.files.getlist('ens_files')
        if not ens_files or ens_files[0].filename == '':
            flash('No selected ENS files')
            return render_template('upload.html')
        for ens_file in ens_files:
            if ens_file and allowed_file(ens_file.filename):
                filename = secure_filename(ens_file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                ens_file.save(file_path)
                input_files.append(file_path)
        
        num_columns = int(request.form.get('num_columns', 1))
        variable_names = [request.form.get(f'var_name_{i}', f'Variable{i+1}') for i in range(num_columns)]
        
        if len(input_files) < 3:
            flash('Please upload all required files (CASE, GEO, and at least one ENS)')
            return render_template('upload.html')

        try:
            output_dir = os.path.join(app.config['OUTPUT_FOLDER'], 'temp_vtk')
            os.makedirs(output_dir, exist_ok=True)
            conversion_result = ens_to_vtk(input_files, output_dir, num_columns, variable_names)
            if conversion_result:
                # Create a ZIP file with all VTU files
                zip_filename = "vtk_files.zip"
                zip_path = os.path.join(app.config['OUTPUT_FOLDER'], zip_filename)
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for root, dirs, files in os.walk(output_dir):
                        for file in files:
                            zipf.write(os.path.join(root, file), file)
                return send_file(zip_path, as_attachment=True)
            else:
                flash('Conversion failed. Check server logs for details.')
        except Exception as e:
            flash(f'Error during conversion: {str(e)}')
        finally:
            # Limpieza de archivos
            for file in input_files:
                os.remove(file)
            shutil.rmtree(output_dir, ignore_errors=True)
            if 'zip_path' in locals() and os.path.exists(zip_path):
                os.remove(zip_path)
        
        return render_template('upload.html')
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(port=5001, debug=True)
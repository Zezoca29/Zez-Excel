from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import pandas as pd
from openpyxl import load_workbook
from io import BytesIO

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        df = read_file(filepath, filename)
        processed_file = process_file(df, filepath)
        os.remove(filepath)  # Removendo o arquivo original
        return processed_file

    else:
        return 'Arquivo não permitido'

def read_file(filepath, filename):
    if filename.endswith('.xlsx') or filename.endswith('.xls'):
        df = pd.read_excel(filepath)
    elif filename.endswith('.csv'):
        df = pd.read_csv(filepath)
    else:
        return 'Formato de arquivo não suportado'
    return df

def process_file(df, filepath):
    # Processamento dos dados (exemplo)
    # Aqui você pode adicionar a lógica para ordenar, filtrar, adicionar coluna calculada, etc.

    # Salvando o arquivo convertido
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    writer.book = load_workbook(filepath)
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.save()
    output.seek(0)

    return output.getvalue(), 200, {'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'Content-Disposition': 'attachment; filename=converted.xlsx'}

if __name__ == '__main__':
    app.run(debug=True)

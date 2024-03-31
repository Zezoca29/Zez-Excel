import os
from flask import Flask, jsonify, redirect, render_template, request, url_for, send_file
from werkzeug.utils import secure_filename
import pandas as pd
import json
from plotly import express as px
import xml.etree.ElementTree as ET
import sqlite3
import plotly.express as px
from datetime import datetime
import plotly.graph_objs as go

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def convert_to_csv(data):
    csv_data = data.to_csv(index=False)
    return csv_data

def convert_to_json(data):
    json_data = data.to_json(orient='records')
    return json_data

def convert_to_xml(data):
    root = ET.Element('data')
    for _, row in data.iterrows():
        item = ET.SubElement(root, 'item')
        for col_name, col_value in row.items():
            sub_element = ET.SubElement(item, col_name)
            sub_element.text = str(col_value)
    xml_data = ET.tostring(root, encoding='unicode')
    return xml_data

def convert_to_sql(data):
    table_name = 'data_table'
    sql_create_table = f'CREATE TABLE {table_name} ('
    sql_insert_into = f'INSERT INTO {table_name} VALUES '

    for idx, row in data.iterrows():
        if idx == 0:
            sql_create_table += ', '.join([f'{col} TEXT' for col in row.index])
        sql_insert_into += f'({", ".join([repr(val) for val in row.values])}), '

    sql_create_table += ');'
    sql_insert_into = sql_insert_into[:-2] + ';'

    return f'{sql_create_table} {sql_insert_into}'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/converter')
def converter():
    return render_template('converter.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'Nenhum arquivo enviado'
    
    file = request.files['file']
    
    if file.filename == '':
        return 'Nenhum arquivo selecionado'
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        df = pd.read_excel(filepath)

        conversions = {
            'CSV': convert_to_csv,
            'JSON': convert_to_json,
            'XML': convert_to_xml,
            'SQL': convert_to_sql
        }

        conversion = request.form.get('conversion')
        if conversion not in conversions:
            return 'Conversão não suportada'

        data = conversions[conversion](df)
        extension = conversion.lower()

        converted_filename = f'converted_{filename[:-5]}.{extension}'
        converted_filepath = os.path.join(app.config['UPLOAD_FOLDER'], converted_filename)
        with open(converted_filepath, 'w') as f:
            f.write(data)

        download_link = url_for('download_file', filename=converted_filename)
        return render_template('converter.html', filename=filename, download_link=download_link)

    else:
        return 'Arquivo não permitido'

@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(filepath, as_attachment=True)

@app.route('/manipular')
def manipular():
    return render_template('Manipule.html')

def convert_excel_to_json(filepath):
    df = pd.read_excel(filepath)
    return df.to_json(orient='records')

@app.route('/upload-excel', methods=['POST'])
def upload_excel():
    if 'file' not in request.files:
        return 'Nenhum arquivo enviado'
    
    file = request.files['file']
    
    if file.filename == '':
        return 'Nenhum arquivo selecionado'
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        json_data = convert_excel_to_json(filepath)
        return json_data

    else:
        return 'Arquivo não permitido'

@app.route('/analise_dados')
def analise_dados():
    return render_template('analise.html')

@app.route('/uploadanalises', methods=['POST'])
def uploadanalises():
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        df = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        columns = df.columns.tolist()
        data = df.to_dict(orient='records')
        return jsonify({'columns': columns, 'data': data})
    return jsonify({'error': 'No file provided'})


def get_column_titles(file):
    df = pd.read_excel(file)
    return df.columns.tolist()

import plotly.express as px

@app.route('/plot', methods=['POST'])
def plot():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400

        column1 = request.form['column1']
        column2 = request.form['column2']
        chart_type = request.form['chart_type']

        # Lendo o arquivo Excel
        df = pd.read_excel(file)

        # Gerando o gráfico com os dados do arquivo
        if chart_type == 'pie':
            fig = px.pie(df, names=column1, values=column2, title='Gráfico de Pizza')
        elif chart_type == 'bar':
            fig = px.bar(df, x=column1, y=column2, title='Gráfico de Barras')
        elif chart_type == 'line':
            fig = px.line(df, x=column1, y=column2, title='Gráfico de Linhas')
        elif chart_type == 'scatter':
            fig = px.scatter(df, x=column1, y=column2, title='Gráfico de Dispersão')

        # Salvar o gráfico como HTML para ser exibido na página
        graph_html = fig.to_html(full_html=False)

        return render_template('grafico.html', graph_html=graph_html)
    except Exception as e:
        return f"Erro ao processar a requisição: {e}", 400


@app.route('/uploadgrafic', methods=['GET'])
def upload_grafico():
    return render_template('grafico.html')

@app.route('/get_columns', methods=['POST'])
def get_columns():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400

    # Lendo o arquivo Excel
    df = pd.read_excel(file)

    # Obtendo os títulos das colunas
    colunas = df.columns.tolist()

    # Retornando os títulos das colunas como JSON
    return jsonify(colunas)

if __name__ == '__main__':
    app.run(debug=True)


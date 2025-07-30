from flask import Flask, render_template, request, redirect, url_for
import csv
import requests
import os

app = Flask(__name__)

# Configuración
API_BASE_URL = "https://api.dell.com/support/v2/asset"
OUTPUT_FILE = "output.csv"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/procesar', methods=['POST'])
def procesar():
    if 'archivo' not in request.files:
        return redirect(url_for('index'))
    
    archivo = request.files['archivo']
    if archivo.filename == '':
        return redirect(url_for('index'))
    
    # Guardar el archivo temporalmente
    ruta_archivo = os.path.join(UPLOAD_FOLDER, archivo.filename)
    archivo.save(ruta_archivo)
    
    # Procesar el archivo
    resultados = []
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        lector = csv.DictReader(f)
        for fila in lector:
            service_tag = fila.get('ServiceTag')  # Asegúrate que la columna se llame 'ServiceTag'
            if service_tag:
                try:
                    # Consultar API de Dell
                    respuesta = requests.get(f"{API_BASE_URL}/{service_tag}")
                    if respuesta.status_code == 200:
                        datos = respuesta.json()
                        resultados.append({
                            'ServiceTag': service_tag,
                            'Datos': datos
                        })
                    else:
                        resultados.append({
                            'ServiceTag': service_tag,
                            'Error': f"Error API: {respuesta.status_code}"
                        })
                except Exception as e:
                    resultados.append({
                        'ServiceTag': service_tag,
                        'Error': str(e)
                    })
    
    # Guardar resultados en output.csv
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['ServiceTag', 'Datos', 'Error'])
        writer.writeheader()
        for res in resultados:
            writer.writerow({
                'ServiceTag': res['ServiceTag'],
                'Datos': str(res.get('Datos', '')),
                'Error': str(res.get('Error', ''))
            })
    
    return render_template('resultado.html', resultados=resultados)

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, jsonify
import pydicom
from werkzeug.utils import secure_filename
import os  # Adicionei a importação da biblioteca 'os'

app = Flask(__name__)

def anonimize_dicom(file):
    # Salvar o arquivo temporário
    temp_path = secure_filename(file.filename)
    file.save(temp_path)

    # Carregar o arquivo DICOM
    ds = pydicom.dcmread(temp_path)

    # Anonimizar os metadados desejados
    ds.PatientName = "Metadado Anonimizado pela API"
    ds.PatientSex = "Metadado Anonimizado pela API"
    ds.PatientBirthDate = "000000"
    ds.PatientID = "000000"
    ds.PatientAge = "00"
    ds.PatientSize = "00"
    ds.PatientWeight = "00"

    # Criar o caminho para o novo arquivo anonimizado
    output_file = "anonimized_" + secure_filename(file.filename)

    # Salvar o arquivo DICOM anonimizado
    ds.save_as(output_file)

    # Remover o arquivo temporário
    os.remove(temp_path)

    return output_file

@app.route('/anonimize', methods=['POST'])
def anonimize():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # Anonimizar o arquivo DICOM
        result_file = anonimize_dicom(file)

        return jsonify({'message': 'Metadados DICOM anonimizados com sucesso.', 'anonimized_file': result_file})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

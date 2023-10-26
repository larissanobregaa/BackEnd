from flask import Flask, request, jsonify
import pydicom
import os

app = Flask(__name__)

def anonimize_dicom(dicom_file):
    ds = pydicom.dcmread(dicom_file)

    # Anonimizar os metadados desejados

    ds.PatientName = "Metadado Anonimizado pela API"
    ds.PatientSex = "Metadado Anonimizado pela API"
    ds.PatientBirthDate = "000000"
    ds.PatientID = "000000"
    ds.PatientAge = "00"
    ds.PatientSize = "00"
    ds.PatientWeight = "00"

    return ds

@app.route('/anonimize', methods=['POST'])
def anonimize():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        try:
            anonimized_ds = anonimize_dicom(file)
            output_file = "anonimized_" + file.filename
            anonimized_ds.save_as(output_file)
            return jsonify({'message': 'Metadados DICOM anonimizados e salvos com sucesso como ' + output_file})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

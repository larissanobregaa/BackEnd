from flask import Flask, request, jsonify
import pydicom
import os
import SimpleITK as sitk
import numpy as np

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

def segment_dicom_image(dicom_file):
    ds = pydicom.dcmread(dicom_file)

    # Obter matriz de pixel
    pixel_array = ds.pixel_array

    # Converter para imagem SimpleITK
    image = sitk.GetImageFromArray(pixel_array)

    # Segmentação usando SimpleITK (exemplo simples - ajuste conforme necessário)
    segmentation = sitk.BinaryThreshold(image, lowerThreshold=100, upperThreshold=200)

    # Converter imagem segmentada para numpy array
    segmented_array = sitk.GetArrayFromImage(segmentation)

    return segmented_array

@app.route('/segment', methods=['POST'])
def segment():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        try:
            # Segmentar imagem DICOM
            segmented_array = segment_dicom_image(file)

            # Salvar imagem segmentada
            segmented_output_file = "segmented_" + file.filename + ".npy"
            np.save(segmented_output_file, segmented_array)

            return jsonify({'message': 'Imagem DICOM segmentada e salva com sucesso como ' + segmented_output_file})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, jsonify, send_file
import pydicom
import os
from pathlib import Path
from werkzeug.utils import secure_filename
import numpy as np

app = Flask(__name__)

def segment_image(dicom_file, segmentation_parameters):
    try:
        # Caminho do diretório para salvar os arquivos processados
        processed_dir = os.path.join(os.getcwd(), 'processed')
        Path(processed_dir).mkdir(parents=True, exist_ok=True)

        # Leitura do arquivo DICOM
        dicom_dataset = pydicom.dcmread(dicom_file)

        # Anonimização dos metadados
        anonymize_dicom(dicom_dataset)

        # Obtenha os dados da imagem como numpy array
        image_array = dicom_dataset.pixel_array

        # Implementação genérica de segmentação usando o método de limiarização
        lower_threshold = segmentation_parameters.get('lower_threshold', 0)
        upper_threshold = segmentation_parameters.get('upper_threshold', 255)
        segmented_array = np.where((image_array >= lower_threshold) & (image_array <= upper_threshold), 1, 0)

        # Nome do novo arquivo DICOM com "processed"
        base_name = secure_filename(dicom_file.filename).split('.')[0]
        processed_dicom_path = os.path.join(processed_dir, f'processed_{base_name}.dcm')

        # Salve o DICOM
        save_dicom(segmented_array, dicom_dataset, processed_dicom_path)

        return processed_dicom_path

    except Exception as e:
        raise e

def anonymize_dicom(dicom_dataset):
    # Anonimização dos metadados conforme necessário
    dicom_dataset.PatientName = "Anonymous"
    dicom_dataset.PatientID = "AnonID"
    dicom_dataset.PatientBirthDate = "19000101"
    dicom_dataset.InstitutionName = "Anonymous Institution"
    dicom_dataset.InstitutionAddress = "Anonymous Address"
    # Adicione mais campos conforme necessário

def save_dicom(pixel_array, original_dicom, save_path):
    # Crie um novo objeto DICOM para o arquivo atualizado
    updated_dicom = pydicom.Dataset()

    # Copie os metadados anonimizados do DICOM original para o DICOM atualizado
    updated_dicom.update(original_dicom)

    # Atualize outros metadados conforme necessário
    updated_dicom.PatientName = "Anonymous"
    updated_dicom.PatientID = "AnonID"
    updated_dicom.PatientBirthDate = "19000101"
    updated_dicom.InstitutionName = "Anonymous Institution"
    updated_dicom.InstitutionAddress = "Anonymous Address"
    # Adicione mais campos conforme necessário

    # Salve a imagem segmentada no formato DICOM no novo arquivo
    updated_dicom.PixelData = pixel_array.tobytes()
    updated_dicom.Rows, updated_dicom.Columns = pixel_array.shape
    updated_dicom.save_as(save_path.replace('.dcm', '_updated.dcm'))

# ...

@app.route('/segment', methods=['POST'])
def segment():
    try:
        # Verifique se o pedido contém um arquivo DICOM
        if 'file' not in request.files:
            return jsonify({'error': 'No DICOM file provided'}), 400

        dicom_file = request.files['file']

        # Parâmetros de segmentação definidos pela IA (ajuste conforme necessário)
        segmentation_parameters = {
            'lower_threshold': 100,
            'upper_threshold': 255
        }

        # Realize a segmentação
        processed_dicom_path = segment_image(dicom_file, segmentation_parameters)

        # Exiba mensagem de sucesso
        result_message = (
            f"Imagem DICOM foi anonimizada e segmentada com sucesso.\n"
            f"Caminho do arquivo processado: {processed_dicom_path}"
        )

        # Retorna o arquivo processado como resposta
        return send_file(processed_dicom_path), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ...

if __name__ == '__main__':
    app.run(debug=True, threaded=True)

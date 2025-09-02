GYB Classification Model

gyb_classification_model is a Python package for classifying medical documents.
It provides a simple interface so you can run predictions directly on raw text.

📦 Installation
pip install gyb-classification-model


🚀 Usage
from gyb_classification_model import predictor

text = '''
        18 19 20 L.HAIG BEMBRY SIDER,JEFFREY # 3 Left Shoulder Arthroscopy 7/24/2025
    '''

predictor = predictor.predict_text(text)

print(predictor)

from gyb_classification_model import predictor

text = "AOB"

processed_text = predictor.preprocess_text(text)
category = predictor.predict_text(processed_text)

print(category['category'])


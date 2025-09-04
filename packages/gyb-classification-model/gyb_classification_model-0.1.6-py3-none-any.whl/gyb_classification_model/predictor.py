import pickle
import re
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import os
import nltk
from nltk.stem import WordNetLemmatizer

nltk.download('punkt')
nltk.download('punkt_tab')

nltk.download('stopwords')
nltk.download('wordnet')

script_dir = os.path.dirname(os.path.abspath(__file__))
base_path = os.path.abspath(os.path.join(script_dir, '../models'))

# Load files
with open(os.path.join(base_path, "vectorizerV28.pkl"), "rb") as f:
    tfidf_vectorizer = pickle.load(f)

with open(os.path.join(base_path, "label_mapV28.pkl"), "rb") as f:
    reverse_label_map = pickle.load(f)

with open(os.path.join(base_path, "textClassificationModelV28.pkl"), "rb") as f:
    model = pickle.load(f)


# Load files for order
with open(os.path.join(base_path, "OnlyDeliverSlipPharmOrderVectorizerV4.pkl"), "rb") as f:
    delivery_order_vectorizer = pickle.load(f)

with open(os.path.join(base_path, "OnlyDeliverSlipPharmOrderlabel_mapV4.pkl"), "rb") as f:
    delivery_order_label_map = pickle.load(f)

with open(os.path.join(base_path, "OnlyDeliverSlipPharmOrderModelV4.pkl"), "rb") as f:
    delivery_order_model = pickle.load(f)


# Load files for Medical Reports
with open(os.path.join(base_path, "MedicalReportVectorizerV9.pkl"), "rb") as f:
    medical_vectorizer = pickle.load(f)

with open(os.path.join(base_path, "MedicalReportLabelMapV9.pkl"), "rb") as f:
    reverse_medical_map = pickle.load(f)

with open(os.path.join(base_path, "MedicalReportClassifierV9.pkl"), "rb") as f:
    medical_model = pickle.load(f)


# Preprocessing text
def preprocess_text(text):
    if not isinstance(text, str) or not text.strip():
        return "misc"

    text = text.lower()

    # Extract and preserve URLs
    urls = re.findall(r'(https?://\S+|www\.\S+)', text)

    # Remove URLs temporarily from the text
    text_without_urls = re.sub(r'(https?://\S+|www\.\S+)', '', text)

    # Remove punctuation from the rest of the text
    text_without_urls = text_without_urls.translate(str.maketrans('', '', string.punctuation))

    # Normalize whitespace
    text_without_urls = re.sub(r'\s+', ' ', text_without_urls).strip()

    # Tokenize
    tokens = word_tokenize(text_without_urls)

    # Remove stopwords and short tokens
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words and len(token) > 2]

    # Lemmatize
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]

    # Combine tokens with preserved URLs
    tokens.extend(urls)

    # If no meaningful tokens or URLs remain, return 'misc'
    if not tokens:
        return "misc"

    return ' '.join(tokens)

# Prediction
def predict_text(input_text):
    processed_text = preprocess_text(input_text)

    input_vector = tfidf_vectorizer.transform([processed_text])

    predicted_label = model.predict(input_vector)[0]
    predicted_proba = model.predict_proba(input_vector)[0]
    label_index = list(model.classes_).index(predicted_label)
    probability = predicted_proba[label_index]

    category = reverse_label_map.get(predicted_label)

    if category == "EOB_EOR" and probability <= 0.5:
        category = "MISC"

    order_delivery = ["DELIVERY_SLIP_ORDER"]
    medical_reports = ["MEDICAL_REPORT"]

    if category in order_delivery:
        input_vector = delivery_order_vectorizer.transform([processed_text])

        predicted_label = delivery_order_model.predict(input_vector)[0]
        predicted_proba = delivery_order_model.predict_proba(input_vector)[0]
        label_index = list(delivery_order_model.classes_).index(predicted_label)
        probability = predicted_proba[label_index]

        category = delivery_order_label_map.get(predicted_label)

    if category in medical_reports:
        input_vector = medical_vectorizer.transform([processed_text])

        predicted_label = medical_model.predict(input_vector)[0]
        predicted_proba = medical_model.predict_proba(input_vector)[0]
        label_index = list(medical_model.classes_).index(predicted_label)
        probability = predicted_proba[label_index]

        category = reverse_medical_map.get(predicted_label)

    result = {
        "category": category,
        "probability": round(probability, 4)
    }

    return result
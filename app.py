from flask import Flask, render_template, request, jsonify
from supabase import create_client, Client
import joblib
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize Flask app
app = Flask(__name__)

# Load models
model = joblib.load('xss_classifier.pkl')
vectorizer = joblib.load('tfidf_vectorizer.pkl')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    sentence = request.form['sentence']
    X_input = vectorizer.transform([sentence])
    prediction = model.predict(X_input)
    result = "XSS Threat" if prediction[0] == 1 else "Non-XSS"

    # Save to Supabase
    response = supabase.table("XSSRecord").insert({
        "input_text": sentence,
        "prediction": result
    }).execute()

    if response.status_code == 201:
        print("Record added successfully!")

    return render_template('index.html', prediction=result)

@app.route('/records')
def records():
    response = supabase.table("XSSRecord").select("*").execute()
    if response.status_code == 200:
        all_records = response.data
    else:
        all_records = []
    
    return render_template('records.html', records=all_records)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)

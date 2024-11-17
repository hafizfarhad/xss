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
    response = supabase.table("records").insert({
        "input_text": sentence,
        "prediction": result
    }).execute()

    # Check response directly
    if response.data:
        print("Record added successfully!")
    elif response.errors:
        print(f"Error inserting record: {response.errors}")
    else:
        print("Unexpected response:", response)

    return render_template('index.html', prediction=result)
    
@app.route('/records')
def records():
    response = supabase.table("records").select("*").execute()

    # Check response directly
    if response.data:  # Data exists, meaning the query was successful
        all_records = response.data
    elif response.errors:  # Check if there are errors
        print(f"Error fetching records: {response.errors}")
        all_records = []
    else:  # Unexpected response
        print("Unexpected response:", response)
        all_records = []

    return render_template('records.html', records=all_records)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)

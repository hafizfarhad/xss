from flask import Flask, render_template, request
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
def landing_page():
    return render_template('index.html')  # Landing page

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        sentence = request.form['sentence']
        X_input = vectorizer.transform([sentence])
        prediction = model.predict(X_input)
        prediction_bool = bool(prediction[0])  # Convert to boolean (0 or 1)
        result = "The given script is possibly a threat (XSS)" if prediction_bool else "The given script is safe (Non-XSS)"

        # Save to Supabase with the new column name 'is_xss'
        response = supabase.table("records").insert({
            "input_text": sentence,
            "is_xss": prediction_bool
        }).execute()

        return render_template('predict.html', prediction=result)

    return render_template('predict.html')  # Prediction page (GET)

@app.route('/about')
def about():
    return render_template('about.html')  # About page

@app.route('/records')
def records():
    response = supabase.table("records").select("*").execute()
    all_records = response.data if response.data else []
    return render_template('records.html', records=all_records)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv('PORT', 5000)))
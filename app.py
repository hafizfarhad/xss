from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
import os

# Initialize the Flask app
app = Flask(__name__)

# Database configuration
# For Vercel, SQLite database will not persist after the serverless function terminates.
# You can consider using a cloud database (e.g., PostgreSQL, MySQL, or others).
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///xss_data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database model for storing inputs and outputs
class XSSRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    input_text = db.Column(db.String(500), nullable=False)
    prediction = db.Column(db.String(50), nullable=False)

# Create the database (only needs to be run once)
with app.app_context():
    db.create_all()

# Load the trained model and vectorizer (make sure these files are deployed with the app)
model = joblib.load('xss_classifier.pkl')  
vectorizer = joblib.load('tfidf_vectorizer.pkl')

# Home route to display the form
@app.route('/')
def home():
    return render_template('index.html')  # This will render your HTML form

# Route to handle prediction from form submission
@app.route('/predict', methods=['POST'])
def predict():
    sentence = request.form['sentence']  # Get the sentence from the form
    # Vectorize the input sentence
    X_input = vectorizer.transform([sentence])
    
    # Predict using the loaded model
    prediction = model.predict(X_input)
    result = "XSS Threat" if prediction[0] == 1 else "Non-XSS"
    
    # Save the input and prediction to the database
    new_record = XSSRecord(input_text=sentence, prediction=result)
    db.session.add(new_record)
    db.session.commit()
    
    # Return the result
    return render_template('index.html', prediction=result)

# API route to handle JSON requests (for testing)
@app.route('/api/predict', methods=['POST'])
def api_predict():
    data = request.get_json()  # Get JSON input
    sentence = data['sentence']
    
    # Vectorize the input
    X_input = vectorizer.transform([sentence])
    
    # Make the prediction
    prediction = model.predict(X_input)
    result = "XSS Threat" if prediction[0] == 1 else "Non-XSS"
    
    # Save the input and prediction to the database
    new_record = XSSRecord(input_text=sentence, prediction=result)
    db.session.add(new_record)
    db.session.commit()
    
    # Return JSON response
    return jsonify({'prediction': result})

# New route to display records
@app.route('/records')
def records():
    all_records = XSSRecord.query.all()  # Fetch all records from the database
    return render_template('records.html', records=all_records)

# Run the Flask app only if we're not deploying to Vercel or another platform
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)

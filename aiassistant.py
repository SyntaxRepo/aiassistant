from flask import Flask, render_template, request, jsonify
import cohere
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file during local development.
# On platforms like Render, these will be set directly in the environment.
load_dotenv()

app = Flask(__name__)

# Initialize Cohere client with error handling.
# The API key is fetched from environment variables, ensuring it's not hardcoded.
# This is crucial for security when deploying.
cohere_api_key = os.getenv('COHERE_API_KEY') or os.getenv('CO_API_KEY')
if not cohere_api_key:
    # Raise an error if the API key is not found, preventing the app from starting.
    raise ValueError("No Cohere API key found. Please set COHERE_API_KEY in .env file or as an environment variable.")

co = cohere.Client(cohere_api_key)  # Initialize with the validated key

@app.route('/')
def home():
    # Renders the index.html file.
    # Ensure index.html is in a 'templates' subfolder relative to this file.
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data['message']
        
        # Convert user message to lowercase for case-insensitive comparison
        lower_user_message = user_message.lower()

        # Check for a specific question about the AI's creator.
        # This is a hardcoded response for specific queries.
        if "who made you" in lower_user_message or "who created you" in lower_user_message or "who develop you" in lower_user_message:
            ai_response = "Jomer John Valmoria Alvarado, a Bachelor Of Science In Information Technology who graduated at St. Vincent's College Incorporated."
        else:
            # If it's not the specific question, use the Cohere API to generate a response.
            # Adjusted temperature to 0.0 for more direct and deterministic responses.
            response = co.chat(
                message=user_message,
                model="command",
                temperature=0.0
            )
            ai_response = response.text
        
        # Return the AI's response and a timestamp as JSON.
        return jsonify({
            'response': ai_response,
            'timestamp': datetime.now().strftime("%I:%M %p")
        })
        
    except Exception as e:
        # Log any errors and return a generic error message to the client.
        print(f"Error: {str(e)}")
        return jsonify({
            'response': "Sorry, I'm having trouble processing your request.",
            'timestamp': datetime.now().strftime("%I:%M %p")
        }), 500

if __name__ == '__main__':
    # This block runs when the script is executed directly (e.g., during local development).
    # When deployed on Render (or similar platforms), Gunicorn will manage running the app.
    # Render automatically provides the PORT environment variable.
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

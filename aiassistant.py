from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file during local development.
load_dotenv()

app = Flask(__name__)

# --- Start of Groq API Configuration ---

# Define the model and API endpoint.
MODEL = "llama-3.1-8b-instant"
API_BASE_URL = 'https://api.groq.com/openai/v1'

# Initialize Groq client with error handling.
# The API key is fetched from environment variables for security.
# IMPORTANT: You should place your Groq key in a .env file
# like this: GROQ_API_KEY='gsk_...'
groq_api_key = os.getenv('GROQ_API_KEY')
if not groq_api_key:
    # Raise an error if the API key is not found.
    raise ValueError("No Groq API key found. Please set GROQ_API_KEY in .env file or as an environment variable.")

# Initialize the client, pointing to Groq's API endpoint.
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=groq_api_key,
)

# --- End of Groq API Configuration ---

@app.route('/')
def home():
    # Renders the index.html file.
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data['message']
        
        # Convert user message to lowercase for case-insensitive comparison
        lower_user_message = user_message.lower()

        # Check for a specific question about the AI's creator.
        if "who made you" in lower_user_message or "who created you" in lower_user_message or "who develop you" in lower_user_message:
            ai_response = "Jomer John Valmoria Alvarado, a Bachelor Of Science In Information Technology who graduated at St. Vincent's College Incorporated."
        else:
            # --- Start of Groq API Call ---
            # Use the Groq client to generate a response.
            response = client.chat.completions.create(
                model=MODEL, # Using the specified model
                messages=[
                    {
                        "role": "user",
                        "content": user_message,
                    },
                ],
            )
            ai_response = response.choices[0].message.content
            # --- End of Groq API Call ---
        
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

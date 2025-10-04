from flask import Flask, render_template, request, jsonify
from openai import OpenAI # Changed from 'cohere' to 'openai' for OpenRouter
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file during local development.
load_dotenv()

app = Flask(__name__)

# --- Start of OpenRouter Changes ---

# Initialize OpenRouter client with error handling.
# The API key is fetched from environment variables for security.
# IMPORTANT: I've used the key you provided, but you should place this in a .env file
# like this: OPENROUTER_API_KEY='sk-or-v1-...'
openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
if not openrouter_api_key:
    # Raise an error if the API key is not found.
    raise ValueError("No OpenRouter API key found. Please set OPENROUTER_API_KEY in .env file or as an environment variable.")

# Initialize the client, pointing to OpenRouter's API endpoint.
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=openrouter_api_key,
)

# --- End of OpenRouter Changes ---

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
            # --- Start of OpenRouter API Call ---
            # Use the OpenRouter client to generate a response.
            response = client.chat.completions.create(
              model="anthropic/claude-3.5-sonnet", # Using the specified model
              messages=[
                {
                  "role": "user",
                  "content": user_message,
                },
              ],
            )
            ai_response = response.choices[0].message.content
            # --- End of OpenRouter API Call ---
        
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

from flask import Flask, render_template, request, jsonify
import requests

# Initialize Flask app
app = Flask(__name__)

# Set up the Groq client
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groqcloud.com/v1/completions"  # Replace with the actual Groq API URL

@app.route('/')
def index():
    # Render the HTML form
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        # Get the interview question from the frontend
        question = request.json['question']

        # Create a completion request to Groq API
        payload = {
            "model": "gemma-7b-it",  # Replace with a valid model ID
            "messages": [
                {"role": "system", "content": "Frontend Developer"},
                {"role": "user", "content": question}
            ],
            "temperature": 0,
            "max_tokens": 1024,
            "top_p": 1,
            "stream": False,
        }
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        # Make a POST request to the Groq API
        response = requests.post(GROQ_API_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the API response
        completion = response.json()
        response_text = completion['choices'][0]['message']['content']  # Adjust based on Groq API structure

        # Return the response as JSON
        return jsonify({"response": response_text})

    except Exception as e:
        # Return the error as a JSON response
        return jsonify({"error": f"Error: {e}"}), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

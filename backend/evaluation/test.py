from flask import Flask, render_template, request, jsonify
from groq import Groq

# Initialize Flask app
app = Flask(__name__)

# Set up the Groq client with your API key
client = Groq(api_key='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')

@app.route('/')
def index():
    # Render the HTML form
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        # Get the interview question from the frontend
        question = request.json['question']
        
        # Create a completion request using the correct model ID
        completion = client.chat.completions.create(
            model="gemma-7b-it",  # Replace with a valid model ID from the Groq platform
            messages=[
                {
                    "role": "system",
                    "content": "Frontend Developer"
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            temperature=0,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )

        # Print the entire response to understand its structure
        print(completion)

        # Extract the response from the model - modify this based on the actual structure
        response_text = completion.choices[0].message.content  # Adjust based on structure

        # Return the response as JSON
        return jsonify({"response": response_text})

    # Use generic exception handling to capture all errors
    except Exception as e:
        return jsonify({"error": f"Error: {e}"}), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
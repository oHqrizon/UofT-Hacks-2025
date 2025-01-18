import os

from groq import Groq

client = Groq(
    api_key= "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",
)
#import the education variable from the home.js file
education = "high school"
topic = "math"

# Function to read the transcription file
def read_transcription_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Path to the transcription file
transcription_file_path = 'speech/transcription.txt'

# Read the transcription file and store its content in a variable
transcription_content = read_transcription_file(transcription_file_path)

# Use the transcription content in the chat completion
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": (
                f'You are a {education} student. You are judging the transcript below based on the following criteria: '
                '1. How much you can understand the speaker based on the language (diction) they use and your role. '
                '2. How much they pause and or stutter '
                f'3. How much the content is relevant to the {topic} topic. Please provide 1. A percentage overall score for how well they followed the criteria '
                '2. Strengths of the speaker 3. Improvements that can be made to the speaker. '
                f'The transcription is: {transcription_content}'

                f' In addition, only provide the score and the explanation, no other text. Also do not add any styling to the text and seperate the text with a new line'
            )
        }
    ],
    model="llama3-70b-8192",
)

print(chat_completion.choices[0].message.content)
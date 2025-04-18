from flask import Flask, request, jsonify
import openai
from langdetect import detect

app = Flask(__name__)

# Replace with your actual key
openai.api_key = "whatsapp"

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Tamil Translator and Grammar Correction API"})

@app.route('/api/translate', methods=['POST'])
def translator():
    data = request.get_json()
    user_input = data.get('text', '')

    # Detect language using langdetect
    try:
        lang = detect(user_input)
    except Exception as e:
        lang = 'unknown'

    # If input is already in Tamil, return it directly
    if lang == 'ta':
        translated_text = user_input
    else:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a bot that converts English / Tanglish text to Tamil. Return only the Tamil translation."
                },
                {"role": "user", "content": user_input}
            ]
        )
        translated_text = response['choices'][0]['message']['content']

    return jsonify({
        "input": user_input,
        "language_detected": lang,
        "translation": translated_text
    })

@app.route('/api/grammar', methods=['POST'])
def grammar():
    data = request.get_json()
    user_input = data.get('text', '')

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a bot that corrects grammatical mistakes in Tamil text. Please correct any mistakes and return the corrected text in Tamil. and also explain the mistake in both tamil and english discripitively"
            },
            {"role": "user", "content": user_input}
        ]
    )

    corrected_text = response['choices'][0]['message']['content']

    return jsonify({
        "input": user_input,
        "correction_and_explanation": corrected_text
    })

@app.route('/api/history', methods=['GET'])
def history():
    return jsonify({"message": "History endpoint is under construction or not implemented."})

if __name__ == "__main__":
    app.run(debug=True)

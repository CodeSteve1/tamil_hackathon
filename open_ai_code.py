from flask import Flask, render_template, request
import openai
from langdetect import detect
# this code will not work on its own you have to install flask and openai==0.28

app = Flask(__name__)

# Replace with your actual key
openai.api_key = "check whatsapp for the api key"

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/translator', methods=['GET', 'POST'])
def translator():
    translated_text = ''
    if request.method == 'POST':
        user_input = request.form['text']
        # Detect language using langdetect
        try:
            lang = detect(user_input)
        except Exception as e:
            lang = 'unknown'

        # If input is already in Tamil, return it directly, otherwise translate it
        if lang == 'ta':
            translated_text = user_input  
        else:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a bot that converts English / Tanglish text to Tamil. Return only the Tamil translation."
                    },
                    {"role": "user", "content": user_input}
                ]
            )
            translated_text = response['choices'][0]['message']['content']
    return render_template('translator.html', translated_text=translated_text)

@app.route('/grammar', methods=['GET', 'POST'])
def grammar():
    corrected_text = ''
    if request.method == 'POST':
        user_input = request.form['text']
        # Use OpenAI API to correct grammatical mistakes in Tamil
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
        print(corrected_text)
    return render_template('grammar.html', corrected_text=corrected_text)

if __name__ == "__main__":
    app.run(debug=True)

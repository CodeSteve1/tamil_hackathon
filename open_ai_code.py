from flask import Flask, render_template, request
import openai
from langdetect import detect

app = Flask(__name__)

openai.api_key = "check whatsapp for code"

@app.route('/', methods=['GET', 'POST'])
def index():
    translated_text = ''
    if request.method == 'POST':
        user_input = request.form['text']
        try:
            lang = detect(user_input)
        except:
            lang = 'unknown'

        if lang == 'ta':
            translated_text = user_input  # Already in Tamil
        else:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a bot that converts English / Tanglish text to Tamil. Return only the Tamil translation."},
                    {"role": "user", "content": user_input}
                ]
            )
            translated_text = response['choices'][0]['message']['content']

    return render_template('index.html', translated_text=translated_text)

if __name__ == "__main__":
    app.run(debug=True)

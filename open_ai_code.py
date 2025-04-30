# app.py
from flask import Flask, render_template, request
import openai
from langdetect import detect
import subprocess

# Move your model‐list here:
LLM_MODELS = [
    {'id': 'openai:gpt-4o',      'name': 'OpenAI GPT-4o'},
    {'id': 'openai:gpt-4o-mini', 'name': 'OpenAI GPT-4o Mini'},
    {'id': 'llama3.2',           'name': 'LLaMA 3.2 (Ollama CLI)'},
    {'id': 'gemma3:27B',             'name': 'Gemma 3 (Ollama CLI)'},
]

app = Flask(__name__)
openai.api_key = "sk-..."

def generate_with_ollama(prompt: str, model: str) -> str:
    """Shell out to `ollama run <model> <prompt>` and capture Unicode safely."""
    command = ["ollama", "run", model, prompt]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        return result.stdout.strip() or ""
    except subprocess.CalledProcessError as e:
        print("Error running Ollama CLI:", e)
        return "Error generating response."

def use_ollama_model(user_input: str, model: str, system_prompt: str) -> str:
    """
    Prepend the system prompt to the user input and send it
    to the CLI as one block.
    """
    full_prompt = f"{system_prompt}\n\nUser: {user_input}\n\nAssistant:"
    return generate_with_ollama(full_prompt, model)

def use_openai_model(user_input: str, model: str, system_prompt: str) -> str:
    resp = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system",  "content": system_prompt},
            {"role": "user",    "content": user_input}
        ]
    )
    return resp.choices[0].message.content

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/translator', methods=['GET','POST'])
def translator():
    translated_text = ""
    user_input     = request.form.get('text', "")
    selected_model = request.form.get('model', LLM_MODELS[0]['id'])

    if request.method == 'POST' and user_input:
        try:
            lang = detect(user_input)
        except:
            lang = "unknown"

        if lang == 'ta':
            translated_text = user_input
        else:
            system_prompt = (
                "You are a bot that converts English / Tanglish text "
                "to Tamil. Return only the Tamil translation."
            )
            if selected_model.startswith("openai:"):
                _, model_key = selected_model.split(":",1)
                translated_text = use_openai_model(user_input, model_key, system_prompt)
            else:
                # CLI‐based models
                translated_text = use_ollama_model(user_input, selected_model, system_prompt)

    return render_template(
        'translator.html',
        llm_models=LLM_MODELS,
        selected_model=selected_model,
        user_input=user_input,
        translated_text=translated_text
    )

@app.route('/grammar', methods=['GET','POST'])
def grammar():
    corrected_text = ""
    user_input     = request.form.get('text', "")
    selected_model = request.form.get('model', LLM_MODELS[0]['id'])

    if request.method == 'POST' and user_input:
        system_prompt = (
            "You are a bot that corrects grammatical mistakes in Tamil text. "
            "Please correct any mistakes and return the corrected text in Tamil, "
            "and also explain the mistake in both Tamil and English descriptively."
        )
        if selected_model.startswith("openai:"):
            _, model_key = selected_model.split(":",1)
            corrected_text = use_openai_model(user_input, model_key, system_prompt)
        else:
            corrected_text = use_ollama_model(user_input, selected_model, system_prompt)

    return render_template(
        'grammar.html',
        llm_models=LLM_MODELS,
        selected_model=selected_model,
        user_input=user_input,
        corrected_text=corrected_text
    )

@app.route('/history')
def history():
    return render_template('history.html')

if __name__ == "__main__":
    app.run(debug=True)

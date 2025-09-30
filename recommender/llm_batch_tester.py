
import requests
import json
from datetime import datetime

# Prompt base (ajustar según el uso real)
with open("./recommender/prompt_monza.txt", "r", encoding="utf-8") as f:
    prompt = f.read()

# Añadir instrucción explícita al final para Qwen
if "qwen" in prompt.lower():
    prompt += "\nNo incluyas razonamiento ni bloques <|think|>. Devuelve solo el reglaje final."

# Configuraciones a probar
models = ["llama3", "mistral:7b-instruct"]
temperatures = [0.6, 0.7, 0.8, 0.9]
top_ps = [0.7, 0.8, 0.9]
repetition_penalties = [1.1, 1.2]
max_tokens = 2000

# Archivo de salida
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"./recommender/llm_responses/llm_responses_{timestamp}.json"
results = []

def clean_qwen_output(output):
    if "<|think|>" in output and "</|think|>" in output:
        return output.split("</|think|>")[-1].strip()
    return output.strip()

def query_ollama(prompt, model, temperature, top_p, max_tokens, repetition_penalty):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_p": top_p,
            "num_predict": max_tokens,
            "repetition_penalty": repetition_penalty
        }
    }

    response = requests.post(url, json=payload)
    data = response.json()

    if "response" in data:
        content = data["response"]
        if "qwen" in model.lower():
            content = clean_qwen_output(content)
        return content
    else:
        error_msg = data.get("error", "Respuesta inesperada del modelo.")
        print(f"Error con {model} | temp={temperature} | top_p={top_p} | penalty={repetition_penalty}")
        print("Mensaje devuelto:", error_msg)
        return f"[ERROR] {error_msg}"

# Ejecutar todas las combinaciones
for model in models:
    for temp in temperatures:
        for top_p in top_ps:
            for rp in repetition_penalties:
                print(f"▶ Ejecutando: {model} | temp={temp} | top_p={top_p} | penalty={rp}")
                response = query_ollama(prompt, model, temp, top_p, max_tokens, rp)
                results.append({
                    "model": model,
                    "temperature": temp,
                    "top_p": top_p,
                    "repetition_penalty": rp,
                    "response": response
                })

# Guardar resultados
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Resultados guardados en {output_file}")

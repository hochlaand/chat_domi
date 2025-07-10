from flask import Flask, render_template, request, jsonify
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe z pliku .env
load_dotenv()

app = Flask(__name__)

# Konfiguracja Hugging Face API
API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"
HF_TOKEN = os.getenv('HF_TOKEN', 'TWÓJ_TOKEN_HF')  # Ustaw token w pliku .env
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# Sprawdzenie czy token jest ustawiony
if HF_TOKEN == 'TWÓJ_TOKEN_HF' or not HF_TOKEN:
    print("⚠️  OSTRZEŻENIE: Brak tokenu Hugging Face!")
    print("   Ustaw token w pliku .env lub jako zmienną środowiskową HF_TOKEN")
    print("   Token możesz uzyskać na: https://huggingface.co/settings/tokens")

def generuj_odpowiedz(pytanie):
    """Generuje zabawną i miłą odpowiedź dla znajomej"""
    
    # Lista gotowych komplementów na wypadek problemów z API
    backup_responses = [
        "Przepraszam, mam chwilową przerwę w myśleniu! 😅 Spróbuj ponownie za chwilę.",
        "Moment, muszę się skupić - za bardzo się śmieję z naszej rozmowy! 😄 Napisz ponownie.",
        "Oj, chyba jestem tak rozrywkowy, że zapomniałem jak mówić! 😊 Spróbuj jeszcze raz.",
        "Wybacz, ale nasze rozmowy są tak fajne, że nie mogę się skupić! 🤗"
    ]
    
    prompt = (
        "Jesteś bardzo zabawnym, romantycznym, przyjaznym i pozytywnym chatbotem. "
        "Odpowiadasz na pytania Dominiki w sposób, który ją rozśmieszy, pozwiedzi i sprawi radość. "
        "Dominika to 23-letnia tancerka pracująca w przedszkolu. Ma 164 cm wzrostu, "
        "piękne ciemne włosy, wspaniałą sylwetkę i jest bardzo sympatyczna. "
        "Czasem brakuje jej energii, ale świetnie tańczy i jest bardzo urocza. "
        "Zawsze dodawaj pozytywne komentarze i emotikonki. Odpowiadaj po polsku jak do dobrej znajomej. "
        "Pytanie: " + pytanie + "\n"
        "Odpowiedź:"
    )
    
    try:
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 100,
                "temperature": 0.8,
                "do_sample": True,
                "top_p": 0.9
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                tekst = result[0].get('generated_text', '').replace(prompt, '').strip()
                if tekst and len(tekst) > 10:
                    return tekst
        
        # Fallback do gotowych odpowiedzi
        import random
        return random.choice(backup_responses)
        
    except Exception as e:
        print(f"Błąd API: {e}")
        import random
        return random.choice(backup_responses)

@app.route('/')
def home():
    """Strona główna chatbota"""
    return render_template('index.html')

@app.route('/debug')
def debug():
    """Debug endpoint do sprawdzenia struktury plików"""
    import os
    files = []
    for root, dirs, filenames in os.walk('.'):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    
    # Sprawdź specjalnie folder templates
    templates_exist = os.path.exists('templates')
    index_exist = os.path.exists('templates/index.html')
    
    debug_info = f"""
    <h1>Debug Info</h1>
    <p><strong>Folder templates istnieje:</strong> {templates_exist}</p>
    <p><strong>Plik templates/index.html istnieje:</strong> {index_exist}</p>
    <h2>Wszystkie pliki na serwerze:</h2>
    <pre>{"<br>".join(files)}</pre>
    """
    
    return debug_info

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint do obsługi wiadomości czatu"""
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Pusta wiadomość'}), 400
    
    # Generuj odpowiedź
    bot_response = generuj_odpowiedz(user_message)
    
    return jsonify({
        'response': bot_response,
        'timestamp': datetime.now().strftime('%H:%M')
    })

if __name__ == '__main__':
    # Pobierz port z zmiennej środowiskowej (dla hostingu w chmurze)
    try:
        port = int(os.getenv('PORT', 5000))
    except (ValueError, TypeError):
        port = 5000  # Domyślny port jeśli PORT nie jest liczbą
    
    debug_mode = os.getenv('DEBUG', 'True').lower() == 'true'
    
    print("🤖 Chatbot dla Dominiki uruchamia się...")
    print(f"📁 Folder templates istnieje: {os.path.exists('templates')}")
    print(f"📄 Plik index.html istnieje: {os.path.exists('templates/index.html')}")
    if debug_mode:
        print(f"🌐 Otwórz http://localhost:{port} w przeglądarce")
    else:
        print("🌐 Aplikacja działa w trybie produkcyjnym")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)

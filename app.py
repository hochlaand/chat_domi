from flask import Flask, render_template, request, jsonify
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe z pliku .env
load_dotenv()

app = Flask(__name__)

# Konfiguracja Hugging Face API
API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"  # Zmieniono na medium
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
        
        print(f"🔍 Wysyłam zapytanie do API: {prompt[:50]}...")
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        print(f"📊 Status code: {response.status_code}")
        print(f"📝 Odpowiedź API: {response.text[:200]}...")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Otrzymano odpowiedź: {result}")
            if isinstance(result, list) and len(result) > 0:
                tekst = result[0].get('generated_text', '').replace(prompt, '').strip()
                if tekst and len(tekst) > 10:
                    print(f"🎉 Zwracam odpowiedź: {tekst}")
                    return tekst
        else:
            print(f"❌ Błąd API: {response.status_code} - {response.text}")
        
        # Fallback do gotowych odpowiedzi
        import random
        return random.choice(backup_responses)
        
    except Exception as e:
        print(f"💥 Błąd API: {e}")
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
    <p><strong>HF_TOKEN ustawiony:</strong> {HF_TOKEN != 'TWÓJ_TOKEN_HF' and HF_TOKEN is not None}</p>
    <p><strong>API URL:</strong> {API_URL}</p>
    <h2>Wszystkie pliki na serwerze:</h2>
    <pre>{"<br>".join(files)}</pre>
    """
    
    return debug_info

@app.route('/test-api')
def test_api():
    """Test endpoint dla API Hugging Face"""
    try:
        # Test prostego zapytania
        test_prompt = "Cześć! Jak się masz?"
        
        payload = {
            "inputs": test_prompt,
            "parameters": {
                "max_new_tokens": 50,
                "temperature": 0.7
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=15)
        
        result_html = f"""
        <h1>🔍 Test API Hugging Face</h1>
        <h2>Konfiguracja:</h2>
        <p><strong>Model URL:</strong> {API_URL}</p>
        <p><strong>Token ustawiony:</strong> {HF_TOKEN != 'TWÓJ_TOKEN_HF' and HF_TOKEN is not None}</p>
        <p><strong>Token długość:</strong> {len(HF_TOKEN) if HF_TOKEN else 0}</p>
        
        <h2>Zapytanie:</h2>
        <p><strong>Payload:</strong> {payload}</p>
        
        <h2>Odpowiedź API:</h2>
        <p><strong>Status Code:</strong> {response.status_code}</p>
        <p><strong>Headers:</strong> {dict(response.headers)}</p>
        <p><strong>Response Text:</strong></p>
        <pre>{response.text}</pre>
        
        <h2>Parsed JSON:</h2>
        """
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                result_html += f"<pre>{json_data}</pre>"
            except:
                result_html += "<p>Nie można sparsować JSON</p>"
        else:
            result_html += "<p>Błąd API - brak JSON</p>"
        
        # Test backup odpowiedzi
        backup_test = generuj_odpowiedz("Cześć!")
        result_html += f"""
        <h2>Test funkcji generuj_odpowiedz:</h2>
        <p><strong>Odpowiedź:</strong> {backup_test}</p>
        """
        
        return result_html
        
    except Exception as e:
        return f"""
        <h1>❌ Błąd testu API</h1>
        <p><strong>Błąd:</strong> {str(e)}</p>
        <p><strong>Typ błędu:</strong> {type(e).__name__}</p>
        """

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

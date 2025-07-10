from flask import Flask, render_template, request, jsonify
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe z pliku .env
load_dotenv()

app = Flask(__name__)

# Konfiguracja Google Gemini AI - przez REST API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

if GEMINI_API_KEY:
    print(f"✅ Gemini API skonfigurowane (klucz: {GEMINI_API_KEY[:10]}...)")
    USE_GEMINI = True
else:
    print("⚠️ Używam Hugging Face jako głównego API")
    USE_GEMINI = False

# Backup/Alternative - Hugging Face API
API_URL = "https://api-inference.huggingface.co/models/openai-community/gpt2"
HF_TOKEN = os.getenv('HF_TOKEN')
if HF_TOKEN:
    HF_TOKEN = HF_TOKEN.strip().replace('\n', '').replace('\r', '').replace('\t', '')

headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

# Sprawdzenie czy token jest ustawiony
if HF_TOKEN == 'TWÓJ_TOKEN_HF' or not HF_TOKEN:
    print("⚠️  OSTRZEŻENIE: Brak tokenu Hugging Face!")
    print("   Ustaw token w pliku .env lub jako zmienną środowiskową HF_TOKEN")
    print("   Token możesz uzyskać na: https://huggingface.co/settings/tokens")
    print("   Token powinien mieć typ 'Read' i być aktywny")
else:
    print(f"✅ Token HF ustawiony (długość: {len(HF_TOKEN)})")
    print(f"🔗 Używany model: {API_URL}")

def generuj_odpowiedz(pytanie):
    """Generuje zabawną i miłą odpowiedź dla znajomej - używa Gemini jako główne API"""
    
    # Lista gotowych komplementów na wypadek problemów z API
    backup_responses = [
        "Przepraszam, mam chwilową przerwę w myśleniu! 😅 Spróbuj ponownie za chwilę.",
        "Moment, muszę się skupić - za bardzo się śmieję z naszej rozmowy! 😄 Napisz ponownie.",
        "Oj, chyba jestem tak rozrywkowy, że zapomniałem jak mówić! 😊 Spróbuj jeszcze raz.",
        "Wybacz, ale nasze rozmowy są tak fajne, że nie mogę się skupić! 🤗"
    ]
    
    # Spróbuj najpierw Gemini (jeśli dostępne)
    if USE_GEMINI:
        try:
            return generuj_odpowiedz_gemini(pytanie)
        except Exception as e:
            print(f"❌ Błąd Gemini: {e}, przechodzę na backup HF")
    
    # Fallback do Hugging Face
    return generuj_odpowiedz_hf(pytanie)

def generuj_odpowiedz_gemini(pytanie):
    """Generuje odpowiedź używając Google Gemini REST API"""
    
    # Spersonalizowany prompt dla Dominiki
    prompt = f"""
    Jesteś bardzo zabawnym, romantycznym, przyjaznym i pozytywnym chatbotem stworzonym specjalnie dla Dominiki.
    
    O Dominice:
    - Ma 23 lata
    - Jest tancerką i pracuje w przedszkolu
    - Ma 164 cm wzrostu
    - Ma piękne ciemne włosy i wspaniałą sylwetkę
    - Jest bardzo sympatyczna i urocza
    - Świetnie tańczy, ale czasem brakuje jej energii do aktywności
    
    Twoje zadanie:
    - Odpowiadaj w sposób, który ją rozśmieszy, pocieszy i sprawi radość
    - Używaj emotikonek i pozytywnych komentarzy
    - Pisz po polsku jak do dobrej znajomej
    - Bądź romantyczny ale w sposób przyjazny i zabawny
    - Doceniaj jej pasję do tańca i pracę z dziećmi
    - Odpowiedź powinna być krótka (1-3 zdania)
    
    Pytanie od Dominiki: {pytanie}
    
    Odpowiedz w sposób ciepły, zabawny i pozytywny:
    """
    
    print(f"🤖 Wysyłam zapytanie do Gemini REST API: {pytanie[:50]}...")
    
    # Przygotuj payload zgodnie z REST API
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt.strip()
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.8,
            "topP": 0.9,
            "topK": 40,
            "maxOutputTokens": 200
        }
    }
    
    # Headers zgodnie z dokumentacją
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': GEMINI_API_KEY
    }
    
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload, timeout=15)
        print(f"📊 Gemini Status: {response.status_code}")
        print(f"📝 Gemini Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            result = response.json()
            
            # Wyciągnij tekst z odpowiedzi Gemini
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    parts = candidate['content']['parts']
                    if len(parts) > 0 and 'text' in parts[0]:
                        odpowiedz = parts[0]['text'].strip()
                        print(f"✅ Gemini odpowiedź: {odpowiedz[:100]}...")
                        return odpowiedz
            
            raise Exception("Nie znaleziono tekstu w odpowiedzi Gemini")
        else:
            raise Exception(f"Gemini API błąd: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Błąd połączenia z Gemini: {e}")
    except Exception as e:
        raise Exception(f"Błąd przetwarzania odpowiedzi Gemini: {e}")

def generuj_odpowiedz_hf(pytanie):
    """Backup funkcja używająca Hugging Face GPT-2"""
    
    backup_responses = [
        "Przepraszam, mam chwilową przerwę w myśleniu! 😅 Spróbuj ponownie za chwilę.",
        "Moment, muszę się skupić - za bardzo się śmieję z naszej rozmowy! 😄 Napisz ponownie.",
        "Oj, chyba jestem tak rozrywkowy, że zapomniałem jak mówić! 😊 Spróbuj jeszcze raz.",
        "Wybacz, ale nasze rozmowy są tak fajne, że nie mogę się skupić! 🤗"
    ]
    
    # Prompt dostosowany do GPT-2
    prompt = (
        "Jestem przyjaznym chatbotem dla Dominiki. "
        "Dominika to urocza 23-letnia tancerka. "
        f"Pytanie: {pytanie}\n"
        "Odpowiedź:"
    )
    
    try:
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 150,
                "temperature": 0.7,
                "do_sample": True,
                "top_p": 0.9,
                "pad_token_id": 50256
            }
        }
        
        print(f"🔍 Wysyłam zapytanie do HF: {prompt[:50]}...")
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                tekst = result[0].get('generated_text', '')
                
                # Usuń oryginalny prompt z odpowiedzi
                if tekst.startswith(prompt):
                    tekst = tekst[len(prompt):].strip()
                
                # Dla GPT-2 może być też tylko część po "Odpowiedź:"
                if "Odpowiedź:" in tekst:
                    tekst = tekst.split("Odpowiedź:")[-1].strip()
                
                if tekst and len(tekst) > 5:
                    print(f"🎉 Zwracam odpowiedź HF: {tekst}")
                    return tekst
        else:
            print(f"❌ Błąd HF API: {response.status_code} - {response.text}")
        
        # Fallback do gotowych odpowiedzi
        import random
        return random.choice(backup_responses)
        
    except Exception as e:
        print(f"💥 Błąd HF API: {e}")
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
    <h1>🛠️ Debug Info - Gemini Edition</h1>
    <p><strong>Folder templates istnieje:</strong> {templates_exist}</p>
    <p><strong>Plik templates/index.html istnieje:</strong> {index_exist}</p>
    <p><strong>Gemini API:</strong> {'✅ Dostępny' if USE_GEMINI else '❌ Niedostępny'}</p>
    <p><strong>Gemini API Key długość:</strong> {len(GEMINI_API_KEY) if GEMINI_API_KEY else 0}</p>
    <p><strong>HF Token (backup):</strong> {'✅ Ustawiony' if HF_TOKEN and HF_TOKEN != 'TWÓJ_TOKEN_HF' else '❌ Brak'}</p>
    <p><strong>Główne API:</strong> {'🤖 Google Gemini' if USE_GEMINI else '🔄 Hugging Face GPT-2'}</p>
    
    <h2>🔍 Endpointy diagnostyczne:</h2>
    <ul>
        <li><a href="/test-gemini">🤖 Test Gemini</a> - test głównego API Google</li>
        <li><a href="/test-gemini-simple">🧪 Test Gemini Simple</a> - prosty test Gemini</li>
        <li><a href="/test-comparison">⚖️ Porównanie</a> - Gemini vs HF</li>
        <li><a href="/test-hf-backup">🔄 Test HF Backup</a> - test zapasowego HF</li>
        <li><a href="/debug-token-raw">🔍 Debug Raw Token</a> - szczegółowy debug tokena HF</li>
        <li><a href="/test-token">🔐 Test tokena HF</a> - standardowy test HF</li>
    </ul>
    
    <h2>📁 Wszystkie pliki na serwerze:</h2>
    <pre>{"<br>".join(files)}</pre>
    
    <hr>
    <p><a href="/">🏠 Powrót do chatbota</a></p>
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

@app.route('/test-token')
def test_token():
    """Test sprawdzający czy token jest poprawny"""
    try:
        # Prosta weryfikacja tokena poprzez zapytanie do API
        test_headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        
        # Próba prostego zapytania do API - test tokena
        response = requests.get(
            "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
            headers=test_headers,
            timeout=10
        )
        
        result_html = f"""
        <h1>🔐 Test Tokena Hugging Face</h1>
        <h2>Konfiguracja:</h2>
        <p><strong>Token ustawiony:</strong> {HF_TOKEN != 'TWÓJ_TOKEN_HF' and HF_TOKEN is not None}</p>
        <p><strong>Token długość:</strong> {len(HF_TOKEN) if HF_TOKEN else 0}</p>
        <p><strong>Token pierwsze 10 znaków:</strong> {HF_TOKEN[:10] if HF_TOKEN else 'Brak'}...</p>
        <p><strong>Token ostatnie 10 znaków:</strong> ...{HF_TOKEN[-10:] if HF_TOKEN else 'Brak'}</p>
        
        <h2>Test autoryzacji (GET na model):</h2>
        <p><strong>Status Code:</strong> {response.status_code}</p>
        <p><strong>Response:</strong></p>
        <pre>{response.text}</pre>
        
        <h2>Diagnostyka:</h2>
        """
        
        if response.status_code == 200:
            result_html += "<p>✅ Token jest poprawny!</p>"
        elif response.status_code == 401:
            result_html += "<p>❌ Token jest niepoprawny lub nieaktywny</p>"
            result_html += "<p>🔧 Sprawdź czy token ma odpowiednie uprawnienia (Read)</p>"
        else:
            result_html += f"<p>⚠️ Nieoczekiwany status: {response.status_code}</p>"
        
        # Test czy token zawiera spacje lub niepoprawne znaki
        if HF_TOKEN and (' ' in HF_TOKEN or '\n' in HF_TOKEN or '\t' in HF_TOKEN):
            result_html += "<p>⚠️ Token może zawierać spacje lub znaki nowej linii!</p>"
        
        result_html += """
        <h2>Instrukcje:</h2>
        <p>1. Przejdź do <a href="https://huggingface.co/settings/tokens" target="_blank">Hugging Face Tokens</a></p>
        <p>2. Wygeneruj nowy token typu "Read"</p>
        <p>3. Skopiuj token (uważaj na spacje!)</p>
        <p>4. Zaktualizuj zmienną środowiskową HF_TOKEN w Render</p>
        <p>5. Restartuj aplikację</p>
        <hr>
        <p><a href="/test-api">🔍 Test pełnego API</a></p>
        <p><a href="/debug">🛠️ Debug Info</a></p>
        <p><a href="/">🏠 Powrót do chatbota</a></p>
        """
        
        return result_html
        
    except Exception as e:
        return f"""
        <h1>❌ Błąd testowania tokena</h1>
        <p>Błąd: {str(e)}</p>
        <p>Sprawdź logi aplikacji w Render</p>
        <p><a href="/">🏠 Powrót do chatbota</a></p>
        """

@app.route('/test-models')
def test_models():
    """Test różnych modeli do chatbota"""
    models_to_test = [
        "openai-community/gpt2",        # Stabilny GPT-2
        "gpt2",                         # Alternatywny GPT-2
        "facebook/blenderbot-400M-distill",
        "microsoft/DialoGPT-medium", 
        "facebook/blenderbot-small-90M",
        "google/flan-t5-small"
    ]
    
    results = []
    test_input = "Cześć! Jak się masz?"
    
    for model in models_to_test:
        try:
            url = f"https://api-inference.huggingface.co/models/{model}"
            
            payload = {
                "inputs": test_input,
                "parameters": {
                    "max_length": 100,
                    "temperature": 0.7,
                    "do_sample": True
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            
            status = "✅ OK" if response.status_code == 200 else f"❌ Error {response.status_code}"
            
            results.append({
                'model': model,
                'status': status,
                'response_code': response.status_code,
                'response_text': response.text[:200]
            })
            
        except Exception as e:
            results.append({
                'model': model,
                'status': f"❌ Exception: {str(e)[:100]}",
                'response_code': 'Error',
                'response_text': str(e)
            })
    
    result_html = f"""
    <h1>🤖 Test różnych modeli</h1>
    <p><strong>Test input:</strong> {test_input}</p>
    <p><strong>Token Status:</strong> {'✅ Set' if HF_TOKEN and HF_TOKEN != 'TWÓJ_TOKEN_HF' else '❌ Not set'}</p>
    
    <h2>Wyniki:</h2>
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr>
            <th>Model</th>
            <th>Status</th>
            <th>Response Code</th>
            <th>Response Preview</th>
        </tr>
    """
    
    for result in results:
        result_html += f"""
        <tr>
            <td>{result['model']}</td>
            <td>{result['status']}</td>
            <td>{result['response_code']}</td>
            <td><pre style="white-space: pre-wrap; max-width: 300px; overflow: hidden;">{result['response_text']}</pre></td>
        </tr>
        """
    
    result_html += """
    </table>
    
    <h2>Instrukcje:</h2>
    <p>Model z statusem ✅ OK można użyć w chatbocie</p>
    <p>Aby zmienić model, zaktualizuj zmienną API_URL w kodzie</p>
    
    <hr>
    <p><a href="/test-token">🔐 Test tokena</a></p>
    <p><a href="/test-api">🔍 Test aktualnego API</a></p>
    <p><a href="/">🏠 Powrót do chatbota</a></p>
    """
    
    return result_html

@app.route('/debug-token-raw')
def debug_token_raw():
    """Szczegółowy debug tokena - RAW"""
    import base64
    
    # Sprawdź różne sposoby odczytywania tokena
    token_from_env = os.getenv('HF_TOKEN')
    token_from_env_upper = os.getenv('HF_TOKEN', '').upper()
    token_stripped = os.getenv('HF_TOKEN', '').strip()
    
    # Sprawdź czy token jest base64
    try:
        if token_from_env:
            decoded = base64.b64decode(token_from_env).decode('utf-8')
            is_base64 = True
        else:
            decoded = "No token"
            is_base64 = False
    except:
        decoded = "Not base64"
        is_base64 = False
    
    # Sprawdź format tokena
    token_analysis = {
        'raw_token': token_from_env,
        'token_length': len(token_from_env) if token_from_env else 0,
        'token_type': type(token_from_env).__name__,
        'starts_with_hf': token_from_env.startswith('hf_') if token_from_env else False,
        'has_spaces': ' ' in token_from_env if token_from_env else False,
        'has_newlines': '\n' in token_from_env if token_from_env else False,
        'is_base64': is_base64,
        'decoded_if_base64': decoded if is_base64 else "Not base64",
        'all_env_vars': dict(os.environ)
    }
    
    result_html = f"""
    <h1>🔍 Debug Token RAW</h1>
    
    <h2>Token Analysis:</h2>
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr><th>Property</th><th>Value</th></tr>
        <tr><td>Raw Token</td><td><pre>{token_from_env[:50] if token_from_env else 'None'}...</pre></td></tr>
        <tr><td>Length</td><td>{token_analysis['token_length']}</td></tr>
        <tr><td>Type</td><td>{token_analysis['token_type']}</td></tr>
        <tr><td>Starts with hf_</td><td>{token_analysis['starts_with_hf']}</td></tr>
        <tr><td>Has spaces</td><td>{token_analysis['has_spaces']}</td></tr>
        <tr><td>Has newlines</td><td>{token_analysis['has_newlines']}</td></tr>
        <tr><td>Is base64?</td><td>{token_analysis['is_base64']}</td></tr>
        <tr><td>Decoded (if base64)</td><td><pre>{decoded[:50] if decoded else 'N/A'}...</pre></td></tr>
    </table>
    
    <h2>Environment Variables (HF related):</h2>
    <ul>
    """
    
    for key, value in os.environ.items():
        if 'HF' in key.upper() or 'HUGGING' in key.upper():
            result_html += f"<li><strong>{key}</strong>: {value[:50]}...</li>"
    
    result_html += """
    </ul>
    
    <h2>Test Headers:</h2>
    <p>Current header: <code>Authorization: Bearer {token}</code></p>
    <p>Alternative header: <code>Authorization: token {token}</code></p>
    
    <hr>
    <p><a href="/test-token">🔐 Test tokena</a></p>
    <p><a href="/test-hardcoded-token">🔧 Test hardcoded token</a></p>
    <p><a href="/">🏠 Powrót do chatbota</a></p>
    """
    
    return result_html

@app.route('/test-hardcoded-token')
def test_hardcoded_token():
    """Test z hardcoded tokenem (tylko do debugowania)"""
    # UWAGA: To tylko do testów - w produkcji usuń ten endpoint!
    
    # Tutaj możesz wstawić token bezpośrednio do testów
    # Spróbuj najpierw z pliku .env, potem hardcoded
    HARDCODED_TOKEN = os.getenv('HF_TOKEN', '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')
    
    # Jeśli chcesz przetestować inny token, odkomentuj poniżej:
    # HARDCODED_TOKEN = "hf_NOWY_TOKEN_TUTAJ"
    
    # Test z hardcoded tokenem
    try:
        test_headers = {"Authorization": f"Bearer {HARDCODED_TOKEN}"}
        
        response = requests.get(
            "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
            headers=test_headers,
            timeout=10
        )
        
        hardcoded_test_result = f"""
        <h2>🔧 Test Hardcoded Token:</h2>
        <p><strong>Hardcoded Token:</strong> {HARDCODED_TOKEN[:15]}...</p>
        <p><strong>Status Code:</strong> {response.status_code}</p>
        <p><strong>Response:</strong></p>
        <pre>{response.text[:200]}</pre>
        """
        
        if response.status_code == 200:
            hardcoded_test_result += "<p>✅ <strong>Hardcoded token DZIAŁA!</strong></p>"
        else:
            hardcoded_test_result += f"<p>❌ <strong>Hardcoded token też nie działa: {response.status_code}</strong></p>"
    
    except Exception as e:
        hardcoded_test_result = f"""
        <h2>❌ Błąd testu hardcoded:</h2>
        <p>{str(e)}</p>
        """
    
    return f"""
    <h1>🔧 Test Hardcoded Token</h1>
    <p><strong>UWAGA:</strong> Ten endpoint służy tylko do testów!</p>
    
    <h2>Porównanie tokenów:</h2>
    <p><strong>Token z environment:</strong> {'✅' if HF_TOKEN and HF_TOKEN != 'TWÓJ_TOKEN_HF' else '❌'}</p>
    <p><strong>Env token:</strong> {HF_TOKEN[:15] if HF_TOKEN else 'Brak'}...</p>
    <p><strong>Hardcoded token:</strong> {HARDCODED_TOKEN[:15]}...</p>
    
    {hardcoded_test_result}
    
    <hr>
    <p><a href="/debug-token-raw">🔍 Debug Raw Token</a></p>
    <p><a href="/test-token">🔐 Test tokena</a></p>
    <p><a href="/">🏠 Powrót do chatbota</a></p>
    """

@app.route('/test-token-formats')
def test_token_formats():
    """Test różnych formatów tokena"""
    if not HF_TOKEN or HF_TOKEN == 'TWÓJ_TOKEN_HF':
        return """
        <h1>❌ Brak tokena do testowania</h1>
        <p>Ustaw token w zmiennej środowiskowej HF_TOKEN</p>
        <p><a href="/">🏠 Powrót do chatbota</a></p>
        """
    
    # Testuj różne formaty nagłówka autoryzacji
    test_formats = [
        ("Bearer {token}", f"Bearer {HF_TOKEN}"),
        ("token {token}", f"token {HF_TOKEN}"),
        ("{token}", HF_TOKEN),
        ("Bearer: {token}", f"Bearer: {HF_TOKEN}"),
    ]
    
    results = []
    
    for format_name, header_value in test_formats:
        try:
            test_headers = {"Authorization": header_value}
            
            response = requests.get(
                "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
                headers=test_headers,
                timeout=10
            )
            
            status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
            
            results.append({
                'format': format_name,
                'header': header_value[:50] + "..." if len(header_value) > 50 else header_value,
                'status': status,
                'response': response.text[:100]
            })
            
        except Exception as e:
            results.append({
                'format': format_name,
                'header': header_value[:50] + "..." if len(header_value) > 50 else header_value,
                'status': f"❌ Error: {str(e)[:50]}",
                'response': str(e)[:100]
            })
    
    result_html = """
    <h1>🔧 Test formatów tokena</h1>
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr>
            <th>Format</th>
            <th>Header Value</th>
            <th>Status</th>
            <th>Response</th>
        </tr>
    """
    
    for result in results:
        result_html += f"""
        <tr>
            <td>{result['format']}</td>
            <td><code>{result['header']}</code></td>
            <td>{result['status']}</td>
            <td><pre>{result['response']}</pre></td>
        </tr>
        """
    
    result_html += """
    </table>
    
    <p><strong>Instrukcje:</strong> Jeśli któryś format zwraca ✅ OK, możemy go użyć w kodzie.</p>
    
    <hr>
    <p><a href="/debug-token-raw">🔍 Debug Raw Token</a></p>
    <p><a href="/test-token">🔐 Test tokena</a></p>
    <p><a href="/">🏠 Powrót do chatbota</a></p>
    """
    
    return result_html

@app.route('/test-simple-api')
def test_simple_api():
    """Test z najprostszym możliwym zapytaniem"""
    
    # Użyj nowego tokena gdy go uzyskasz - spróbuj z .env
    TEST_TOKEN = os.getenv('HF_TOKEN', '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')
    
    # Jeśli chcesz przetestować inny token, odkomentuj:
    # TEST_TOKEN = "hf_NOWY_TOKEN_TUTAJ"
    
    if TEST_TOKEN == "WSTAW_TUTAJ_NOWY_TOKEN" or not TEST_TOKEN:
        return """
        <h1>⚠️ Konfiguracja tokena</h1>
        <p>Token odczytany z .env lub ustaw nowy w kodzie</p>
        <p><strong>Aktualny token:</strong> {}</p>
        <p><a href="https://huggingface.co/settings/tokens" target="_blank">🔗 Hugging Face Tokens</a></p>
        """.format(TEST_TOKEN[:15] + "..." if TEST_TOKEN else "Brak")
    
    # Testuj różne proste modele
    simple_models = [
        "openai-community/gpt2",       # Stabilny GPT-2
        "gpt2",                        # Podstawowy GPT-2
        "distilgpt2",                  # Lżejszy GPT-2
        "microsoft/DialoGPT-small",
        "facebook/blenderbot-small-90M"
    ]
    
    results = []
    
    for model in simple_models:
        try:
            url = f"https://api-inference.huggingface.co/models/{model}"
            headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
            
            # Bardzo prosty payload
            payload = {"inputs": "Hello"}
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
            
            results.append({
                'model': model,
                'status': status,
                'response_code': response.status_code,
                'response': response.text[:200]
            })
            
        except Exception as e:
            results.append({
                'model': model,
                'status': f"❌ Error: {str(e)[:50]}",
                'response_code': 'Exception',
                'response': str(e)[:200]
            })
    
    result_html = f"""
    <h1>🧪 Test Simple API</h1>
    <p><strong>Test Token:</strong> {TEST_TOKEN[:15]}...</p>
    <p><strong>Simple Input:</strong> "Hello"</p>
    
    <h2>Wyniki:</h2>
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr><th>Model</th><th>Status</th><th>Response Code</th><th>Response</th></tr>
    """
    
    for result in results:
        result_html += f"""
        <tr>
            <td>{result['model']}</td>
            <td>{result['status']}</td>
            <td>{result['response_code']}</td>
            <td><pre>{result['response']}</pre></td>
        </tr>
        """
    
    result_html += """
    </table>
    
    <p><strong>Instrukcje:</strong></p>
    <ol>
        <li>Jeśli wszystkie modele zwracają 401 - token jest niepoprawny</li>
        <li>Jeśli niektóre modele działają - używaj działającego modelu</li>
        <li>Jeśli żaden nie działa - wygeneruj nowy token</li>
    </ol>
    
    <hr>
    <p><a href="/test-hardcoded-token">🔧 Test Hardcoded Token</a></p>
    <p><a href="/debug-token-raw">🔍 Debug Raw Token</a></p>
    <p><a href="/">🏠 Powrót do chatbota</a></p>
    """
    
    return result_html

@app.route('/test-gpt2')
def test_gpt2():
    """Test specjalnie dla modelu GPT-2"""
    
    # Test różnych wariantów GPT-2
    gpt2_models = [
        "openai-community/gpt2",
        "gpt2",
        "distilgpt2",
        "openai-community/gpt2-medium",
        "openai-community/gpt2-large"
    ]
    
    # Prosty prompt dla GPT-2
    test_prompt = "Cześć! Jestem przyjaznym chatbotem. Jak się masz?"
    
    results = []
    
    for model in gpt2_models:
        try:
            url = f"https://api-inference.huggingface.co/models/{model}"
            headers = {"Authorization": f"Bearer {HF_TOKEN}"}
            
            # Parametry dostosowane do GPT-2
            payload = {
                "inputs": test_prompt,
                "parameters": {
                    "max_length": 100,
                    "temperature": 0.7,
                    "do_sample": True,
                    "top_p": 0.9,
                    "pad_token_id": 50256
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            
            status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
            
            # Sparsuj odpowiedź
            generated_text = "Brak odpowiedzi"
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    if isinstance(json_data, list) and len(json_data) > 0:
                        generated_text = json_data[0].get('generated_text', 'Brak tekstu')
                        # Usuń oryginalny prompt z odpowiedzi
                        if generated_text.startswith(test_prompt):
                            generated_text = generated_text[len(test_prompt):].strip()
                except:
                    generated_text = "Błąd parsowania JSON"
            
            results.append({
                'model': model,
                'status': status,
                'response_code': response.status_code,
                'generated_text': generated_text[:200],
                'raw_response': response.text[:200]
            })
            
        except Exception as e:
            results.append({
                'model': model,
                'status': f"❌ Error: {str(e)[:50]}",
                'response_code': 'Exception',
                'generated_text': str(e)[:100],
                'raw_response': str(e)[:200]
            })
    
    result_html = f"""
    <h1>🤖 Test GPT-2 Models</h1>
    <p><strong>Test Prompt:</strong> {test_prompt}</p>
    <p><strong>Token Status:</strong> {'✅ Set' if HF_TOKEN and HF_TOKEN != 'TWÓJ_TOKEN_HF' else '❌ Not set'}</p>
    
    <h2>Wyniki:</h2>
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr>
            <th>Model</th>
            <th>Status</th>
            <th>Response Code</th>
            <th>Generated Text</th>
            <th>Raw Response</th>
        </tr>
    """
    
    for result in results:
        result_html += f"""
        <tr>
            <td>{result['model']}</td>
            <td>{result['status']}</td>
            <td>{result['response_code']}</td>
            <td><pre style="white-space: pre-wrap; max-width: 250px; overflow: hidden;">{result['generated_text']}</pre></td>
            <td><pre style="white-space: pre-wrap; max-width: 250px; overflow: hidden;">{result['raw_response']}</pre></td>
        </tr>
        """
    
    result_html += """
    </table>
    
    <p><strong>Instrukcje:</strong></p>
    <ol>
        <li>Model z ✅ OK można użyć w chatbocie</li>
        <li>Jeśli GPT-2 działa - zmień API_URL na działający model</li>
        <li>GPT-2 jest stabilny i popularny - powinien działać</li>
    </ol>
    
    <hr>
    <p><a href="/test-simple-api">🧪 Test Simple API</a></p>
    <p><a href="/test-models">🤖 Test wszystkich modeli</a></p>
    <p><a href="/debug">🛠️ Debug Info</a></p>
    <p><a href="/">🏠 Powrót do chatbota</a></p>
    """
    
    return result_html

@app.route('/test-gemini')
def test_gemini():
    """Test głównego API Gemini"""
    
    if not USE_GEMINI:
        return f"""
        <h1>❌ Gemini niedostępny</h1>
        <p><strong>API Key:</strong> {'Set' if GEMINI_API_KEY else 'Not set'}</p>
        <p><strong>Powód:</strong> Brak klucza API</p>
        
        <h2>Instrukcje:</h2>
        <ol>
            <li>Ustaw GEMINI_API_KEY w .env</li>
            <li>Restartuj aplikację</li>
        </ol>
        
        <p><a href="/test-hf-backup">🔄 Test HF Backup</a></p>
        <p><a href="/">🏠 Powrót do chatbota</a></p>
        """
    
    test_questions = [
        "Cześć! Jak się masz?",
        "Jestem zmęczona po pracy w przedszkolu",
        "Chciałabym potańczyć, ale nie mam energii",
        "Powiedz mi coś miłego"
    ]
    
    results = []
    
    for question in test_questions:
        try:
            start_time = datetime.now()
            response = generuj_odpowiedz_gemini(question)
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            results.append({
                'question': question,
                'response': response,
                'status': '✅ OK',
                'time': f"{response_time:.2f}s"
            })
            
        except Exception as e:
            results.append({
                'question': question,
                'response': f"Błąd: {str(e)}",
                'status': '❌ Error',
                'time': 'N/A'
            })
    
    result_html = f"""
    <h1>🤖 Test Gemini API</h1>
    <p><strong>API Key Status:</strong> {'✅ Set' if GEMINI_API_KEY else '❌ Not set'}</p>
    <p><strong>API Key:</strong> {GEMINI_API_KEY[:15] if GEMINI_API_KEY else 'Brak'}...</p>
    
    <h2>Testy konwersacyjne:</h2>
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr>
            <th>Pytanie</th>
            <th>Odpowiedź Gemini</th>
            <th>Status</th>
            <th>Czas</th>
        </tr>
    """
    
    for result in results:
        result_html += f"""
        <tr>
            <td>{result['question']}</td>
            <td style="max-width: 400px;"><pre style="white-space: pre-wrap;">{result['response']}</pre></td>
            <td>{result['status']}</td>
            <td>{result['time']}</td>
        </tr>
        """
    
    result_html += """
    </table>
    
    <hr>
    <p><a href="/test-gemini-simple">🧪 Test Simple</a></p>
    <p><a href="/test-comparison">⚖️ Porównanie</a></p>
    <p><a href="/debug">🛠️ Debug</a></p>
    <p><a href="/">🏠 Powrót do chatbota</a></p>
    """
    
    return result_html

@app.route('/test-gemini-simple')
def test_gemini_simple():
    """Prosty test Gemini"""
    
    if not USE_GEMINI:
        return """
        <h1>❌ Gemini niedostępny</h1>
        <p>Ustaw GEMINI_API_KEY w .env</p>
        <p><a href="/debug">🛠️ Debug</a></p>
        """
    
    try:
        # Bardzo prosty test z REST API
        simple_prompt = "Powiedz 'Cześć Dominika!' po polsku"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": simple_prompt
                        }
                    ]
                }
            ]
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': GEMINI_API_KEY
        }
        
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload, timeout=10)
        
        result_html = f"""
        <h1>🧪 Test Simple Gemini</h1>
        <p><strong>API Key:</strong> {GEMINI_API_KEY[:15]}...</p>
        <p><strong>API URL:</strong> {GEMINI_API_URL}</p>
        <p><strong>Prompt:</strong> {simple_prompt}</p>
        
        <h2>Odpowiedź:</h2>
        <p><strong>Status Code:</strong> {response.status_code}</p>
        <p><strong>Response Text:</strong></p>
        <pre>{response.text}</pre>
        """
        
        if response.status_code == 200:
            try:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    candidate = result['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        parts = candidate['content']['parts']
                        if len(parts) > 0 and 'text' in parts[0]:
                            generated_text = parts[0]['text']
                            result_html += f"""
                            <h2>Wyciągnięty tekst:</h2>
                            <pre>{generated_text}</pre>
                            <p><strong>Status:</strong> ✅ Sukces - Gemini działa!</p>
                            """
                        else:
                            result_html += "<p><strong>Status:</strong> ❌ Brak tekstu w parts</p>"
                    else:
                        result_html += "<p><strong>Status:</strong> ❌ Brak content/parts</p>"
                else:
                    result_html += "<p><strong>Status:</strong> ❌ Brak candidates</p>"
            except Exception as e:
                result_html += f"<p><strong>Błąd parsowania:</strong> {e}</p>"
        else:
            result_html += f"<p><strong>Status:</strong> ❌ Błąd API - {response.status_code}</p>"
        
        result_html += """
        <hr>
        <p><a href="/test-gemini">🤖 Test pełny</a></p>
        <p><a href="/">🏠 Powrót do chatbota</a></p>
        """
        
        return result_html
        
    except Exception as e:
        return f"""
        <h1>❌ Błąd Simple Test</h1>
        <p><strong>Błąd:</strong> {str(e)}</p>
        <p><strong>Typ błędu:</strong> {type(e).__name__}</p>
        
        <h2>Możliwe przyczyny:</h2>
        <ul>
            <li>Nieprawidłowy API key</li>
            <li>Brak dostępu do internetu</li>
            <li>Ograniczenia API</li>
            <li>Błąd w bibliotece google-generativeai</li>
        </ul>
        
        <p><a href="/debug">🛠️ Debug</a></p>
        <p><a href="/test-hf-backup">🔄 Test HF Backup</a></p>
        """

@app.route('/test-comparison')
def test_comparison():
    """Porównanie Gemini vs Hugging Face"""
    
    test_question = "Cześć! Powiedz mi coś miłego"
    
    # Test Gemini
    try:
        if USE_GEMINI:
            gemini_response = generuj_odpowiedz_gemini(test_question)
            gemini_status = "✅ OK"
        else:
            gemini_response = "Gemini niedostępny - brak klucza API"
            gemini_status = "❌ Niedostępny"
    except Exception as e:
        gemini_response = f"Błąd: {str(e)}"
        gemini_status = "❌ Error"
    
    # Test HF Backup
    try:
        hf_response = generuj_odpowiedz_hf(test_question)
        hf_status = "✅ OK"
    except Exception as e:
        hf_response = f"Błąd: {str(e)}"
        hf_status = "❌ Error"
    
    return f"""
    <h1>⚖️ Porównanie API</h1>
    <p><strong>Pytanie testowe:</strong> {test_question}</p>
    <p><strong>Główne API:</strong> {'🤖 Gemini' if USE_GEMINI else '🔄 Hugging Face'}</p>
    
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr>
            <th>API</th>
            <th>Status</th>
            <th>Odpowiedź</th>
        </tr>
        <tr>
            <td><strong>🤖 Google Gemini</strong></td>
            <td>{gemini_status}</td>
            <td style="max-width: 400px;"><pre style="white-space: pre-wrap;">{gemini_response}</pre></td>
        </tr>
        <tr>
            <td><strong>🔄 Hugging Face (backup)</strong></td>
            <td>{hf_status}</td>
            <td style="max-width: 400px;"><pre style="white-space: pre-wrap;">{hf_response}</pre></td>
        </tr>
    </table>
    
    <h2>Rekomendacja:</h2>
    <p>Główne API: <strong>Google Gemini</strong> (nowocześniejsze, lepsze konwersacje)</p>
    <p>Backup: <strong>Hugging Face GPT-2</strong> (w razie problemów z Gemini)</p>
    
    <hr>
    <p><a href="/test-gemini">🤖 Test Gemini</a></p>
    <p><a href="/test-hf-backup">🔄 Test HF Backup</a></p>
    <p><a href="/debug">🛠️ Debug</a></p>
    <p><a href="/">🏠 Powrót do chatbota</a></p>
    """

@app.route('/test-hf-backup')
def test_hf_backup():
    """Test zapasowego API Hugging Face"""
    
    test_question = "Cześć! Jak się masz?"
    
    try:
        response = generuj_odpowiedz_hf(test_question)
        
        return f"""
        <h1>🔄 Test HF Backup</h1>
        <p><strong>HF Token:</strong> {'✅ Set' if HF_TOKEN and HF_TOKEN != 'TWÓJ_TOKEN_HF' else '❌ Not set'}</p>
        <p><strong>API URL:</strong> {API_URL}</p>
        <p><strong>Pytanie:</strong> {test_question}</p>
        
        <h2>Odpowiedź:</h2>
        <pre style="white-space: pre-wrap;">{response}</pre>
        
        <p><strong>Status:</strong> ✅ Backup działa</p>
        
        <hr>
        <p><a href="/test-comparison">⚖️ Porównanie</a></p>
        <p><a href="/test-token">🔐 Test tokena HF</a></p>
        <p><a href="/">🏠 Powrót do chatbota</a></p>
        """
        
    except Exception as e:
        return f"""
        <h1>❌ Błąd HF Backup</h1>
        <p><strong>Błąd:</strong> {str(e)}</p>
        <p><strong>HF Token:</strong> {'Set' if HF_TOKEN else 'Not set'}</p>
        
        <hr>
        <p><a href="/debug">🛠️ Debug</a></p>
        <p><a href="/">🏠 Powrót do chatbota</a></p>
        """

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
    print(f"🤖 Główne API: {'✅ Google Gemini' if USE_GEMINI else '🔄 Hugging Face GPT-2'}")
    
    if USE_GEMINI:
        print(f"✅ Gemini API Key: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-5:]}")
    if HF_TOKEN and HF_TOKEN != 'TWÓJ_TOKEN_HF':
        print(f"🔄 HF Backup dostępny: {HF_TOKEN[:10]}...{HF_TOKEN[-5:]}")
    
    if debug_mode:
        print(f"🌐 Otwórz http://localhost:{port} w przeglądarce")
        print(f"🔧 Debug: http://localhost:{port}/debug")
        if USE_GEMINI:
            print(f"🤖 Test Gemini: http://localhost:{port}/test-gemini")
    else:
        print("🌐 Aplikacja działa w trybie produkcyjnym")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)

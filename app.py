from flask import Flask, render_template, request, jsonify
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe z pliku .env
load_dotenv()

app = Flask(__name__)

# Konfiguracja Hugging Face API
# Opcje modeli (odkomentuj żądany):
API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"  # Zmieniony na bardziej stabilny
# API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"  # Oryginalny
# API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-small"  # Alternatywny 2

# Próba odczytania tokena z różnych źródeł
HF_TOKEN = None

# 1. Próba z zmiennej środowiskowej
if os.getenv('HF_TOKEN') and os.getenv('HF_TOKEN') != 'TWÓJ_TOKEN_HF':
    HF_TOKEN = os.getenv('HF_TOKEN').strip()
    print(f"✅ Token z env variable (długość: {len(HF_TOKEN)})")

# 2. Próba z pliku config.py (jeśli istnieje)
if not HF_TOKEN:
    try:
        import config  # type: ignore
        if hasattr(config, 'HF_TOKEN_ALT') and config.HF_TOKEN_ALT != 'TWÓJ_TOKEN_TUTAJ':
            HF_TOKEN = config.HF_TOKEN_ALT.strip()
            print(f"✅ Token z config.py (długość: {len(HF_TOKEN)})")
    except (ImportError, AttributeError):
        print("⚠️  Brak pliku config.py lub tokena w config.py")

# 3. Fallback do zmiennej środowiskowej (nawet jeśli pusta)
if not HF_TOKEN:
    HF_TOKEN = os.getenv('HF_TOKEN', 'TWÓJ_TOKEN_HF')

# Sprawdzenie i czyszczenie tokena
if HF_TOKEN:
    # Usuń możliwe spacje, nowe linie, tabulatory
    HF_TOKEN = HF_TOKEN.strip().replace('\n', '').replace('\r', '').replace('\t', '')
    
    # Sprawdź czy token ma poprawny format
    if not HF_TOKEN.startswith('hf_'):
        print(f"⚠️  Token nie zaczyna się od 'hf_': {HF_TOKEN[:10]}...")
    
    # Sprawdź długość tokena (typowo 37 znaków)
    if len(HF_TOKEN) < 30:
        print(f"⚠️  Token wydaje się za krótki: {len(HF_TOKEN)} znaków")

headers = {"Authorization": f"Bearer {HF_TOKEN}"}

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
    <h1>🛠️ Debug Info</h1>
    <p><strong>Folder templates istnieje:</strong> {templates_exist}</p>
    <p><strong>Plik templates/index.html istnieje:</strong> {index_exist}</p>
    <p><strong>HF_TOKEN ustawiony:</strong> {HF_TOKEN != 'TWÓJ_TOKEN_HF' and HF_TOKEN is not None}</p>
    <p><strong>HF_TOKEN długość:</strong> {len(HF_TOKEN) if HF_TOKEN else 0}</p>
    <p><strong>API URL:</strong> {API_URL}</p>
    
    <h2>🔍 Endpointy diagnostyczne:</h2>
    <ul>
        <li><a href="/debug-token-raw">🔍 Debug Raw Token</a> - szczegółowy debug tokena</li>
        <li><a href="/test-token-formats">🔧 Test formatów tokena</a> - test różnych formatów autoryzacji</li>
        <li><a href="/test-hardcoded-token">🔨 Test hardcoded token</a> - test z tokenem w kodzie</li>
        <li><a href="/test-token">🔐 Test tokena</a> - standardowy test</li>
        <li><a href="/test-api">🧪 Test API</a> - test pełnego API</li>
        <li><a href="/test-models">🤖 Test modeli</a> - test różnych modeli</li>
        <li><a href="/test-simple-api">🧪 Test Simple API</a> - test z najprostszym zapytaniem</li>
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
    HARDCODED_TOKEN = "TOKEN_TEST"  # Wstaw nowy token z HF
    
    # UWAGA: Najpierw wygeneruj nowy token na https://huggingface.co/settings/tokens
    # Potem zastąp "WSTAW_TUTAJ_NOWY_TOKEN" prawdziwym tokenem
    
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
    
    # Użyj nowego tokena gdy go uzyskasz
    TEST_TOKEN = "WSTAW_TUTAJ_NOWY_TOKEN"  # Zastąp prawdziwym tokenem
    
    if TEST_TOKEN == "WSTAW_TUTAJ_NOWY_TOKEN":
        return """
        <h1>⚠️ Wstaw nowy token</h1>
        <p>Wygeneruj nowy token na HF i wstaw go w kodzie</p>
        <p><a href="https://huggingface.co/settings/tokens" target="_blank">🔗 Hugging Face Tokens</a></p>
        """
    
    # Testuj różne proste modele
    simple_models = [
        "gpt2",
        "distilgpt2", 
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

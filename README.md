## 🔧 Rozwiązywanie problemów

### Problem: Błąd 401 "Invalid credentials"
**Przyczyna**: Token Hugging Face jest niepoprawny lub nieaktywny.

**Rozwiązanie**:
1. Przejdź na: https://huggingface.co/settings/tokens
2. Wygeneruj nowy token typu "Read"
3. Skopiuj token (bez spacji!)
4. Zaktualizuj zmienną `HF_TOKEN` w Render
5. Restartuj aplikację

**Szczegółowe instrukcje**: Zobacz plik `NAPRAWA_TOKENA.md`

### Endpointy diagnostyczne
- `/test-token` - test tokena HF
- `/test-api` - test pełnego API
- `/test-models` - test różnych modeli
- `/debug` - informacje systemowe

**Więcej informacji**: Zobacz plik `ENDPOINTY_DIAGNOSTYCZNE.md`

## 🤖 Zmiana modelu AI

Jeśli aktualny model nie działa, możesz zmienić model w pliku `app.py`:

```python
# Zmień tę linię:
API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"

# Na jeden z tych:
# API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
# API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-small-90M"
# API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-small"
```

Użyj endpointu `/test-models` aby sprawdzić, które modele działają.

## 🚀 Najszybsze rozwiązanie

1. **Wygeneruj nowy token HF** (typ "Read")
2. **Zaktualizuj token w Render** (zmienna `HF_TOKEN`) 
3. **Restartuj aplikację**
4. **Test**: Przejdź na `/test-token`

---

# 🔧 Endpointy diagnostyczne chatbota

## Dostępne endpointy testowe

### 1. `/test-token` - Test tokena Hugging Face
- **Cel**: Sprawdza czy token HF jest poprawny
- **Użycie**: `https://twoja-aplikacja.onrender.com/test-token`
- **Co sprawdza**:
  - Długość tokena
  - Pierwsze i ostatnie znaki
  - Autoryzację z API HF
  - Spacje i niepoprawne znaki

### 2. `/test-api` - Test pełnego API
- **Cel**: Testuje kompletne wywołanie API z aktualnym modelem
- **Użycie**: `https://twoja-aplikacja.onrender.com/test-api`
- **Co sprawdza**:
  - Aktualny model (API_URL)
  - Payload i parametry
  - Pełną odpowiedź API
  - Funkcję generuj_odpowiedz

### 3. `/test-models` - Test różnych modeli
- **Cel**: Testuje kilka różnych modeli HF
- **Użycie**: `https://twoja-aplikacja.onrender.com/test-models`
- **Co sprawdza**:
  - facebook/blenderbot-400M-distill
  - microsoft/DialoGPT-medium
  - facebook/blenderbot-small-90M
  - google/flan-t5-small

### 4. `/debug` - Informacje systemowe
- **Cel**: Wyświetla informacje o systemie i konfiguracji
- **Użycie**: `https://twoja-aplikacja.onrender.com/debug`
- **Co wyświetla**:
  - Zmienne środowiskowe
  - Konfigurację aplikacji
  - Status tokena

## 🔍 Jak używać endpointów diagnostycznych

### Krok 1: Test tokena
```
https://twoja-aplikacja.onrender.com/test-token
```
**Oczekiwany rezultat**: Status 200 i komunikat "✅ Token jest poprawny!"

### Krok 2: Test API
```
https://twoja-aplikacja.onrender.com/test-api
```
**Oczekiwany rezultat**: Odpowiedź z API (nie backup)

### Krok 3: Test modeli (opcjonalnie)
```
https://twoja-aplikacja.onrender.com/test-models
```
**Oczekiwany rezultat**: Lista modeli z statusem ✅ OK

## ⚠️ Interpretacja wyników

### Token OK (200)
- ✅ Token jest poprawny
- ✅ Można używać API

### Token Error (401)
- ❌ Token niepoprawny/nieaktywny
- 🔧 Wygeneruj nowy token

### Token Error (429)
- ⚠️ Przekroczono limit API
- 🔧 Poczekaj lub użyj innego tokena

### API Error (503)
- ⚠️ Model przeciążony
- 🔧 Spróbuj innego modelu

## 🛠️ Najczęstsze problemy

1. **Token 401**: Wygeneruj nowy token typu "Read"
2. **API 503**: Model przeciążony - spróbuj innego
3. **API 429**: Przekroczono limit - poczekaj
4. **Spacje w tokenie**: Skopiuj token ostrożnie
5. **Stary token**: Tokeny mogą wygasnąć

## 🎯 Kolejność diagnozowania

1. **Najpierw**: `/test-token` - czy token działa
2. **Potem**: `/test-api` - czy API działa
3. **Jeśli problem**: `/test-models` - znajdź działający model
4. **Na koniec**: `/debug` - pełna diagnostyka

---
**Tip**: Wszystkie endpointy mają linki do innych testów na dole strony dla łatwej nawigacji.

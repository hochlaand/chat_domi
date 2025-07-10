# 🚨 SZYBKA NAPRAWA - Błąd 401 Token

## Problem
Chatbot nie działa - błąd "Invalid credentials in Authorization header"

## ⚡ Szybka naprawa (5 minut)

### Krok 1: Nowy token
1. Otwórz: https://huggingface.co/settings/tokens
2. Zaloguj się
3. Kliknij: **"New token"**
4. Nazwa: `ChatBot-Token`
5. Role: **"Read"**
6. Kliknij: **"Generate a token"**
7. **SKOPIUJ TOKEN NATYCHMIAST** (już się nie pokaże!)

### Krok 2: Zaktualizuj w Render
1. Otwórz: https://dashboard.render.com/
2. Znajdź swoją aplikację chatbota
3. Kliknij na aplikację
4. Zakładka: **"Environment"**
5. Znajdź: `HF_TOKEN`
6. Kliknij: **"Edit"**
7. Wklej nowy token (usuń stary!)
8. Kliknij: **"Save Changes"**

### Krok 3: Restartuj
1. Render automatycznie restartuje aplikację
2. Lub kliknij: **"Manual Deploy"**

### Krok 4: Test
1. Przejdź na: `https://twoja-aplikacja.onrender.com/test-token`
2. Sprawdź czy widzisz: **"✅ Token jest poprawny!"**

## ✅ Działa!
Teraz chatbot powinien odpowiadać z AI, a nie backup odpowiedziami.

## ❌ Nadal nie działa?
1. Sprawdź czy token został skopiowany bez spacji
2. Sprawdź czy token ma typ "Read"
3. Spróbuj wygenerować nowy token
4. Sprawdź `/test-models` - może problem z modelem

---
**Czas wykonania**: 5 minut  
**Koszt**: DARMOWE  
**Wymagania**: Konto Hugging Face (darmowe)

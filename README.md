# AI-chattbot för Försäkringskassan – Streamlit-app med RAG och Google Gemini

AI-chattbot som svarar på frågor om ersättningar från Försäkringskassan, baserat på **Retrieval-Augmented Generation (RAG)** och **Google Gemini**.

Chattboten är tillgänglig via ett interaktivt webbgränssnitt byggt i **Streamlit**.

---

## Funktion

- Använder förtränad Gemini-modell via Google AI Studio
- Söker semantiskt i en faktabas baserad på PDF-dokument från Försäkringskassan
- Ger faktabaserade och kontextstyrda svar
- Etisk systemprompt begränsar hallucinationer
- Automatisk validering av svar i notebook (`chatbot.ipynb`)

---

## Funktioner i Streamlit-appen

- Ställ en fråga direkt i webbläsaren
- AI svarar endast utifrån källtext från Försäkringskassan
- Länk till källa eller kontaktinformation visas vid osäkerhet
- Klar och tydlig stil med användarfokus

---

## Så kör du Streamlit-appen

**1. Klona projektet**

```bash
git clone https://github.com/<ditt-användarnamn>/kunskapskontroll_2.git
cd kunskapskontroll_2
```

**2. Skapa en `.env`-fil med din API-nyckel**

```
API_KEY=din_google_api_nyckel
```

Skapa nyckeln gratis: https://aistudio.google.com/app/apikey

**3. Installera beroenden**

```bash
pip install -r requirements.txt
```

**4. Starta appen**

```bash
streamlit run app.py
```

---

## Utvärdering

Notebooken `chatbot.ipynb` innehåller:

- 8 testfrågor med godkända svar
- Automatisk poängsättning
- Reflektion och förbättringsförslag

---

## Ansvarsfriskrivning

**Observera:** Denna bot är endast ett informationsstöd.
Den ersätter **inte** Försäkringskassans rådgivning eller beslut.
Vid osäkerhet – kontakta alltid Försäkringskassan:
**Telefon:** 0771-524 524
**Webbplats:** https://www.forsakringskassan.se


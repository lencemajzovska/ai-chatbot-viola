# AI-chattbot för Försäkringskassan – Streamlit-app med RAG och Google Gemini

AI-chattbot som svarar på frågor om ersättningar från Försäkringskassan, baserat på **Retrieval-Augmented Generation (RAG)** och **Google Gemini**.

Chattboten är tillgänglig via ett interaktivt webbgränssnitt byggt i **Streamlit**.

---

## 🌐 Testa appen online

👉 [Öppna appen här](https://your-app-url.streamlit.app)

> Denna AI-chattbot är endast tillgänglig via webbappen.

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

## Utvärdering

Notebooken `chatbot.ipynb` innehåller:

- 8 testfrågor med godkända svar
- Automatisk poängsättning
- Reflektion och förbättringsförslag

---

## Ansvarsfriskrivning

**Observera:** Denna bot är endast ett informationsstöd.
Den ersätter **inte** Försäkringskassans rådgivning eller beslut.
Vid osäkerhet kontakta alltid Försäkringskassan.


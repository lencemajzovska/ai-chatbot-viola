# Fråga Viola – AI-chattbot för Försäkringskassan

AI-chattbot som svarar på frågor om ersättningar från Försäkringskassan, baserat på **Retrieval-Augmented Generation (RAG)** och **Google Gemini**.

Webbgränssnittet är byggt med **Streamlit**.

---

## Testa appen online

👉 [Öppna appen här](https://chatbot-viola.streamlit.app)

---

## Funktion

- Använder förtränad Gemini-modell via Google AI Studio
- Söker semantiskt i en faktabas baserad på PDF-dokument från Försäkringskassan
- Ger faktabaserade och kontextstyrda svar
- Systemprompt begränsar hallucinationer

---

## Funktioner i Streamlit-appen

- Ställ en fråga direkt i webbläsaren
- AI svarar endast utifrån källtext från Försäkringskassan
- Länk till källa eller kontaktinformation visas vid osäkerhet
- Tydlig, enkel och användarfokuserad design

---

## Utvärdering

Notebooken `chatbot.ipynb` innehåller:

- Testfrågor och svar
- Automatisk poängsättning av svarens kvalitet
- Reflektion och förbättringsförslag

---

## Ansvarsfriskrivning

**Observera:** Denna bot är endast ett informationsstöd.
Den ersätter **inte** Försäkringskassans rådgivning eller beslut.
Vid osäkerhet kontakta alltid Försäkringskassan.

## Utvecklare

Lence Majzovska
Data Science Student, EC Utbildning 2025
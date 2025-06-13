# Viola – AI-chattbot 

An AI chatbot that answers questions about Swedish social insurance benefits provided by **Försäkringskassan (The Swedish Social Insurance Agency).**
The solution is built using **Retrieval-Augmented Generation (RAG)** and **Google Gemini,** with a web interface developed in **Streamlit.**

---

## Live Demo

👉 [Open the app here](https://chatbot-viola.streamlit.app)

---

## Functionality

- Uses the pre-trained Gemini model via Google AI Studio
- Performs semantic search in a fact base created from official PDF documents from the Swedish Social Insurance Agency
- Provides fact-based and context-aware answers
- System prompt is used to minimize hallucinations

---

## Features of the Streamlit App

- Ask questions directly in the browser
- AI answers strictly based on official Försäkringskassan content
- Displays source links or contact information if uncertainty arises
- Clean, simple, and user-friendly design

---

## Evaluation

The notebook `chatbot.ipynb` includes:

- Test questions and answers
- Automated scoring of answer quality
- Reflection and improvement suggestions

---

## Disclaimer

Disclaimer
**Important:** This chatbot is for informational purposes only.
It does **not** replace official advice or decisions from Försäkringskassan.
For official guidance, always contact Försäkringskassan directly.

## Developer

Lence Majzovska
Data Science Student, EC Utbildning 2025

import os
import re
import numpy as np
import polars as pl
import unicodedata
from pypdf import PdfReader
from google import genai
from google.genai import types

# Grundläggande inställningar
REBUILD = False
CHUNK_SIZE = 1000
K_TOP = 20
EMBEDDING_MODEL = "text-embedding-004"
GENERATION_MODEL = "gemini-2.0-flash"

# Initiera Gemini-klient
client = genai.Client(api_key=os.getenv("API_KEY"))

# Textbearbetning
def read_pdfs_from_folder(folder_path: str) -> str:
    all_text = ""
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            path = os.path.join(folder_path, filename)
            reader = PdfReader(path)
            for page in reader.pages:
                all_text += page.extract_text() or ""
    return all_text

def clean_text(text: str) -> str:
    return unicodedata.normalize("NFKC", re.sub(r'\s+', ' ', text))

def chunk_text(text: str) -> list[str]:
    sentences = text.split(". ")
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if not sentence.endswith((".", "!", "?")):
            sentence += "."
        if len(current_chunk) + len(sentence) + 1 <= CHUNK_SIZE:
            current_chunk = (current_chunk + " " + sentence).strip() if current_chunk else sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

# Embeddings
def create_embedding(text: str, model=EMBEDDING_MODEL, task_type="retrieval_document") -> list[float]:
    response = client.embed_content(
        model=model,
        content=text,
        task_type=task_type
    )
    emb = response.embedding.values
    v = np.array(emb)
    return (v / np.linalg.norm(v)).tolist()

def load_or_build_embeddings(chunks: list[str]) -> tuple[list[str], list[list[float]]]:
    if not REBUILD and os.path.exists("embeddings.parquet"):
        df = pl.read_parquet("embeddings.parquet")
        return df["texts"].to_list(), df["vectors"].to_list()
    embeddings = [create_embedding(chunk) for chunk in chunks]
    df = pl.DataFrame({"texts": chunks, "vectors": embeddings})
    df.write_parquet("embeddings.parquet")
    return chunks, embeddings

# VectorStore-klass
class VectorStore:
    def __init__(self, texts=None, vectors=None):
        self.texts = texts if texts is not None else []
        self.vectors = [np.array(v) for v in vectors] if vectors is not None else []

    def add(self, vector, text):
        self.vectors.append(np.array(vector))
        self.texts.append(text)

    def semantic_search(self, query_embedding, k=K_TOP):
        similarities = [
            (i, np.dot(query_embedding, v) / (np.linalg.norm(query_embedding) * np.linalg.norm(v)))
            for i, v in enumerate(self.vectors)
        ]
        similarities.sort(key=lambda x: x[1], reverse=True)
        k = min(k, len(self.texts))
        return [self.texts[i] for i, _ in similarities[:k]]

# Initiera VectorStore från PDF-mapp
def init_vectorstore(folder_path="data_pdf") -> VectorStore:
    raw_text = read_pdfs_from_folder(folder_path)
    clean = clean_text(raw_text)
    chunks = chunk_text(clean)
    chunks, embeddings = load_or_build_embeddings(chunks)
    vs = VectorStore()
    for chunk, emb in zip(chunks, embeddings):
        vs.add(emb, chunk)
    return vs

# Systemprompt för språkmodellen
system_prompt = """
Du är expert på socialförsäkringsregler.

Du svarar endast på frågor som rör bostadsbidrag, sjukpenning eller föräldrapenning och endast med information som finns i källtexten.
Svara kortfattat och tydligt på det som efterfrågas.

Om frågan gäller hur länge man kan få en ersättning, svara i antal dagar om sådan information finns i källtexten.
Om frågan gäller åldersgränser eller andra villkor, nämn dem punktvis om det behövs.

Om relevant information om frågan **saknas i källtexten**, svara:
"Det framgår inte.

För mer information kontakta Försäkringskassan på 0771-524 524 eller besök [forsakringskassan.se](https://www.forsakringskassan.se)."

Om frågan inte alls gäller bostadsbidrag, sjukpenning eller föräldrapenning, svara:
"Jag kan bara svara på frågor som rör bostadsbidrag, sjukpenning och föräldrapenning."

Om någon frågar vad du heter, svara: "Jag heter Viola. Vad kan jag hjälpa dig med?"
Om någon frågar vad de själva heter, svara: "Det vet jag inte."

Hitta inte på egna fakta.
"""

# Frågefunktion för semantisk sökning och svarsgenerering
def run_semantic_search(question: str, vs: VectorStore) -> str:
    q_emb = create_embedding(question)
    top_texts = vs.semantic_search(q_emb, k=K_TOP)
    context = "\n".join(top_texts)
    prompt = f"Fråga: {question}\n\nKONTEXT:\n{context}"
    response = client.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=system_prompt)
    )
    return response.text

# Exporterar till Streamlit-app
__all__ = [
    "init_vectorstore",
    "run_semantic_search",
    "client",
    "system_prompt",
    "GENERATION_MODEL"
]
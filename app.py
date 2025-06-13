import streamlit as st
import markdown
import html
from chatbot import init_vectorstore, run_semantic_search as semantic_search

# Grundinställningar
st.set_page_config(page_title="Fråga Viola", layout="centered")

# Cache: ladda vectorstore en gång per session
@st.cache_resource
def init_vectorstore_cached():
    return init_vectorstore()

# Initiera session_state
default_state = {
    "vs": None,
    "ready": False,
    "last_query": "",
    "svar": "",
    "input_text": ""
}
for key in default_state:
    st.session_state.setdefault(key, default_state[key])

# Ladda vectorstore vid behov
if not st.session_state.ready or st.session_state.vs is None:
    with st.spinner("Laddar kunskapsdatabasen..."):
        st.session_state.vs = init_vectorstore_cached()
    st.session_state.ready = True

# Formatera fråga och svar som HTML
def format_svar(query, svar):
    user_q = html.escape(query).replace('\n', '<br>').strip()
    bot_a_html = markdown.markdown(svar)
    return (
        f"<b><span style='color:#127247;'>Fråga:</span></b><br>{user_q}<br><br>"
        f"<b><span style='color:#127247;'>Svar:</span></b><br>{bot_a_html}"
    )

# Konvertera markdown-listor till HTML-listor
def convert_markdown_lists(text):
    if "* " not in text:
        return text
    lines = text.split("\n")
    inside_list, new_lines = False, []
    for line in lines:
        if line.strip().startswith("* "):
            if not inside_list:
                new_lines.append("<ul>")
                inside_list = True
            new_lines.append(f"<li>{line.strip()[2:].strip()}</li>")
        else:
            if inside_list:
                new_lines.append("</ul>")
                inside_list = False
            new_lines.append(line)
    if inside_list:
        new_lines.append("</ul>")
    return "\n".join(new_lines)

# Generera svar
def svara(query):
    if not st.session_state.ready or st.session_state.vs is None:
        st.warning("Kunskapsdatabasen är inte laddad än.")
        return

    query = query.strip()

    if not query:
        st.session_state.svar = ""
        return

    # Hälsningar
    greetings = {
        ("hej", "hej!", "hallå", "hejsan", "hej på dig"): "Hej! Vad kan jag hjälpa dig med?",
        ("hejdå", "hej då", "vi ses", "adjö"): "Du är alltid välkommen tillbaka."
    }
    for keys, response in greetings.items():
        if query in keys:
            st.session_state.svar = format_svar(query, response)
            return

    # Filtrera irrelevanta frågor
    irrelevanta = ["hur mår du", "vad gör du", "vad tycker du", "var bor du", "vem är du"]
    if any(fr in query.lower() for fr in irrelevanta):
        st.session_state.svar = format_svar(
            query,
            "Jag kan bara svara på frågor som rör bostadsbidrag, sjukpenning och föräldrapenning."
        )
        return

    # Semantic search
    try:
        svar = semantic_search(query, st.session_state.vs)
        svar = convert_markdown_lists(svar)
        st.session_state.svar = format_svar(query, svar)
    except Exception as e:
        st.error("Något gick fel vid hämtning av svar.")
        return

# CSS och design
st.markdown("""
    <style>
    .block-container {
        max-width: 800px !important;
        margin: 0 auto;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .info-box {
        background-image: linear-gradient(to bottom, #c7dfd8, #e4f3ee) !important;
        border: 1.5px solid #b8ded0;
        border-radius: 8px;
        padding: 24px;
        margin: 20px auto;
        box-shadow: 0 8px 32px 0 rgba(34, 60, 80, 0.22);
        text-align: center;
        max-width: 100%;
        font-size: 1.05rem;
    }
    .stTextInput input {
        background: #e8f0ee;
        border: 1.5px solid #b8ded0 !important;
        border-radius: 8px !important;
        padding: .9rem 1.2rem !important;
        font-size: 1rem !important;
    }
    .stTextInput input::placeholder {
        color: #127247 !important;
        opacity: 1 !important;
    }
    .answer-box {
        background-image: linear-gradient(to bottom, #c7dfd8, #e4f3ee) !important;
        border: 1.5px solid #b4e2cb;
        border-radius: 12px;
        padding: 20px;
        margin-top: 16px;
        box-shadow: 0 8px 32px 0 rgba(34, 60, 80, 0.22);
        position: relative;
        box-sizing: border-box;
        font-size: 1.02rem;
    }
    [data-testid="stSidebar"] {
        background-image: linear-gradient(to bottom, #c7dfd8, #e4f3ee) !important;
        box-shadow: 0 8px 32px 0 rgba(34, 60, 80, 0.22);
    }
    [data-testid="stAppViewContainer"] {
        background: #e8f0ee;
    }
    .mobile-info {
    display: none;
    }
    @media (max-width: 768px) {
        .mobile-info {
            display: block;
            font-size: 0.95rem;
            color: #127247;
            margin-top: 0.5rem;
            text-align: center;
        }
    </style>
    <div class="mobile-info">
        <strong>💡 Klicka på > längst upp till vänster för mer info</strong>
    </div>
""", unsafe_allow_html=True)

# Sidopanel med projektinfo
with st.sidebar:
    st.markdown("""
        <div class="sidebar-section">
            <h3 style="color:#127247; font-weight:bold; font-size: 1.2rem; margin-top: 1.4em;">Om projektet</h3>
            Detta projekt demonstrerar hur <b>Retrieval-Augmented Generation (RAG)</b> i kombination med språkmodellen <b>Google Gemini</b> kan användas för att göra samhällsinformation mer tillgänglig, tydlig och lätt att förstå.
            <br><br>
            Data är hämtad från Försäkringskassans hemsida och omfattar några vanliga ersättningar.
            Lösningen är flexibel och kan enkelt utökas till fler områden eller anpassas med fler funktioner.
        </div><br>
        <hr style="margin: 1.3em 0 1em 0; border: none; border-top: 1.5px solid #b8ded0;" />
        <div class="sidebar-section">
            <h3 style="color:#127247; font-weight:bold; font-size: 1.2rem; margin-top: 1.4em;">Syfte</h3>
            <ul style="margin-top: 0; margin-bottom: 0;">
                <li>Göra det enklare för användare att navigera och förstå information</li>
                <li>Ge tydliga, kortfattade och vägledande svar</li>
                <li>Öka tillgängligheten till faktabaserad information utan att ersätta personlig rådgivning</li><br>
            </ul>
        </div>
        <hr style="margin: 1.3em 0 1em 0; border: none; border-top: 1.5px solid #b8ded0;" />
        <div class="sidebar-section">
            <h3 style="color:#127247; font-weight:bold; font-size: 1.2rem; margin-top: 1.4em;">Information</h3>
            Detta är ett studentprojekt framtaget i utbildningssyfte.
            Informationen bygger på offentlig data från Försäkringskassan och är endast vägledande.
            Svaren är inte juridiskt bindande och Försäkringskassan har inte medverkat i projektet.
        </div>
    """, unsafe_allow_html=True)

# Inforuta på startsidan
st.markdown("""
<div class="info-box">
  <h2 style='color:#127247;'>Fråga Viola</h2>
  <p>
    Har du frågor om <b>sjukpenning</b>, <b>bostadsbidrag</b> eller <b>föräldrapenning</b>?<br>
    Jag hjälper dig att snabbt få vägledande svar baserat på information från Försäkringskassan.
  </p>

  <hr style="margin:1rem 0; border-color:#b8ded0;" />

  <p style="font-size:0.9rem; color:#555;">
    För mer information besök
    <a href="https://www.forsakringskassan.se" target="_blank" style="color:#127247;">
        forsakringskassan.se
    </a> eller kontakta kundcenter på <b>0771-524 524</b>.
  </p>
</div>
""", unsafe_allow_html=True)

# Inputfält
def handle_query():
    query = st.session_state.input_text.strip()
    if query and query != st.session_state.last_query:
        st.session_state.last_query = query
        svara(query)
        st.session_state.input_text = ""

st.text_input(
    label="Frågeruta (dold)",
    placeholder="Skriv din fråga här...",
    key="input_text",
    label_visibility="collapsed",
    on_change=handle_query
)

# Visa svar
if st.session_state.svar:
    svar_text = st.session_state.svar.lower()
    is_unknown = (
        "det vet jag inte" in svar_text
        or "jag kan bara svara på frågor som rör" in svar_text
        or "det framgår inte" in svar_text
        or "jag heter viola" in svar_text
        or "vad kan jag hjälpa dig med" in svar_text
        or "du är alltid välkommen tillbaka" in svar_text
    )

    if not is_unknown:
        query = st.session_state.last_query.lower()

        länk_dict = {
            "bostadsbidrag": "https://www.forsakringskassan.se/privatperson/arbetssokande/bostadsbidrag",
            "sjukpenning": "https://www.forsakringskassan.se/privatpers/sjuk",
            "föräldrapenning": "https://www.forsakringskassan.se/privatperson/foralder/foraldrapenning"
        }

        länk = next(
            (
                f'<a href="{url}" target="_blank" style="color:#127247;">Läs mer om {key}</a>'
                for key, url in länk_dict.items() if key in query
            ),
            'För mer information besök <a href="https://www.forsakringskassan.se" target="_blank" style="color:#127247;">forsakringskassan.se</a>'
        )

        st.markdown(
            f"""
            <div class="answer-box">
                {st.session_state.svar}
                <div style="margin-top: 18px;">{länk}</div>
                <br><b>Kontakta Försäkringskassan vid frågor eller oklarheter.</b>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(f"""
            <div class="answer-box">
                {st.session_state.svar}
            </div>
        """, unsafe_allow_html=True)

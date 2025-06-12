import streamlit as st
import markdown
import html
from chatbot import (
    init_vectorstore,
    run_semantic_search as semantic_search
)

# Grundinställningar
st.set_page_config(page_title="Fråga Viola", layout="centered")

# Cacha vectorstore så den inte laddas om varje gång
@st.cache_resource
def init_vectorstore_cached():
    return init_vectorstore()

# Initiera session_state med defaultvärden en gång per ny session
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.vs = None
    st.session_state.ready = False
    st.session_state.last_query = ""
    st.session_state.svar = ""
    st.session_state.query = ""
    st.session_state.vald_fraga = ""

# Ladda vectorstore om den inte redan är laddad
if st.session_state.vs is None:
    with st.spinner("Laddar kunskapsdatabasen..."):
        st.session_state.vs = init_vectorstore_cached()
    st.session_state.ready = True

# Genererar svar på frågan
def svara():
    if not st.session_state.ready:
        st.warning("Vänta ett ögonblick - data håller fortfarande på att laddas.")
        return

    query = st.session_state.get("vald_fraga") or st.session_state.get("query", "")
    query = query.strip()
    st.session_state.last_query = query

    # Om inget skrivits, töm svaret och avsluta
    if not query:
        st.session_state.svar = ""
        return

    # Filtrerar bort irrelevanta frågor utan att fråga modellen
    irrelevanta = ["hur mår du", "vad gör du", "vad tycker du", "var bor du", "vem är du"]
    if any(fr in query.lower() for fr in irrelevanta):
        st.session_state.svar = (
            "<b><span style='color:#127247;'>Fråga:</span></b><br>" + html.escape(query) + "<br><br>"
            "<b><span style='color:#127247;'>Svar:</span></b><br>Jag kan bara svara på frågor som rör bostadsbidrag, sjukpenning och föräldrapenning."
        )
        st.session_state.vald_fraga = ""
        st.session_state.query = ""
        return

    try:
        svar = semantic_search(query, st.session_state.vs)
    except Exception as e:
        st.error(f"Något gick fel vid hämtning av svar: {e}")
        return

   # Konverterar eventuella markdown-listor till HTML-listor
    if "* " in svar:
        lines = svar.split("\n")
        inside_list = False
        new_lines = []
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
        svar = "\n".join(new_lines)

    user_q = html.escape(query).replace('\n', '<br>').strip()
    bot_a_html = markdown.markdown(svar)

    st.session_state.svar = (
        f"<b><span style='color:#127247;'>Fråga:</span></b><br>{user_q}<br><br>"
        f"<b><span style='color:#127247;'>Svar:</span></b><br>{bot_a_html}"
    )

    st.session_state.vald_fraga = ""
    st.session_state.query = ""

# Anpassad CSS
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
        # transition: border 0.18s;
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
    </style>
""", unsafe_allow_html=True)

# Visar tipsruta endast på mobil
st.markdown("""
<style>
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

# Inforuta
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
    </a> eller kontakta kundcenter på <b>0771-524 524</b>
    </p>
</div>
""", unsafe_allow_html=True)

# Sökfält
st.text_input(
    label="Frågeruta (dold)",
    placeholder="Skriv din fråga här...",
    key="query",
    on_change=svara,
    label_visibility="collapsed"
)

# Visar svaret från modellen
if st.session_state.svar:
    svar_text = st.session_state.svar.lower()
    is_unknown = (
        "det vet jag inte" in svar_text
        or "jag kan bara svara på frågor som rör" in svar_text
        or "det framgår inte" in svar_text
        or "jag heter viola" in svar_text
    )

    # Om svaret är relevant, visa relaterad informationslänk
    if not is_unknown:
        query = st.session_state.last_query.lower()

        # Matcha frågan mot specifika nyckelord för att skapa rätt länk
        if "bostadsbidrag" in query:
            länk = '<a href="https://www.forsakringskassan.se/privatperson/arbetssokande/bostadsbidrag" target="_blank" style="color:#127247;">Läs mer om bostadsbidrag</a>'
        elif "sjukpenning" in query:
            länk = '<a href="https://www.forsakringskassan.se/privatpers/sjuk" target="_blank" style="color:#127247;">Läs mer om sjukpenning</a>'
        elif "föräldrapenning" in query:
            länk = '<a href="https://www.forsakringskassan.se/privatperson/foralder/foraldrapenning" target="_blank" style="color:#127247;">Läs mer om föräldrapenning</a>'
        else:
            länk = 'För mer information besök <a href="https://www.forsakringskassan.se" target="_blank" style="color:#127247;">forsakringskassan.se</a>'

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

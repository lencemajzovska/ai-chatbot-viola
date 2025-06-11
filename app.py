import streamlit as st
import markdown
import html
from chatbot import (
    init_vectorstore,
    run_semantic_search as semantic_search
)

# Grundinställningar för sidan
st.set_page_config(page_title="Fråga Viola", layout="centered")

# Ladda vectorstore och embeddings om det inte redan finns i session_state
if "vs" not in st.session_state:
    st.session_state.vs = init_vectorstore()

# Flagga som indikerar att appen är färdigladdad och redo att ta emot frågor
if "ready" not in st.session_state:
    st.session_state.ready = True  # eftersom vi just initierat den ovan

# Initiera session_state med standardvärden om de saknas
for key, default in [("last_query", ""), ("svar", ""), ("query", ""), ("vald_fraga", "")]:
    if key not in st.session_state:
        st.session_state[key] = default

# Funktion för att hantera användarens fråga och generera svar från modellen
def svara():
    if not st.session_state.ready:
        st.warning("Vänta ett ögonblick - data håller fortfarande på att laddas.")
        return
    # Använd det som skrivits i sökrutan
    query = st.session_state.get("vald_fraga") or st.session_state.get("query", "")
    query = query.strip()
    st.session_state.last_query = query

    # Om inget skrivits, töm svaret och avsluta
    if not query:
        st.session_state.svar = ""
        return

    # Hantera irrelevanta frågor direkt utan att skicka till modellen
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
        # Anropa semantisk sökning och få svar
        svar = semantic_search(query, st.session_state.vs)
    except Exception as e:
        # Visa felmeddelande i appen om något går fel
        st.error(f"Något gick fel vid hämtning av svar: {e}")
        return

   # Om svaret innehåller markdown-listor (* ), konvertera dem till HTML-listor för snyggare visning
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

    # Konvertera användarens fråga och modellens svar till HTML-format för visning
    user_q = html.escape(query).replace('\n', '<br>').strip()
    bot_a_html = markdown.markdown(svar)

    st.session_state.svar = (
        f"<b><span style='color:#127247;'>Fråga:</span></b><br>{user_q}<br><br>"
        f"<b><span style='color:#127247;'>Svar:</span></b><br>{bot_a_html}"
    )

    # Rensa inputfält och återställ knappval
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
        background: #e4f3ee;
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
        background-color: #e4f3ee !important;
        border: 2px solid #b8ded0 !important;
        border-radius: 8px !important;
        padding: .9rem 1.2rem !important;
        font-size: 0.95rem !important;
        transition: border 0.18s;

    }
    .stTextInput input::placeholder {
        color: #127247 !important;
        opacity: 0.8 !important;
        # font-style: italic;
    }
    .answer-box {
        background: #e4f3ee;
        border: 1.5px solid #b4e2cb;
        border-radius: 12px;
        padding: 20px;
        margin-top: 16px;
        box-shadow: 0 8px 32px 0 rgba(34, 60, 80, 0.22);
        position: relative;
        box-sizing: border-box;
        font-size: 1.02rem;
    }
   .box-shadowed {
        background-image: linear-gradient(to bottom, #c7dfd8, #e4f3ee) !important;
        border: 1.5px solid #b8ded0 !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 32px 0 rgba(34, 60, 80, 0.22) !important;
    }
    [data-testid="stSidebar"] {
        background-image: linear-gradient(to bottom, #c7dfd8, #e4f3ee) !important;
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

# Svarsruta – visar resultat från modellen och lägger till en relevant länk baserat på frågans innehåll
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
        # Ta reda på vilket område frågan gäller genom att analysera användarens fråga
        query = st.session_state.last_query.lower()

        # Matcha frågan mot specifika nyckelord för att skapa rätt länk
        if "bostadsbidrag" in query:
            länk = '<a href="https://www.forsakringskassan.se/privatperson/arbetssokande/bostadsbidrag" target="_blank" style="color:#127247;">Läs mer om bostadsbidrag</a>'
        elif "sjukpenning" in query:
            länk = '<a href="https://www.forsakringskassan.se/privatpers/sjuk" target="_blank" style="color:#127247;">Läs mer om sjukpenning</a>'
        elif "föräldrapenning" in query:
            länk = '<a href="https://www.forsakringskassan.se/privatperson/foralder/foraldrapenning" target="_blank" style="color:#127247;">Läs mer om föräldrapenning</a>'
        else:
             # Standardlänk om frågan inte matchar något specifikt område
            länk = '<a href="https://www.forsakringskassan.se" target="_blank" style="color:#127247;">Besök Försäkringskassan för mer information</a>'


        # Visa svaret tillsammans med den relaterade länken och ett råd att kontakta Försäkringskassan
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
        # Om svaret är ett standardsvar, visa bara svaret utan länk

        st.markdown(f"""
            <div class="answer-box">
                {st.session_state.svar}
            </div>
        """, unsafe_allow_html=True)

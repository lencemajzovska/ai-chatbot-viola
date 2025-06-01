import streamlit as st
import markdown
import html
from chatbot import (
    init_vectorstore,
    run_semantic_search as semantic_search
)

# Grundinställningar för sidan
st.set_page_config(page_title="Fråga Viola", layout="wide")

# Initiera vectorstore och ladda embeddings och chunks
vs = init_vectorstore()

# Initiera session_state med standardvärden om de saknas
for key, default in [("last_query", ""), ("svar", "")]:
    if key not in st.session_state:
        st.session_state[key] = default

# Funktion för att hantera fråga från användaren och hämtar svar från modellen
def svara():
    # Läs och spara aktuell fråga från inputfältet
    query = st.session_state.query.strip()
    st.session_state.last_query = query

    # Om inget skrivits, töm svaret och avsluta
    if not query:
        st.session_state.svar = ""
        return

    try:
        # Anropa semantisk sökning och få svar
        svar = semantic_search(query, vs)
    except Exception as e:
        # Visa felmeddelande i appen om något går fel
        st.error(f"Något gick fel vid hämtning av svar: {e}")
        return

    # Konvertera eventuella markdown-listor (* ) till HTML-listor för bättre visning
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

    # Gör frågetexten säker att visa i HTML och ersätt radbrytningar med <br>
    user_q = html.escape(query).replace('\n', '<br>').strip()

    # Konvertera markdown-svaret till HTML
    bot_a_html = markdown.markdown(svar)

    # Spara formaterat fråga-och-svar i session_state för visning i appen
    st.session_state.svar = (
        f"<b><span style='color:#127247;'>Fråga:</span></b><br>{user_q}<br><br>"
        f"<b><span style='color:#127247;'>Svar:</span></b><br>{bot_a_html}"
    )

    # Rensa inputfältet efter att frågan skickats
    st.session_state.query = ""

# Anpassad CSS för bättre utseende och läsbarhet i appen
st.markdown("""
    <style>
    .block-container {
        max-width: 1000px !important;
        margin: 0 auto;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .stTextInput input {
        background-color: #e4f3ee !important;
        border: 2px solid #b8ded0 !important;
        border-radius: 8px !important;
        padding: .9rem 1.2rem !important;
        font-size: 1.14rem !important;
        transition: border 0.18s;
    }
    .stTextInput input::placeholder {
        color: #127247 !important;
        opacity: 0.8 !important;
        font-style: italic;
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


# Sidopanel med information om projektet, syfte och annan viktig info
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
                <li>Öka tillgängligheten till faktabaserad information utan att ersätta personlig rådgivning</li>
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


# Huvudlayout
st.markdown("<div style='margin-top:18px; margin-bottom:18px;'>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

# Info-ruta: Fråga Viola
with col1:
    st.markdown("""
        <div class="box-shadowed" style="
            height: 330px;
            padding: 20px 15px 14px 18px;
            font-size: 1.02em;
            min-height: 120px;
        ">
            <span style="color:#127247; font-weight:500; font-size:1.5em;">🤖 <b>Fråga Viola</span></b>
            <div style="height:0.5em;"></div>
            Viola svarar på frågor om <b>sjukpenning</b>, <b>bostadsbidrag</b><br> och
            <b>föräldrapenning</b> baserat på information från Försäkringskassans webbplats.
            <br><br>
            <b>Ställ en fråga i rutan nedan</b> - <br>
            Till exempel: <i>Hur länge kan jag få sjukpenning?</i><br><br>
            För fullständig information:
            <a href="https://www.forsakringskassan.se" target="_blank" style="color:#127247;">
                forsakringskassan.se
            </a><br>
            För personliga ärenden ring: <b>0771-524 524</b>
        </div>
    """, unsafe_allow_html=True)

# Tips på frågor
with col2:
    st.markdown("""
        <div class="box-shadowed" style="
            height: 330px;
            padding: 16px 12px 12px 14px;
            font-size: 1.02em;
            min-height: 120px;
        ">
            <span style="color:#127247; font-weight:500; font-size:1.5em;">💡 <b>Tips på frågor</b></span>
            <div style="height:0.5em;"></div>
            <ul style="margin-top:0; margin-bottom:0; padding-left:20px;">
                <li>Hur mycket får man i sjukpenning?</li>
                <li>Kan man få sjukpenning som egenföretagare?</li>
                <li>Hur många dagar har jag rätt till med föräldrapenning?</li>
                <li>Kan båda föräldrarna ta ut föräldrapenning samtidigt?</li>
                <li>Får jag föräldrapenning om jag är arbetslös?</li>
                <li>Hur räknas inkomsten för bostadsbidrag?</li>
                <li>Kan jag få bostadsbidrag som student?</li>
                <li>Hur söker jag bostadsbidrag?</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)


# Textfält där användaren skriver sin fråga och skickar den genom att trycka Enter
st.text_input(
    "",
    placeholder="Ställ din fråga här...",
    key="query",
    on_change=svara
)


# Visa svar och eventuell relevant länkif st.session_state.
if st.session_state.svar:
    svar_text = st.session_state.svar.lower()

    # Kontrollera om svaret är ett standardmeddelande som inte kräver länk
    is_unknown = (
        "det vet jag inte" in svar_text
        or "jag kan bara svara på frågor som rör bostadsbidrag, sjukpenning och föräldrapenning" in svar_text
        or "det framgår inte" in svar_text
        or "jag heter viola" in svar_text
    )

    if not is_unknown:
        # Visa passande länk baserat på fråga
        query = st.session_state.last_query.lower()
        if "bostadsbidrag" in query:
            länk = '<a href="https://www.forsakringskassan.se/privatperson/arbetssokande/bostadsbidrag" target="_blank" style="color:#127247;">Läs mer om bostadsbidrag</a>'
        elif "sjukpenning" in query:
            länk = '<a href="https://www.forsakringskassan.se/privatpers/sjuk" target="_blank" style="color:#127247;">Läs mer om sjukpenning</a>'
        elif "föräldrapenning" in query:
            länk = '<a href="https://www.forsakringskassan.se/privatperson/foralder/foraldrapenning" target="_blank" style="color:#127247;">Läs mer om föräldrapenning</a>'
        else:
            länk = '<a href="https://www.forsakringskassan.se" target="_blank" style="color:#127247;">Besök Försäkringskassan för mer information</a>'

        # Visa svar och länk
        st.markdown(
            f"""
            <div class="answer-box">
                {st.session_state.svar}
                <div style="margin-top: 18px;">
                    {länk}
                </div><br>
                🔍 Kontakta Försäkringskassan om du är osäker på vad som gäller för dig
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # Visa bara svaret utan länk eller extra text
        st.markdown(
            f"""
            <div class="answer-box">
                {st.session_state.svar}
            </div>
            """,
            unsafe_allow_html=True
        )

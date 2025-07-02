import streamlit as st
from extract_cv_info import extract_text_from_pdf, extract_text_from_docx, extract_cv_info
from koban_api import send_to_koban

st.set_page_config(page_title="CV Extraction & Integration - Koban", layout="centered")

# --- Style for clean look ---
st.markdown("""
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 1.5rem;}
    .stTextInput>div>div>input {background-color: #f7f8fa; font-size: 1.08rem; height: 2.3em;}
    .stButton>button {background-color: #2563eb; color: white; font-weight: bold; width: 220px; height: 2.5em; border-radius: 6px; margin-top: 18px; box-shadow: 0 2px 4px 0 rgba(50,50,93,.08);}
    .stButton>button:hover {background-color: #1d4ed8; color: white;}
    label, .stTextInput label {font-size: 1rem !important; margin-bottom: 0.3rem !important; font-weight: 500 !important;}
    </style>
""", unsafe_allow_html=True)

st.markdown('<h2 style="text-align:center; margin-bottom:2.3rem;">CV Extraction & Integration - Koban</h2>', unsafe_allow_html=True)

uploaded_files = st.file_uploader("CV Files", type=["pdf", "doc", "docx"], accept_multiple_files=True)

if uploaded_files:
    for i, uploaded_file in enumerate(uploaded_files):
        ext = uploaded_file.name.split('.')[-1].lower()

        # Extraction
        if ext == "pdf":
            text = extract_text_from_pdf(uploaded_file)
        elif ext == "docx":
            text = extract_text_from_docx(uploaded_file)
        elif ext == "doc":
            from extract_cv_info import extract_text_from_doc
            text = extract_text_from_doc(uploaded_file)
        else:
            text = ""
        if text:
            infos = extract_cv_info(text)
            # Create a unique key for each contact's fields
            with st.container():
                st.markdown(
                    f"""
                    <div style='background-color: #f7f8fa; padding: 1.3rem 2.2rem 1.5rem 2.2rem; border-radius: 10px; box-shadow: 0 2px 4px 0 rgba(50,50,93,.06); max-width: 470px; margin: auto; margin-bottom:2.5rem;'>
                    <div style="font-size:1rem; font-weight:600; margin-bottom: 0.6rem; color:#2563eb;">{uploaded_file.name}</div>
                    """, unsafe_allow_html=True
                )

                full_name = st.text_input("Full Name", value=infos.get("full_name",""), key=f"name_{i}")
                email = st.text_input("Email", value=infos.get("email",""), key=f"email_{i}")
                mobile = st.text_input("Phone", value=infos.get("mobile",""), key=f"mobile_{i}")

                # Button aligned left (default)
                if st.button("Create in Koban", key=f"create_{i}"):
                    data = {"full_name": full_name, "email": email, "mobile": mobile}
                    ok, resp = send_to_koban(data)
                    if ok:
                        st.success(f"{full_name} created successfully in Koban!")
                    else:
                        st.error(f"Error creating {full_name}: {resp}")

                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning(f"Could not extract info from {uploaded_file.name}")

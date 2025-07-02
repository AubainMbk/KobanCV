import streamlit as st
from extract_cv_info import extract_text_from_pdf, extract_text_from_docx, extract_cv_info
from koban_api import send_to_koban

st.set_page_config(page_title="CV Extraction & Integration - Koban", layout="centered")

st.markdown('<h2 style="text-align:center;">CV Extraction & Integration - Koban</h2>', unsafe_allow_html=True)

uploaded_files = st.file_uploader("CV Files", type=["pdf", "doc", "docx"], accept_multiple_files=True)

contacts = []

if uploaded_files:
    for i, uploaded_file in enumerate(uploaded_files):
        ext = uploaded_file.name.split('.')[-1].lower()
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
            with st.expander(f"Contact {i+1}: {uploaded_file.name}", expanded=True):
                full_name = st.text_input("Full Name", value=infos.get("full_name",""), key=f"name_{i}")
                email = st.text_input("Email", value=infos.get("email",""), key=f"email_{i}")
                mobile = st.text_input("Phone", value=infos.get("mobile",""), key=f"mobile_{i}")
                contacts.append({"full_name": full_name, "email": email, "mobile": mobile})
        else:
            st.warning(f"Could not extract info from {uploaded_file.name}")

if contacts:
    if st.button("Create all in Koban"):
        created, errors = 0, 0
        for c in contacts:
            ok, resp = send_to_koban(c)
            if ok:
                created += 1
            else:
                errors += 1
        st.success(f"{created} contacts created! {'Errors: ' + str(errors) if errors else ''}")
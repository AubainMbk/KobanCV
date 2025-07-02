import os
import re
from unidecode import unidecode

def extract_text_from_pdf(file_path):
    import pdfplumber
    text = ""
    with pdfplumber.open(file_path) as pdf:
        all_lines = []
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                all_lines += page_text.splitlines()
        text = "\n".join(all_lines)
    return unidecode(text)

def extract_text_from_docx(file_path):
    from docx import Document
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return unidecode(text)

def extract_text_from_doc(file_path):
    try:
        import textract
        text = textract.process(file_path)
        return unidecode(text.decode("utf-8"))
    except ImportError:
        raise RuntimeError("Pour les fichiers .doc, installez textract (`pip install textract`).")
    except Exception as e:
        raise RuntimeError(f"Impossible de lire le .doc : {e}")

def is_line_blacklisted(line):
    blacklist = [
        "francaise", "domicile", "tél", "tel", "email", "mail", "adresse", 
        "paris", "mobilite", "coordonnees", "profil", "competences", "certifications",
        "recherche poste", "experiences", "professionnelles", "curriculum", "vitae",
        "anglais", "stratégie", "strategie", "commercial", "directeur", "digital", "nationale"
    ]
    l_lower = line.lower()
    return any(bl in l_lower for bl in blacklist)

def normalize_french_phone(phone_str):
    # Supprime tout sauf chiffres et +
    s = phone_str
    # Remplace (0) ou ( 0 ) par rien (fréquent dans "+33 (0)6...")
    s = re.sub(r"\(0\)", "", s)
    s = re.sub(r"\(\s*0\s*\)", "", s)
    # Remplace les (33), (+33), +33... par +33
    s = re.sub(r"\(\s*\+?33\s*\)", "+33", s)
    s = re.sub(r"\(\s*33\s*\)", "+33", s)
    s = re.sub(r"\+33", "+33", s)
    s = re.sub(r"0033", "+33", s)
    # Garde uniquement les chiffres après +33 ou 0
    s = re.sub(r"[^\d+]", "", s)
    # Si commence par 0033, remplace par +33
    s = re.sub(r"^0033", "+33", s)
    # Si commence par "0", remplace par "+33"
    if s.startswith("0"):
        s = "+33" + s[1:]
    # Si commence deux fois +33, corrige
    s = re.sub(r"^\+33\+33", "+33", s)
    # Si commence par +330, corrige (cas rare)
    s = re.sub(r"^\+330", "+33", s)
    # Garde format +33XXXXXXXXX (9 chiffres après +33)
    if s.startswith("+33"):
        s = "+33" + s[3:][:9]
    else:
        # Sinon, retourne tel quel
        pass
    return s

def extract_cv_info(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    name = ""
    # (le code de détection du nom reste inchangé)
    for l in lines[:15]:
        words = l.split()
        if len(words) == 2 and l.replace(" ", "").isupper() and not is_line_blacklisted(l):
            name = l.title()
            break
    if not name:
        for l in lines[:15]:
            words = l.split()
            if len(words) == 2 and sum([w.isupper() for w in words]) == 1 and not is_line_blacklisted(l):
                name = " ".join([w.title() if not w.isupper() else w.title() for w in words])
                break
    if not name:
        for l in lines[:15]:
            words = l.split()
            if len(words) == 2 and any(w[0].isupper() for w in words) and not l.isupper() and not is_line_blacklisted(l):
                name = l.title()
                break
    if not name:
        for l in lines[:15]:
            words = l.split()
            if len(words) in [2, 3] and all(w[0].isupper() for w in words if w) and not is_line_blacklisted(l):
                name = l.title()
                break
    if not name:
        for i in range(len(lines[:12])-1):
            first = lines[i].strip()
            second = lines[i+1].strip()
            if (
                not is_line_blacklisted(first)
                and not is_line_blacklisted(second)
                and len(first.split()) == 1 and first[0].isupper() and not first.isupper()
                and len(second.split()) == 1 and second.isupper()
            ):
                name = f"{first.title()} {second.title().title()}"
                break
    if not name and len(lines) > 0:
        first = lines[0]
        words = first.split()
        if (len(words) == 2 and not is_line_blacklisted(first) and
            (words[0][0].isupper() or words[1][0].isupper()) and not first.islower()):
            name = first.title()
    if not name:
        for l in lines:
            if l and not is_line_blacklisted(l):
                name = l.title()
                break

    # Email
    email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    emails = re.findall(email_regex, text)
    email = emails[0] if emails else ""

    # Téléphone français (formats divers avec parenthèses, +, etc.)
    phone_regex = r"((\+|00)?33\s?\(0\)?[\s.-]*\d{1}[\s.-]*\d{2}[\s.-]*\d{2}[\s.-]*\d{2}[\s.-]*\d{2}|(\+|00)?33[\s.-]*\d{1}[\s.-]*\d{2}[\s.-]*\d{2}[\s.-]*\d{2}[\s.-]*\d{2}|0[\s.-]*\d{1}[\s.-]*\d{2}[\s.-]*\d{2}[\s.-]*\d{2}[\s.-]*\d{2}|\(\+33\)[\s.-]*\d{1}[\s.-]*\d{2}[\s.-]*\d{2}[\s.-]*\d{2}[\s.-]*\d{2})"
    phone = ""
    match = re.search(phone_regex, text)
    if match:
        phone_str = match.group()
        phone = normalize_french_phone(phone_str)

    return {
        "full_name": name,
        "email": email,
        "mobile": phone
    }

if __name__ == "__main__":
    cv_filename = "CV_Anthony_MACHLAB_2022_Directeur_QHSE.pdf.158278328.pdf" # adapte si besoin
    cv_path = os.path.join(os.path.dirname(__file__), cv_filename)
    if not os.path.exists(cv_path):
        print(f"CV non trouvé : {cv_path}")
        exit(1)
    ext = os.path.splitext(cv_filename)[1].lower()
    if ext == ".pdf":
        text = extract_text_from_pdf(cv_path)
    elif ext == ".docx":
        text = extract_text_from_docx(cv_path)
    elif ext == ".doc":
        text = extract_text_from_doc(cv_path)
    else:
        print(f"Format non supporté ({ext})")
        exit(1)
    infos = extract_cv_info(text)
    print("Nom extrait :", infos["full_name"])
    print("Email extrait :", infos["email"])
    print("Téléphone extrait :", infos["mobile"])
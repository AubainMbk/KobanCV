import tkinter as tk
from tkinter import filedialog, messagebox
import os

# Import extraction & Koban API modules
from extract_cv_info import (
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_text_from_doc,
    extract_cv_info
)
from koban_api import send_to_koban

class CVExtractorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CV Extraction & Integration - Koban")
        self.geometry("520x350")
        self.resizable(False, False)

        self.cv_path = tk.StringVar()
        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        # CV file section
        tk.Label(self, text="CV File:", font=("Arial", 11)).pack(pady=8)
        file_frame = tk.Frame(self)
        file_frame.pack()
        tk.Entry(file_frame, textvariable=self.cv_path, width=40, state="readonly").pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="Browse...", command=self.load_cv).pack(side=tk.LEFT)

        # Extracted info fields
        tk.Label(self, text="Full Name:", font=("Arial", 11)).pack(pady=8)
        tk.Entry(self, textvariable=self.name_var, width=45).pack()

        tk.Label(self, text="Email:", font=("Arial", 11)).pack(pady=8)
        tk.Entry(self, textvariable=self.email_var, width=45).pack()

        tk.Label(self, text="Phone:", font=("Arial", 11)).pack(pady=8)
        tk.Entry(self, textvariable=self.phone_var, width=45).pack()

        # Send to Koban button with increased height ('height' sets number of text lines)
        tk.Button(
            self, text="Create in Koban", command=self.send_to_koban_ui,
            bg="#3A8DFF", fg="white", height=2, font=("Arial", 10, "bold")
        ).pack(pady=20)

    def load_cv(self):
        filetypes = [("CV Files", "*.pdf *.docx *.doc"), ("All files", "*.*")]
        path = filedialog.askopenfilename(title="Select a CV", filetypes=filetypes)
        if path:
            self.cv_path.set(path)
            try:
                ext = os.path.splitext(path)[1].lower()
                if ext == ".pdf":
                    text = extract_text_from_pdf(path)
                elif ext == ".docx":
                    text = extract_text_from_docx(path)
                elif ext == ".doc":
                    text = extract_text_from_doc(path)
                else:
                    messagebox.showerror("Error", f"Unsupported file format: {ext}")
                    return
                infos = extract_cv_info(text)
                self.name_var.set(infos.get("full_name", ""))
                self.email_var.set(infos.get("email", ""))
                self.phone_var.set(infos.get("mobile", ""))
            except Exception as e:
                messagebox.showerror("Extraction Error", str(e))

    def send_to_koban_ui(self):
        data = {
            "full_name": self.name_var.get(),
            "email": self.email_var.get(),
            "mobile": self.phone_var.get()
        }
        # Optionally check required fields
        if not data["full_name"]:
            messagebox.showwarning("Missing Field", "Please enter the full name.")
            return
        if not data["email"]:
            messagebox.showwarning("Missing Field", "Please enter the email address.")
            return

        try:
            ok, msg = send_to_koban(data)
            if ok:
                messagebox.showinfo("Success", msg)
            else:
                messagebox.showerror("Koban Error", msg)
        except Exception as e:
            messagebox.showerror("Error", f"Error sending data to Koban: {e}")

if __name__ == "__main__":
    app = CVExtractorApp()
    app.mainloop()
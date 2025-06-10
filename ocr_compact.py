#!/usr/bin/env python3

import os
import sys
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import pytesseract
import fitz  # PyMuPDF
from PIL import Image

# === SETTINGS ===
# Path to Tesseract executable (adjust if needed)
TESSERACT_CMD = 'tesseract'
# Ghostscript command
GHOSTSCRIPT_CMD = 'gs'

# === PDF TOOLS ===
def ocr_pdf(input_pdf, output_pdf):
    print(f"OCR processing: {input_pdf}")
    doc = fitz.open(input_pdf)
    pdf_writer = fitz.open()

    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # OCR the image
        text = pytesseract.image_to_pdf_or_hocr(img, extension='pdf')

        # Save as new PDF page
        ocr_page = fitz.open("pdf", text)
        pdf_writer.insert_pdf(ocr_page)

    pdf_writer.save(output_pdf)
    print(f"OCR completed: {output_pdf}")

def shrink_pdf(input_pdf, output_pdf):
    print(f"Shrinking file: {input_pdf}")
    gs_command = [
        GHOSTSCRIPT_CMD,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/screen",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_pdf}",
        input_pdf
    ]
    subprocess.run(gs_command, check=True)
    print(f"Shrinking completed: {output_pdf}")

# === CLI MODE ===
def process_pdfs(pdf_files, action, overwrite):
    for pdf in pdf_files:
        base, ext = os.path.splitext(pdf)
        temp_pdf = pdf

        # Determine output filename
        if overwrite:
            ocr_output = pdf
            shrink_output = pdf
        else:
            ocr_output = f"{base}_ocr.pdf"
            shrink_output = f"{base}_small.pdf"

        if action in ('ocr', 'both'):
            ocr_pdf(pdf, ocr_output)
            temp_pdf = ocr_output

        if action in ('shrink', 'both'):
            shrink_pdf(temp_pdf, shrink_output)

# === GUI MODE ===
def gui_mode():
    def process_files():
        files = list(file_listbox.get(0, tk.END))
        action = action_var.get()
        overwrite = overwrite_var.get()
        process_pdfs(files, action, overwrite)

        messagebox.showinfo("Done", "Processing complete!")

    def add_files():
        files = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        for f in files:
            file_listbox.insert(tk.END, f)

    root = tk.Tk()
    root.title("PDF Tool")

    # Action toggle
    action_var = tk.StringVar(value='both')
    tk.Label(root, text="Select Action:").pack()
    for text, val in [("OCR", "ocr"), ("Shrink", "shrink"), ("Both", "both")]:
        tk.Radiobutton(root, text=text, variable=action_var, value=val).pack(anchor='w')

    # Overwrite toggle
    overwrite_var = tk.BooleanVar()
    tk.Checkbutton(root, text="Overwrite original file", variable=overwrite_var).pack(anchor='w')

    # File list
    file_listbox = tk.Listbox(root, width=80, height=10)
    file_listbox.pack()
    tk.Button(root, text="Add PDF files", command=add_files).pack()

    # Process button
    tk.Button(root, text="Start Processing", command=process_files).pack(pady=10)

    root.mainloop()

# === MAIN ===
if __name__ == "__main__":
    if len(sys.argv) > 1:
        # CLI mode
        import argparse
        parser = argparse.ArgumentParser(description="OCR and shrink PDFs.")
        parser.add_argument('--input', nargs='+', required=True, help="Input PDF files")
        parser.add_argument('--action', choices=['ocr', 'shrink', 'both'], default='both', help="Action to perform")
        parser.add_argument('--output', choices=['overwrite', 'new'], default='new', help="Output mode")
        args = parser.parse_args()

        overwrite = (args.output == 'overwrite')
        process_pdfs(args.input, args.action, overwrite)
    else:
        # GUI mode
        gui_mode()


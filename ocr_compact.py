#!/usr/bin/env python3

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import subprocess
import pytesseract
import fitz  # PyMuPDF
from PIL import Image

# === SETTINGS ===
TESSERACT_CMD = 'tesseract'
TARGET_DPI = 300  # Desired DPI for OCR

# === PDF OCR ===
def ocr_pdf(input_pdf, output_pdf):
    print(f"OCR processing: {input_pdf}")
    doc = fitz.open(input_pdf)
    pdf_writer = fitz.open()

    zoom = TARGET_DPI / 72  # Calculate zoom factor for target DPI
    mat = fitz.Matrix(zoom, zoom)

    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # OCR the image to searchable PDF
        text = pytesseract.image_to_pdf_or_hocr(img, extension='pdf')

        # Save as new PDF page
        ocr_page = fitz.open("pdf", text)
        pdf_writer.insert_pdf(ocr_page)

    pdf_writer.save(output_pdf)
    print(f"OCR completed: {output_pdf}")

# === CLI MODE ===
def process_pdfs(pdf_files, overwrite):
    for pdf in pdf_files:
        base, ext = os.path.splitext(pdf)

        # Determine output filename
        if overwrite:
            output_pdf = pdf
        else:
            output_pdf = f"{base}_ocr.pdf"

        ocr_pdf(pdf, output_pdf)

# === GUI MODE ===
def gui_mode():
    def drop(event):
        files = root.tk.splitlist(event.data)
        for f in files:
            if f.lower().endswith(".pdf"):
                file_listbox.insert(tk.END, f)

    def process_files():
        files = list(file_listbox.get(0, tk.END))
        overwrite = overwrite_var.get()
        process_pdfs(files, overwrite)
        messagebox.showinfo("Done", "OCR processing complete!")

    def add_files():
        files = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        for f in files:
            file_listbox.insert(tk.END, f)

    root = TkinterDnD.Tk()
    root.title("PDF OCR Tool (Drag-and-Drop Ready)")

    # Instructions
    tk.Label(root, text="Drag and drop PDF files below or use the 'Add Files' button").pack(pady=5)

    # Overwrite toggle
    overwrite_var = tk.BooleanVar()
    tk.Checkbutton(root, text="Overwrite original file", variable=overwrite_var).pack(anchor='w', padx=5)

    # File list
    file_listbox = tk.Listbox(root, width=80, height=10)
    file_listbox.pack(padx=5, pady=5)

    # Drag-and-drop support
    file_listbox.drop_target_register(DND_FILES)
    file_listbox.dnd_bind('<<Drop>>', drop)

    # Add Files button
    tk.Button(root, text="Add Files", command=add_files).pack(pady=5)

    # Process button
    tk.Button(root, text="Start OCR Processing", command=process_files).pack(pady=10)

    root.mainloop()

# === MAIN ===
if __name__ == "__main__":
    if len(sys.argv) > 1:
        # CLI mode
        import argparse
        parser = argparse.ArgumentParser(description="OCR PDFs.")
        parser.add_argument('--input', nargs='+', required=True, help="Input PDF files")
        parser.add_argument('--output', choices=['overwrite', 'new'], default='new', help="Output mode")
        args = parser.parse_args()

        overwrite = (args.output == 'overwrite')
        process_pdfs(args.input, overwrite)
    else:
        # GUI mode
        gui_mode()


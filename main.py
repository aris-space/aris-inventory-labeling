import pandas as pd
import qrcode

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
import os
import tkinter as tk
from tkinter import ttk, messagebox

from pypdf import PdfReader, PdfWriter

def generate_label(row):
    # Ensure output directory exists
    output_dir = "labels"
    os.makedirs(output_dir, exist_ok=True)

    asset_tag = row.get("Asset Tag")
    asset_id = row.get('ID')
    pdf_path = os.path.join(output_dir, f"{asset_tag}.pdf")

    # Point QR code to the asset page
    qr_data = f"https://inventory.aris-space.ch/hardware/{asset_id}"
    qr_img = qrcode.make(data=qr_data, error_correction=qrcode.ERROR_CORRECT_H)
    qr_img_path = os.path.join(output_dir, f"{asset_tag}_qr.png")
    with open(qr_img_path, "wb") as file:
        qr_img.save(file)

    # Create PDF
    width = 62 * mm
    height = 29 * mm
    c = canvas.Canvas(pdf_path, pagesize=(width, height))

    # Draw QR code
    qr_size = height - 5 * mm
    c.drawImage(qr_img_path, 0, 5 * mm, qr_size, qr_size, preserveAspectRatio=True)

    c.setFont("Mono", 3.5 * mm)
    c.drawCentredString(qr_size / 2, 3 * mm, f"{asset_tag}")

    # Draw text fields
    font_height = 3 * mm
    text_x = qr_size
    text_y = height - 2 * mm - font_height
    c.setFont("Helvetica", font_height)

    fields = [
        ("Project", row.get("Company", "")),
        ("SN", row.get("Serial", "")),
        ("Location", row.get("Default Location", "")),
        ("Name", row.get("Model", "")),
    ]

    for label, value in fields:
        text = f"{label}: {value}"
        lines = simpleSplit(text, "Helvetica", font_height, 36 * mm)
        for i, line in enumerate(lines):
            if(i == 0):
                c.drawString(text_x, text_y, line)
            else:
                c.drawString(text_x + 2 * mm, text_y, line)

            text_y -= 3.5 * mm

    c.save()
    os.remove(qr_img_path)

    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    writer.add_page(reader.pages[0].rotate(-90))
    writer.write(pdf_path)

    print(f"Generated {pdf_path}")
    return pdf_path

def main():
    # Read CSV
    df = pd.read_csv("data.csv")
    pdfmetrics.registerFont(TTFont('Mono', 'AtkinsonHyperlegibleMono-Regular.ttf'))

    # GUI
    root = tk.Tk()
    root.title("Label Generator")

    tk.Label(root, text="Select Asset Tag:").pack(padx=10, pady=5)
    asset_tags = df["Asset Tag"].astype(str).tolist()
    selected = tk.StringVar()
    dropdown = ttk.Combobox(root, textvariable=selected, values=asset_tags, state="readonly")
    dropdown.pack(padx=10, pady=5)

    def on_generate():
        tag = selected.get()
        if not tag:
            messagebox.showwarning("No Selection", "Please select an asset tag.")
            return
        row = df[df["Asset Tag"].astype(str) == tag].iloc[0]
        pdf_path = generate_label(row)
        messagebox.showinfo("Done", f"Generated {pdf_path}")

    tk.Button(root, text="Generate Label", command=on_generate).pack(padx=10, pady=10)
    root.mainloop()


if __name__ == "__main__":
    main()
import pandas as pd
import qrcode

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit

from pdf2image import convert_from_path

import os
import tkinter as tk
from tkinter import ttk, messagebox


def generate_label(row, output_dir):
    asset_tag = row.get("Asset Tag")
    asset_id = row.get('ID')
    pdf_path = os.path.join(output_dir, f"{asset_tag}.pdf")

    # Point QR code to the asset page
    qr_data = f"https://inventory.aris-space.ch/hardware/{asset_id}"
    qr_img = qrcode.make(data=qr_data, error_correction=qrcode.ERROR_CORRECT_H).rotate(90)
    qr_img_path = os.path.join(output_dir, f"{asset_tag}_qr.png")
    with open(qr_img_path, "wb") as file:
        qr_img.save(file)

    # Create PDF
    width = 29 * mm
    height = 62 * mm
    c = canvas.Canvas(pdf_path, pagesize=(width, height))

    # Draw QR code
    qr_size = width - 5 * mm
    c.drawImage(qr_img_path, 0, 0, qr_size, qr_size, preserveAspectRatio=True)

    # Write all text vertically
    c.translate(width, 0)
    c.rotate(90)
    c.setFont("Mono", 3.5 * mm)
    c.drawCentredString(qr_size / 2, 3 * mm, f"{asset_tag}")

    # Draw text fields
    font_height = 3.2 * mm
    text_x = qr_size
    text_y = width - 2 * mm - font_height
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

    print(f"Generated {pdf_path}")
    return pdf_path


def pdf_to_png(pdf_path):
    image = convert_from_path(pdf_path, dpi=300)
    png_path = os.path.splitext(pdf_path)[0] + ".png"
    image[0].save(png_path, "PNG")
    print(f"Converted {pdf_path} to {png_path}")


def main():
    # Ensure output directory exists
    output_dir = "labels"
    os.makedirs(output_dir, exist_ok=True)

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
        pdf_path = generate_label(row, output_dir)
        pdf_to_png(pdf_path)
        messagebox.showinfo("Done", f"Generated {pdf_path}")

    tk.Button(root, text="Generate Label", command=on_generate).pack(padx=10, pady=10)
    root.mainloop()


if __name__ == "__main__":
    main()
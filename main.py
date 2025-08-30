import pandas as pd
import qrcode

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
import os

def main():
    # Read CSV
    df = pd.read_csv("data.csv")

    # Ensure output directory exists
    output_dir = "labels"
    os.makedirs(output_dir, exist_ok=True)

    pdfmetrics.registerFont(TTFont('Mono', 'AtkinsonHyperlegibleMono-Regular.ttf'))

    for _, row in df.iterrows():
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
        print(f"Generated {pdf_path}")

if __name__ == "__main__":
    main()
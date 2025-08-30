import pandas as pd
import qrcode

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import os

def main():
    # Read CSV
    df = pd.read_csv("data.csv")

    # Ensure output directory exists
    output_dir = "labels"
    os.makedirs(output_dir, exist_ok=True)

    for idx, (_, row) in enumerate(df.iterrows()):
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
        qr_size = height - 7 * mm
        c.drawImage(qr_img_path, 0, 7 * mm, qr_size, qr_size)
        c.setFont("Consolas", 3 * mm)
        c.drawString(2 * mm, 2 * mm, f"{asset_tag}")

        c.save()

        exit()

        # Draw text fields
        text_x = 5 * mm + qr_size + 5 * mm
        text_y = height - 10 * mm
        c.setFont("Helvetica", 3 * mm)
        fields = [
            ("Company", row.get("Company", "")),
            ("Model", row.get("Model", "")),
            ("Model No.", row.get("Model No.", "")),
            ("Serial", row.get("Serial", "")),
            ("Default Location", row.get("Default Location", "")),
        ]
        for label, value in fields:
            c.drawString(text_x, text_y, f"{label}: {value}")
            text_y -= 5 * mm

        c.save()
        os.remove(qr_img_path)
        print(f"Generated {pdf_path}")



if __name__ == "__main__":
    main()

"""
Generates sample PDF and image documents for testing the AI Document Extractor.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sample_dir = Path(__file__).parent

def create_sample_image(text_path: Path, output_png_path: Path):
    with open(text_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Create high-res document image (A4 proportion: ~1240 x 1754 at 150 DPI)
    img = Image.new("RGB", (1240, 1600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Use basic PIL default font or load standard font
    y_offset = 50
    x_offset = 60

    # Draw header banner
    draw.rectangle([(40, 30), (1200, 110)], fill=(240, 243, 248), outline=(30, 64, 175), width=2)
    draw.text((60, 55), "ROYAL SQUARE FINANCIAL - SAPS ACCIDENT DOCKET EVIDENCE", fill=(30, 64, 175))

    lines = text.splitlines()
    curr_y = 140
    for line in lines:
        if line.startswith("===") or line.startswith("---"):
            draw.line([(60, curr_y + 8), (1180, curr_y + 8)], fill=(180, 180, 180), width=1)
            curr_y += 24
        else:
            # Highlight key labels in darker color
            fill_color = (15, 23, 42)
            if any(key in line for key in ["CAS NO", "STATION", "OFFICER", "DATE OF ACCIDENT"]):
                fill_color = (2, 44, 100)
            draw.text((x_offset, curr_y), line, fill=fill_color)
            curr_y += 22

    # Draw simulated police stamp
    draw.ellipse([(900, 1300), (1150, 1550)], outline=(180, 30, 30), width=3)
    draw.text((930, 1370), "SOUTH AFRICAN POLICE", fill=(180, 30, 30))
    draw.text((960, 1410), "SANDTON SAPS", fill=(180, 30, 30))
    draw.text((950, 1450), "OFFICIAL STAMP", fill=(180, 30, 30))
    draw.text((965, 1490), "2024-03-14", fill=(180, 30, 30))

    img.save(output_png_path, "PNG")
    print(f"Created sample image: {output_png_path}")

    # Also save as PDF image
    pdf_path = output_png_path.with_suffix(".pdf")
    img.save(pdf_path, "PDF", resolution=150.0)
    print(f"Created sample image PDF: {pdf_path}")

def create_native_text_pdf(text_path: Path, output_pdf: Path):
    """Creates a native PDF containing searchable text streams."""
    with open(text_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Construct minimal valid PDF 1.4 with text stream
    # Escape parentheses and backslashes in PDF text strings
    stream_lines = ["BT", "/F1 11 Tf", "14.5 TL", "50 780 Td"]
    for line in lines:
        clean = line.rstrip().replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream_lines.append(f"({clean}) '")
    stream_lines.append("ET")
    stream_content = "\n".join(stream_lines).encode("latin-1", errors="replace")

    pdf_body = b"%PDF-1.4\n"
    offsets = []
    
    obj1 = b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    offsets.append(len(pdf_body))
    pdf_body += obj1

    obj2 = b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
    offsets.append(len(pdf_body))
    pdf_body += obj2

    obj3 = b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n"
    offsets.append(len(pdf_body))
    pdf_body += obj3

    obj4 = b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>\nendobj\n"
    offsets.append(len(pdf_body))
    pdf_body += obj4

    obj5 = f"5 0 obj\n<< /Length {len(stream_content)} >>\nstream\n".encode("latin-1") + stream_content + b"\nendstream\nendobj\n"
    offsets.append(len(pdf_body))
    pdf_body += obj5

    xref_offset = len(pdf_body)
    xref = b"xref\n0 6\n0000000000 65535 f \n"
    for off in offsets:
        xref += f"{off:010d} 00000 n \n".encode("latin-1")
    
    trailer = f"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("latin-1")
    
    with open(output_pdf, "wb") as f:
        f.write(pdf_body + xref + trailer)
    print(f"Created native text PDF: {output_pdf}")

if __name__ == "__main__":
    t1 = sample_dir / "saps_accident_report_1.txt"
    t2 = sample_dir / "saps_accident_report_2.txt"

    create_sample_image(t1, sample_dir / "saps_accident_report_1.png")
    create_native_text_pdf(t1, sample_dir / "saps_accident_report_1.pdf")
    create_native_text_pdf(t2, sample_dir / "saps_accident_report_2.pdf")

import sys
import os
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from pypdf import PdfReader, PdfWriter, PageObject


def create_overlay(page_width, page_height, margin, num_lines=25, line_spacing=30):
    """Create an overlay with ruled lines below the slide area."""
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(page_width, page_height))

    # Draw lines for notes (bottom half of page)
    y_start = page_height / 2 - margin
    for i in range(num_lines):
        y = y_start - i * line_spacing
        if y > margin:
            c.line(margin, y, page_width - margin, y)

    c.save()
    packet.seek(0)
    return PdfReader(packet).pages[0]


def add_layout_with_notes(input_pdf, output_pdf, margin = 50):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    page_width, page_height = A4  # portrait A4

    for slide_page in reader.pages:
        # Create a blank A4 page
        new_page = PageObject.create_blank_page(width=page_width, height=page_height)

        # Get slide dimensions
        slide_width = float(slide_page.mediabox.width)
        slide_height = float(slide_page.mediabox.height)

        # Scale slides
        scaling_factor_horisontal = (page_width - 2 * margin) / slide_width
        scaling_factor_vertical = (page_height - 2 * margin) / slide_height
        scaling_factor = min(scaling_factor_horisontal, scaling_factor_vertical)
        slide_page.scale_by(scaling_factor)

        # Place slide
        x_offset = (page_width - slide_width*scaling_factor) / 2
        y_offset = (page_height - slide_height*scaling_factor - margin)

        # Place slide in top
        new_page.merge_translated_page(slide_page, tx=x_offset, ty=y_offset)

        # Add ruled lines overlay
        overlay = create_overlay(page_width, page_height, margin = margin)
        new_page.merge_page(overlay)

        writer.add_page(new_page)

    with open(output_pdf, "wb") as f:
        writer.write(f)


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py input.pdf")
        sys.exit(1)

    input_pdf = sys.argv[1]
    base, ext = os.path.splitext(input_pdf)
    output_pdf = f"{base}_with_lines{ext}"

    add_layout_with_notes(input_pdf, output_pdf)
    print(f"Created: {output_pdf}")

if __name__ == "__main__":
    main()
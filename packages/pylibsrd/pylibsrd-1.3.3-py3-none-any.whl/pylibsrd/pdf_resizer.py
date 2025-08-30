import os
from pypdf import PdfWriter, PdfReader, Transformation


# A4 size in points (1 pt = 1/72 inch)
A4_WIDTH_PT, A4_HEIGHT_PT = 595.28, 841.89  

def resize_pdfs(pdf_path, output_path, width_PT, height_PT):
    """
    Resizes the pdf file ```pdf_path``` into (```width_PT```,```height_PT```) as ```output_path```
    """
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for page in reader.pages:
        orig_width = float(page.mediabox.width)
        orig_height = float(page.mediabox.height)

        # Scale factor to fit within A4
        scale_x = width_PT / orig_width
        scale_y = height_PT / orig_height
        scale_factor = min(scale_x, scale_y)  # Keep aspect ratio

        # Calculate the new width & height after scaling
        new_width = orig_width * scale_factor
        new_height = orig_height * scale_factor

        # Center the scaled content on A4
        offset_x = (A4_WIDTH_PT - new_width) / 2
        offset_y = (A4_HEIGHT_PT - new_height) / 2

        # Apply transformation (scaling + translation)
        transform = Transformation().scale(scale_factor).translate(offset_x, offset_y)
        page.add_transformation(transform)

        # Set the final page size to A4
        page.mediabox.lower_left = (0, 0)
        page.mediabox.upper_right = (A4_WIDTH_PT, A4_HEIGHT_PT)

        writer.add_page(page)

    # Save the resized PDF
    with open(output_path, "wb") as f:
        writer.write(f)
             
    print(f"Pdf resized into {output_path}")

def resize_pdfs_to_a4(pdf_path, output_path):    
    """
    Resizes the pdf file ```pdf_path``` into a4 as ```output_path```
    """
    resize_pdfs(pdf_path, output_path, A4_WIDTH_PT, A4_HEIGHT_PT)


def _script():
    folder_path = os.getcwd()
    proceed = input(f"Will resize all pdfs found in folder: {folder_path}\nProceed? (y/n):")

    if proceed.lower() != "y":
        return

    pdf_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')])
    # If no pdf files found, abort.
    if len(pdf_files) == 0:
        print("No pdf files found. Aborting.")
        return
    
    os.makedirs("Output", exist_ok=True)
    for pdf in pdf_files:
        resize_pdfs_to_a4(pdf, os.path.join("Output", os.path.splitext(pdf)[0] + "[A4].pdf"))

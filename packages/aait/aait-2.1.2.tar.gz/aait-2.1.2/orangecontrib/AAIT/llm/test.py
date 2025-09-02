import fitz  # PyMuPDF
import os
import re


def clean_filename(text, max_length=50):
    # Sanitize filename: remove forbidden characters and truncate if too long
    text = re.sub(r'[\\/*?:"<>|]', "", text)  # Remove illegal characters
    text = text.strip()
    return text[:max_length] if len(text) > max_length else text


def split_pdf_with_title(input_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(input_path)

    for i in range(len(doc)):
        page = doc[i]
        text = page.get_text().strip()
        first_line = text.split("\n")[0] if text else f"page_{i + 1}"
        last_line = text.split("\n")[-2] if text else f"page_{i + 1}"
        filename = clean_filename(last_line) or f"page_{i + 1}"

        single_page = fitz.open()
        single_page.insert_pdf(doc, from_page=i, to_page=i)

        output_path = os.path.join(output_dir, f"{filename}.pdf")
        single_page.save(output_path)
        single_page.close()
        print(f"Saved: {output_path}")

    doc.close()


# Exemple d'utilisation
input_pdf = r"C:\Users\lucas\Downloads\FICHES-VINS-MILL2021_PAQUET.pdf"
output_folder = r"C:\Users\lucas\Desktop\Datasets\Wine"
split_pdf_with_title(input_pdf, output_folder)

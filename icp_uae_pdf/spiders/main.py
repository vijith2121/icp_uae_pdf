import scrapy
from icp_uae_pdf.items import Product
from lxml import html
import os
import fitz
from urllib.parse import urljoin
import re
from PIL import Image
import pytesseract
from scrapy.http import Request
import io

def extract_text_and_images(pdf_path, output_dir="extracted_images"):
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    all_text = ""
    image_paths = []

    for page_number in range(len(doc)):
        page = doc[page_number]
        text = page.get_text().strip()

        if not text:
            # Use OCR
            pix = page.get_pixmap(dpi=300)
            img_path = f"{output_dir}/page{page_number+1}_ocr.png"
            pix.save(img_path)
            ocr_text = pytesseract.image_to_string(Image.open(img_path))
            all_text += f"\n--- Page {page_number + 1} (OCR) ---\n{ocr_text}"
        else:
            all_text += f"\n--- Page {page_number + 1} ---\n{text}"

        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_filename = f"{output_dir}/page{page_number+1}_img{img_index+1}.{image_ext}"
            with open(image_filename, "wb") as f:
                f.write(image_bytes)
            image_paths.append(image_filename)

    doc.close()
    return all_text, image_paths

class IcpUaePdfSpider(scrapy.Spider):
    name = "icp_uae_pdf"
    # start_urls = ["https://example.com"]  # Replace with the real URL

    # def start_requests(self):
    #     # Point to your local PDF directory
    #     script_directory = os.path.dirname(os.path.abspath(__file__))
    #     pdf_dir = script_directory  # or a subfolder like os.path.join(script_directory, "pdfs")

    #     pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]
    #     for pdf_file in pdf_files:
    #         pdf_path = os.path.join(pdf_dir, pdf_file)
    #         print(pdf_file)
    #         yield self.parse_pdf(pdf_path)
    def start_requests(self):
        script_directory = os.path.dirname(os.path.abspath(__file__))
        pdf_dir = script_directory
        pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]

        for pdf_file in pdf_files:
            pdf_path = os.path.join(pdf_dir, pdf_file)
            yield Request(
                # url="file://" + pdf_path,  # Dummy URL
                # url = f"file:///home/Desktop/vijith/icp_uae_pdf/icp_uae_pdf/spiders/{pdf_path}",
                url = 'https://www.example.com/',
                callback=self.parse_pdf,
                meta={"pdf_path": pdf_path},
                dont_filter=True
            )

    def parse_pdf(self, response):
        pdf_path = response.meta.get('pdf_path')
        text, images = extract_text_and_images(pdf_path)
        # item = PdfExtractedItem()
        with open(pdf_path, 'rb') as f:
            pdf_binary_data = f.read()
        item = {}
        item['file_name'] = os.path.basename(pdf_path)
        item['text'] = text
        item['images'] = images

        date_of_pattern = r'\b\d{2}:\d{2}\b\s+(\d{2}/\d{2}/\d{4})'
        try:
            date_of_birth = re.search(date_of_pattern, text.split('DATE OF BIRTH')[-1]).group(1)
        except Exception as error:
            print(error)
            date_of_birth = ''
        if not date_of_birth:
            date_of_birth = text.split('DATE OF BIRTH')[-1].strip().split('E-MAIL')[0].strip().split()[-1]

        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        email = re.findall(email_pattern, text)
        name = ''.join(
            text.split('NAME')[-1].split('NATIONALIT')[0].strip().replace(':', '').strip()
        )

        if 'Juall' in name:
            name = name.split(' Juall')[0].strip()
        if 'giilaly' in name:
            name = name.split('giilaly')[0].strip()
        if 'ugllu' in name:
            name = name.split('ugllu')[0].strip()
            #jgaioga
        if 'ginuglga' in name:
            name = name.split('ginuglga')[0].strip()
        if 'jgaioga' in name:
            name = name.split('jgaioga')[0].strip()

        nationality = ''.join(
            text.split('NATIONALITY :')[-1].strip().split(' ')[0]
        )
        # gender = ''.join(
        #     text.split('GENDER :')[-1].strip().split('FILE NUMBER')[0].strip().split(' ')[0].strip()
        # )
        gender_pattern = r'GENDER\s*[:=>-]?\s*(MALE|FEMALE)'
        try:
            gender_match = re.search(gender_pattern, text, re.IGNORECASE)
            gender = gender_match.group(1).capitalize()
        except Exception as error:
            print(error)
            gender = ''

        contact_pattern = r'\b00971\s?\d{8,9}\b'
        contact_matches = re.findall(contact_pattern, text)
        contact = ''
        if contact_matches is not None:
            contact = contact_matches[0]
        print(contact)            
        if 'PHONE NO.' in contact:
            contact = contact.split(' ')[-1].strip()
        submit_date = text.split('SUBMITTED ON')[-1].strip().split(':')[0].strip()
        submit_date = ''.join(
            [i for i in submit_date.split() if '/' in i]
        )
        data = {
            'name': str(name).replace('>', '').strip() if name else '',
            'date_of_birth': str(date_of_birth) if date_of_birth else '',
            'email': ''.join(email).strip() if email else '',
            'nationality': str(nationality) if nationality else '',
            'gender': str(gender) if gender else '',
            'contact': str(contact) if contact else '',
            'submit_date': str(submit_date) if submit_date else '',
            'images': str(images) if images else '',
            'file_name': str(os.path.basename(pdf_path)) if os.path.basename(pdf_path) else '',
            'emirates_id': str(os.path.basename(pdf_path)).replace('.pdf', '').strip(),
            'pdf_text': str(pdf_binary_data)
        }
        yield Product(**data)
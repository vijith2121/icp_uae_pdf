import scrapy
# from icp_uae_pdf.items import Product
from lxml import html

class Icp_uae_pdfSpider(scrapy.Spider):
    name = "icp_uae_pdf"
    start_urls = ["https://example.com"]

    def parse(self, response):
        parser = html.fromstring(response.text)
        print("Visited:", response.url)

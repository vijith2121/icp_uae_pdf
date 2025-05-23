import scrapy

class Product(scrapy.Item):
    name = scrapy.Field()
    date_of_birth = scrapy.Field()
    email = scrapy.Field()
    nationality = scrapy.Field()
    gender = scrapy.Field()
    contact = scrapy.Field()
    submit_date = scrapy.Field()
    images = scrapy.Field()
    file_name = scrapy.Field()
    emirates_id = scrapy.Field()
    pdf_text = scrapy.Field()
    
    
    
    
    # 'name': name if name else '',
    #         'date_of_birth': date_of_birth if date_of_birth else '',
    #         'email': email if email else '',
    #         'nationality': nationality if nationality else '',
    #         'gender': gender if gender else '',
    #         'contact': contact if contact else '',
    #         'submit_date': submit_date if submit_date else '',
    #         'images': images if images else '',
    #         'file_name': os.path.basename(pdf_path) if os.path.basename(pdf_path) else ''


 
from datetime import datetime, timedelta
import scrapy

class TechCrunchScraper(scrapy.Spider):
    name = "techcrunch"

    def start_requests(self):
        start_date = datetime(2018, 5, 1)
        date = start_date
        while date <= datetime.now():
            print(self.generate_url(date))
            new_request = scrapy.Request(self.generate_url(date))
            new_request.meta["date"] = date
            new_request.meta["page_number"] = 1 
            yield new_request 
            date += timedelta(days=1)

    def generate_url(self, date, page_number=None):
    url = 'https://techcrunch.com/' + date.strftime("%Y/%m/%d") + "/"
    if page_number:
        url  += "page/" + str(page_number) + "/"
    return url

    def parse(self, response):
    date = response.meta['date'] # defined above 
    page_number = response.meta['page_number']
 
    articles = response.xpath('//h2[@class="post-title"]/a/@href').extract()
    for url in articles:
        request = scrapy.Request(url,
                        callback=self.parse_article)
        request.meta['date'] = date
        yield request
 
    url = self.generate_url(date, page_number+1)
    request = scrapy.Request(url,
                    callback=self.parse)
    request.meta['date'] = date
    request.meta['page_number'] = page_number
    yield request
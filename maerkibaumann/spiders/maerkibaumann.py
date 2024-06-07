import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from maerkibaumann.items import Article


class MaerkibaumannSpider(scrapy.Spider):
    name = 'maerkibaumann'
    start_urls = ['https://www.maerki-baumann.ch/de/publikationen-und-anlaesse']

    def parse(self, response):
        links = response.xpath('//div[@class="button"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//nav[@class="breadcrumb"]//li[last()]//text()').get()
        if title:
            title = title.strip()

        date = response.xpath('(//div[@class="stage_text"]//p)[last()]//text()').get()
        if date:
            date = " ".join(date.strip().split()[-2:])

        content = response.xpath('//div[@class="node__content"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()

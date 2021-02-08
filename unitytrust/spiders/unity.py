import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from unitytrust.items import Article


class UnitySpider(scrapy.Spider):
    name = 'unity'
    start_urls = ['https://www.unity.co.uk/news/']

    def parse(self, response):
        links = response.xpath('//h3/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get().strip()
        date = " ".join(response.xpath('//span[@class="date"]/text()').get().strip().split()[:3])
        date = datetime.strptime(date, '%B %d, %Y')
        date = date.strftime('%Y/%m/%d')
        content = response.xpath('//article//p//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()
        category = response.xpath('//span[@class="taxonomy-lbl"]/text()').get().strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('category', category)

        return item.load_item()

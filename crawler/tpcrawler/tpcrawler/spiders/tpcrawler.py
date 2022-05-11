import scrapy
from scrapy.utils.response import open_in_browser
from scrapy.http import TextResponse
import re
import fandom
import json

fandom.set_wiki("Twinpeaks")

article_id_pattern="wgArticleId\"\:([0-9]+)"
categories_xpath="//div[@class='page-header__categories']/a//text()"
excluded_categories=set("""Twin Peaks (2017) crew
Actors
Camera and electrical department
Casting department
Catering department
Costume department
Directors
Editors
Location department
Makeup department
Medics
Music department
Producers
Production associates
Special and visual effects department
Stand-ins
Story editors
Stunt department
Transportation department
Writers
Years
Decades
Days
Production timeline""".split("\n"))

#print(excluded_categories)

class Tpcrawler(scrapy.Spider):
    name = 'tpcrawler'
    allowed_domains = ['https://twinpeaks.fandom.com/']
    start_urls = ['https://twinpeaks.fandom.com/wiki/Special:AllPages']

    
    def parse(self, response):
        #open_in_browser(response)

        hrefs = response.xpath("//ul[@class='mw-allpages-chunk']/li/a[not(contains(@class, 'redirect'))]/@href").extract()
        for href in hrefs:
            yield scrapy.Request(url=response.urljoin(href), callback=self.parse_page, dont_filter=True,
            meta={'name':href.rpartition('/')[-1],
            'url':response.urljoin(href)})

        next_page =  response.xpath("//div[@class='mw-allpages-nav']/a[contains(.,'Next page')]/@href").extract_first()

        if next_page:
            yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse, dont_filter=True)

    def parse_page(self, response: TextResponse):
        categories = set(response.xpath(categories_xpath).extract())
        #print(categories)
        if len(categories.intersection(excluded_categories))==0:
            name = response.meta['name']
            url = response.meta['url']
            article_id = int(re.findall(article_id_pattern, response.text)[0])

        # una volta trovato l'id, usa l'API di fandom per recuperare solo il testo della voce
            page = fandom.page(pageid = article_id)
            
            text = page.plain_text.split('\nAppearances\n')[0].split('\nReferences\n')[0]
            
            json_content={'name': name, 'url':url, 'text':text}

            with open(f'./data/{name}.json','w', encoding='utf-8') as fout:
                json.dump(json_content, fout)








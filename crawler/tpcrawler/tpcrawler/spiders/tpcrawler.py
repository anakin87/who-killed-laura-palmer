import scrapy
from scrapy.http import TextResponse
import re
import fandom
import json

# Categories unrelated to Twin Peaks plot
# (they make noise in the index)
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

fandom.set_wiki("Twinpeaks")

article_id_pattern = "wgArticleId\"\:([0-9]+)"
categories_xpath = "//div[@class='page-header__categories']/a//text()"
wiki_page_href_xpath = "//ul[@class='mw-allpages-chunk']/li/a[not(contains(@class, 'redirect'))]/@href"
next_page_href_xpath = "//div[@class='mw-allpages-nav']/a[contains(.,'Next page')]/@href"


class Tpcrawler(scrapy.Spider):
    name = 'tpcrawler'
    allowed_domains = ['https://twinpeaks.fandom.com/']
    start_urls = ['https://twinpeaks.fandom.com/wiki/Special:AllPages']

    
    def parse(self, response):
        """Start from wiki "all pages" list and open them"""
        hrefs = response.xpath(wiki_page_href_xpath).extract()
        for href in hrefs:
            yield scrapy.Request(url=response.urljoin(href),
                callback=self.parse_page, dont_filter=True,
                meta={'name':href.rpartition('/')[-1],
                'url':response.urljoin(href)})

        next_page =  response.xpath(next_page_href_xpath).extract_first()
        if next_page:
            yield scrapy.Request(url=response.urljoin(next_page),
                callback=self.parse, dont_filter=True)

    def parse_page(self, response: TextResponse):
        """
        Collect all interesting pages IDs
        and use the Fandom API to crawl them.
        Save the output in JSON format.
        """

        categories = set(response.xpath(categories_xpath).extract())
        
        # the wiki page is interesting only if related to plot
        # (= not contained in excluded categories)
        if len(categories.intersection(excluded_categories))==0:
            name = response.meta['name']
            url = response.meta['url']
            article_id = int(re.findall(article_id_pattern, response.text)[0])

            # once the ID is found, use the Fandom API to retrieve the clean page text
            page = fandom.page(pageid = article_id)            
            text = page.plain_text.split('\nAppearances\n')[0]\
                .split('\nReferences\n')[0]
            json_content={'name': name, 'url':url, 'text':text}
            with open(f'./data/{name}.json','w', encoding='utf-8') as fout:
                json.dump(json_content, fout)
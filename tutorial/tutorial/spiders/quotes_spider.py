# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from tutorial.items import ChemItem

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    # allowed_domains = ["chembridge.com"]
    headers=[{
            'Host':'www.chembridge.com',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding':'gzip, deflate',
            'Referer':'http://www.chembridge.com/search/search.php?search=1',
            'Connection':'keep-alive',
            'Upgrade-Insecure-Requests':'1'
        },
        {
            'Host':'www.hit2lead.com',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding':'gzip, deflate, br'
        }]
    def start_requests(self):
        start_urls = []
        f=open('MDL.txt','r')
        for line in f.readlines():
            line=line.strip()
            print(line)
            start_urls.append('http://www.chembridge.com/search/search.php?searchType=MFCD&query='+line+'&type=phrase&results=10&search=1')
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse,headers=self.headers[0])

    def parse(self, response):
        links=response.css('#BBResults a.chemical::attr(href)').extract()
        for link in links:
            yield scrapy.Request(url=link,callback=self.parse_dir_contents,headers=self.headers[1])

    def parse_dir_contents(self, response):
        items=[]
        catalogs=response.css('form div.matter h2::text').extract()
        table_headers=[''.join(res.re(r'>(.*)</td>')) for res in response.css('form div.matter thead tr')]
        print(table_headers)
        index=table_headers.index('AmountPriceQty.')
        catalog=catalogs[0]
        trs=response.css('.form tbody tr')
        if len(catalogs)>1:
            catalog=catalogs[index]
        for tr in trs:
            if len(tr.css('td'))>1:
                item=ChemItem()
                # print(tr.css('td::text').extract())
                # row=tuple([catalog])+tuple(td.get_text("|", strip=True) for td in tr.css('td'))
                item['catalog']=catalog
                item['amount']=tr.css('td')[0].css('::text').extract()[0]
                item['price']='|'.join(tr.css('td')[1].css('::text').extract())
                print(len(tr.css('td::text')))
                item['qty']=tr.css('td')[2].css('::text').extract()[0] if len(tr.css('td')[2].css('::text').extract())==1 else tr.css('td')[2].css('::attr(value)').extract()[0]
                # self.log('Saved result %s' % item)
                # print(tr.css('td::text')[0].extract())
                yield item
                # items.append(item)
        # return items
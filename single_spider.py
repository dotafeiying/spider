# -*- coding:utf-8 -*-
import requests,random,time
from bs4 import BeautifulSoup
import mysql.connector

class Spider:
    def __init__(self):
        self.headers=[{
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
        self.filename='MDL1.txt'

    def get_page_link(self,link):
        res=[]
        href=link.get('href')
        print(href)
        parse_html=requests.get(href,headers=self.headers[1]).text
        soup1=BeautifulSoup(parse_html, 'lxml')
        catalogs=[catalog.get_text() for catalog in soup1.select('form div.matter h2')]#获取catalog
        print(catalogs)
        table_headers=[table_header.get_text(strip=True) for table_header in soup1.select('form .matter thead tr')]
        print(table_headers)
        index=table_headers.index('AmountPriceQty.')
        catalog=catalogs[0]
        trs=soup1.select('.form tbody tr')
        # print(trs)
        if len(catalogs)>1:
            catalog=catalogs[index]
        for tr in trs:
            if len(tr.select('td'))>1:
                row=tuple([catalog])+tuple(td.get_text("|", strip=True) for td in tr.select('td'))
                res.append(row)
        print(res)
        conn=mysql.connector.connect(host='10.39.211.198',user='root', passwd='password', db='test')
        cursor = conn.cursor()
        sql = 'INSERT INTO chembridge_test2 VALUES(%s,%s,%s,%s)'
        cursor.executemany(sql,res)
        conn.commit()
        cursor.close()
        conn.close()

    def get_page(self,line):
        url='http://www.chembridge.com/search/search.php?searchType=MFCD&query='+line+'&type=phrase&results=10&search=1'
        try:
            response = requests.get(url,headers=self.headers[0],timeout=20)
            print(response.status_code)
            html_doc=response.text
            # print(html_doc)
            soup = BeautifulSoup(html_doc, 'lxml')
            div=soup.find(id='BBResults')
            if div:
                links=div.select('a.chemical')
                for link in links:
                    self.get_page_link(link)
            relay=random.randint(2,5)/10
            print(relay)
            time.sleep(relay)
        except Exception as e:
            print('except:', e)

    def get_file(self,filename):
        i=0
        f=open(filename,'r')
        for line in f.readlines():
            line=line.strip()
            print(line)
            self.get_page(line)
            i=i+1
            print('第%s个'%(i))
        f.close()

    def run(self):
        self.get_file(self.filename)

spider=Spider()
starttime=time.time()
spider.run()
print('耗时：%f s'%(time.time()-starttime))
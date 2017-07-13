# coding=utf-8
import threading
import queue,requests
import time,random
import mysql.connector
from bs4 import BeautifulSoup

class Fetcher(threading.Thread):
    def __init__(self,urls_queue,html_queue):
        threading.Thread.__init__(self)
        self.__running=threading.Event()
        self.__running.set()
        self.urls_queue = urls_queue
        self.html_queue = html_queue
        self.num_retries=3  #设置尝试重新搜索次数
        self.headers={
            'Host':'www.chembridge.com',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding':'gzip, deflate',
            'Referer':'http://www.chembridge.com/search/search.php?search=1',
            'Connection':'keep-alive',
            'Upgrade-Insecure-Requests':'1'
        }

    def run(self):
        while not self.urls_queue.empty():
        # while self.__running.isSet():
            line=self.urls_queue.get()
            print(line)
            time.sleep(2*random.randint(5,15)/10)
            # self.urls_queue.task_done()
            self.get_page(line,self.num_retries)
    def get_page(self,line,num_retries=2):
        url='http://www.chembridge.com/search/search.php?searchType=MFCD&query='+line+'&type=phrase&results=10&search=1'
        try:
            response = requests.get(url,headers=self.headers,timeout=20)
            status=response.status_code
            if status==200:
                html_doc=response.text
                print(html_doc)
                self.html_queue.put(html_doc)
                # self.urls_queue.task_done()
                print('%s搜索完成'%line)
            else:
                print('搜索%s网络异常,错误代码：%s'%(line,status))
                if num_retries>0:
                    print('尝试重新搜索%s'%(line))
                    time.sleep(2*random.randint(5,15)/10)
                    self.get_page(line,num_retries-1)
                else:
                    print('%s四次搜索失败!!!'%line)
                    self.urls_queue.put(line)

        except Exception as e:
            print('%s搜索异常,error:'%line,e)
            if num_retries>0:
                print('尝试重新搜索%s'%(line))
                time.sleep(2*random.randint(5,15)/10)
                self.get_page(line,num_retries-1)
            else:
                print('%s四次搜索失败!!!'%line)
                self.urls_queue.put(line)

    def stop(self):
        self.__running.clear()

class Parser(threading.Thread):
    def __init__(self, html_queue,item_queue):
        threading.Thread.__init__(self)
        self.__running=threading.Event()
        self.__running.set()
        self.html_queue = html_queue
        self.item_queue = item_queue
        self.num_retries=3  #设置尝试重新搜索次数
        self.headers={
            'Host':'www.hit2lead.com',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding':'gzip, deflate, br'
        }
    def run(self):
        while self.__running.isSet():
            print('html_queue长度: ',self.html_queue.qsize())
            # if self.html_queue.empty():
            #     break
            html_doc=self.html_queue.get()
            try:
                soup = BeautifulSoup(html_doc, 'lxml')
                div=soup.find(id='BBResults')
                if div:
                    links=div.select('a.chemical')
                    for link in links:
                        self.get_page_link(link,self.num_retries)
                relay=random.randint(20,50)/10
                # print(relay)
                time.sleep(relay)
            except Exception as e:
                self.html_queue.put(html_doc)
            # self.html_queue.task_done()

    def get_page_link(self,link,num_retries=2):
        print('haha')
        time.sleep(2*random.randint(5,15)/10)
        res=[]
        href=link.get('href')
        print(href)
        response=requests.get(href,headers=self.headers,timeout=20)
        status=response.status_code
        if status==200:
            parse_html=response.text
            soup1=BeautifulSoup(parse_html, 'lxml')
            catalogs=[catalog.get_text() for catalog in soup1.select('form div.matter h2')]#获取catalog
            # print(catalogs)
            table_headers=[table_header.get_text(strip=True) for table_header in soup1.select('form .matter thead tr')]
            # print(table_headers)
            if 'AmountPriceQty.' in table_headers:
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
                # print(res)
                self.item_queue.put(res)
        else:
            print('搜索%s网络异常,错误代码：%s'%(link,status))
            # time.sleep(self.relay*random.randint(5,15)/10)
            if num_retries>0:
                print('尝试重新搜索%s'%(link))
                time.sleep(random.randint(5,15)/10)
                self.get_page_link(link,num_retries-1)
            else:
                print('%s四次搜索失败!!!'%line)
    def stop(self):
        self.__running.clear()

class Saver(threading.Thread):
    def __init__(self, item_queue):
        threading.Thread.__init__(self)
        self.__running=threading.Event()
        self.__running.set()
        self.item_queue = item_queue

    def run(self):
        # while not self.item_queue.empty():
        while self.__running.isSet():
            print('item_queue长度: ',self.item_queue.qsize())
            res=self.item_queue.get()
            print(res)
            conn=mysql.connector.connect(host='10.39.211.198',user='root', passwd='password', db='test')
            cursor = conn.cursor()
            sql = 'INSERT INTO chembridge_test2 VALUES(%s,%s,%s,%s)'
            cursor.executemany(sql,res)
            print('入库')
            conn.commit()
            cursor.close()
            conn.close()
    def stop(self):
        self.__running.clear()


if __name__ == '__main__':
    starttime=time.time()
    lock = threading.Lock()
    urls_queue = queue.Queue()
    html_queue = queue.Queue()
    item_queue = queue.Queue()

    conn=mysql.connector.connect(host='10.39.211.198',user='root', passwd='password', db='test')
    cursor = conn.cursor()
    print('清空表...')
    cursor.execute('delete from chembridge_test2')
    conn.commit()
    cursor.close()
    conn.close()

    print('start...')

    f=open('MDL1.txt','r')
    for line in f.readlines():
        line=line.strip()
        urls_queue.put(line)
    f.close()

    threads=[]
    for j in range(8):
        thread1 = Fetcher(urls_queue,html_queue)
        thread1.setDaemon(True)
        thread1.start()
        threads.append(thread1)
    for j in range(8):
        thread1 = Parser(html_queue,item_queue)
        thread1.setDaemon(True)
        thread1.start()
        threads.append(thread1)
    for j in range(1):
        thread1 = Saver(item_queue)
        thread1.setDaemon(True)
        thread1.start()
        threads.append(thread1)


    # while not urls_queue.empty():
    #     while not html_queue.empty():
    #         while not item_queue.empty():
    #             pass
    while True:
        time.sleep(0.5)
        if urls_queue.empty() and html_queue.empty() and item_queue.empty():
            break

    print('完成！')
    for t in threads:
        t.stop()
    for t in threads:
        t.join()
    print('end')
    print('耗时：%f s'%(time.time()-starttime))
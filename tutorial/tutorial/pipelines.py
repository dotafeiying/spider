# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class TutorialPipeline(object):
    def process_item(self, item, spider):
        return item

#将数据存储到mysql数据库
from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors
from scrapy import log

class MySQLStorePipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    #数据库参数
    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode= True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)


    # #数据库参数
    # def __init__(self):
    #     dbargs = dict(
    #          host = '10.39.211.198',
    #          db = 'test',
    #          user = 'root',
    #          passwd = 'password',
    #          cursorclass = MySQLdb.cursors.DictCursor,
    #          charset = 'utf8',
    #          use_unicode = True
    #         )
    #     self.dbpool = adbapi.ConnectionPool('MySQLdb',**dbargs)

    '''
    The default pipeline invoke function
    '''
    def process_item(self, item,spider):
        res = self.dbpool.runInteraction(self.insert_into_table,item)
        res.addErrback(self.handle_error)
        return item
    #插入的表，此表需要事先建好
    def insert_into_table(self,conn,item):
            conn.execute('insert into chembridge(catalog, amount, price,qty) values(%s,%s,%s,%s)', (
                item['catalog'],
                item['amount'],
                 # item['star'][0],
                 item['price'],
                 item['qty']
                ))
    def handle_error(self,e):
        log.err(e)
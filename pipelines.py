# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import mysql.connector as conn
import jtnews.config as config


class JtnewsPipeline(object):
    def process_item(self, item, spider):
        connection = self.get_connection()
        cursor = connection.cursor(buffered=True)
        if spider.name == 'reviewer':
            self.save_reviewer(item, cursor)
        elif spider.name == 'review':
            self.save_review(item, cursor)
        connection.commit()
        cursor.execute('SELECT * FROM reviewer')
        cursor.close()
        connection.close()
        return item

    def get_connection(self):
        DATABASE = config.DATABASES['default']
        connect = {
            'user': DATABASE['USER'],
            'password': DATABASE['PASSWORD'],
            'host': DATABASE['HOST'],
            'database': DATABASE['NAME'],
        }
        return conn.connect(**connect)

    def save_reviewer(self, item, cursor):
        sql = 'INSERT INTO reviewer (id, name, gender, age, review_count, last_reviewed_on)' \
              'VALUES (%s, %s, %s, %s, %s, %s)'
        data = tuple(item.values())
        cursor.execute(sql, data)

    def save_review(self, item, cursor):
        # @TODO 本番ではname - reviewer_nameに外部キー制約をはる
        sql = 'INSERT INTO review (reviewer_name, title, point, body, reviewed_on)' \
              'VALUES (%s, %s, %s, %s, %s)'
        data = tuple(item.values())
        cursor.execute(sql, data)

#!/usr/bin/python
import feedparser
import sys
from dateutil import parser
import ConfigParser
import psycopg2
import socket

config = ConfigParser.RawConfigParser()
config.read('reader.cfg')

feedparser._HTMLSanitizer.acceptable_elements.add("object")
feedparser._HTMLSanitizer.acceptable_elements.add("embed")
feedparser._HTMLSanitizer.acceptable_elements.add("iframe")

socket.setdefaulttimeout(30)

conn = psycopg2.connect(host=config.get('Database', 'host'),
                        user=config.get('Database', 'username'),
                        password=config.get('Database', 'password'),
                        dbname="reader")
cur = conn.cursor()

feeds_query = '''
                SELECT * FROM feeds where active_flag=TRUE order by id;
                '''

cur.execute(feeds_query)

for row in cur.fetchall():
    print 'Reading ID:' + str(row[0]), '(' + row[2].encode('ascii', 'ignore') + ')'
    #todo: feedparse timeout/retry?
    print 'start fp'
    fp = feedparser.parse(row[2])
    print 'end fp'
    #print fp
    c = 0

    if len(fp['entries']) == 0:
        #todo: if 404, mark feed as invalid.
        print 'NO ARTICLES'
        continue
    for entry in fp['entries']:
        #todo: populate: rating_enum, rating_int
        #todo: default: add_date,update_date,
        try:
            cur.execute(
                'insert into test_insert_articles (feed_id, link, title, content, viewed_flag, read_later_flag, publish_date) VALUES (%s, %s, %s, %s, %s,%s,%s)',
                (row[0], entry['link'], entry['title'], entry['content'][0]['value'], 'FALSE', 'FALSE', parser.parse(entry['updated'])))
            # use fp['entries'][0]['content'][0]['value'] instead of summary for full text
        except KeyError as e:
            e = y = str(e).replace("'", "")
            try:
                if e == 'link':
                    # print "No Link Element"
                    cur.execute(
                        'insert into test_insert_articles (feed_id, link, title, content, viewed_flag, read_later_flag, publish_date) VALUES (%s,%s,%s,%s,%s,%s,%s)',
                        (row[0], '', entry['title'], entry['content'][0]['value'], 'FALSE', 'FALSE', parser.parse(entry['updated'])))
                elif e == 'updated':
                    # print 'No Updated Element'
                    cur.execute(
                        'insert into test_insert_articles (feed_id, link, title, content, viewed_flag, read_later_flag) VALUES (%s,%s,%s,%s,%s,%s,%s)',
                        (row[0], entry['link'], entry['title'], entry['content'][0]['value'], 'FALSE', 'FALSE'))
                elif e == 'content':  # if content is broken, attempt to insert summary
                    # print 'No Content Element'
                    try:
                        cur.execute(
                            'insert into test_insert_articles (feed_id, link, title, content, viewed_flag, read_later_flag, publish_date) VALUES (%s, %s, %s, %s, %s,%s,%s)',
                            (row[0], entry['link'], entry['title'], entry['summary'], 'FALSE', 'FALSE', parser.parse(entry['updated'])))
                    except KeyError as e2:
                        if str(e2).replace("'", "") == 'summary':
                            print 'No content or summary entries. Inserting NULL.'
                            cur.execute(
                                'insert into test_insert_articles (feed_id, link, title, content, viewed_flag, read_later_flag, publish_date) VALUES (%s, %s, %s, %s, %s,%s,%s)',
                                (row[0], entry['link'], entry['title'], '', 'FALSE', 'FALSE', parser.parse(entry['updated'])))
                elif e == 'title':
                    # print "No title element. Inserting link instead"
                    cur.execute(
                        'insert into test_insert_articles (feed_id, link, title, content, viewed_flag, read_later_flag, publish_date) VALUES (%s, %s, %s, %s, %s,%s,%s)',
                        (row[0], entry['link'], entry['link'], entry['content'][0]['value'], 'FALSE', 'FALSE', parser.parse(entry['updated'])))
                else:
                    print '!!Key Error!!: ', e, entry
            except psycopg2.IntegrityError as e:
                #print 'Article Already Exists', e
                pass
            except:
                print "Unexpected error", sys.exc_info()[0]

        # need to add this to each error section? use functions
        except ValueError as e:
            # most value errors seem to be bad date formats. try removing date
            try:
                cur.execute('insert into test_insert_articles (feed_id, link, title, content, viewed_flag, read_later_flag) VALUES (%s, %s, %s, %s)',
                            (row[0], entry['link'], entry['title'], entry["summary"], 'FALSE', 'FALSE'))
            except ValueError as e:
                print 'Value Error', e, entry
        except psycopg2.IntegrityError as e:
            #print 'Article Already Exists', e
            pass
        except:
            print "Unexpected error", sys.exc_info()[0]
        # todo: get inserted rows from cursor instead of counting loops
        c += 1
        cur.execute('commit')
    print "Read " + str(c) + 'rows.'


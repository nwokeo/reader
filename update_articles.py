#!/usr/bin/python
import feedparser
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
conn.set_session(autocommit=True)
cur = conn.cursor()

feeds_query = 'SELECT * FROM feeds WHERE active_flag=TRUE ORDER BY id DESC;'

cur.execute(feeds_query)

for row in cur.fetchall():
    feed_id = row[0]
    feed_url = row[2]
    fp = feedparser.parse(feed_url)

    # deactivate feeds with invalid xml
    if len(fp['entries']) == 0:
        statement = 'UPDATE feeds SET active_flag = FALSE, update_date = CURRENT_TIMESTAMP WHERE id = {0}'.format(
            str(feed_id))
        cur.execute(statement)
        continue

    for entry in fp['entries']:
        # todo: populate: rating_enum, rating_int
        try:
            cur.execute(
                'insert into articles (feed_id, link, title, content, viewed_flag, read_later_flag, publish_date) VALUES (%s, %s, %s, %s, %s,%s,%s)',
                (feed_id,
                 entry.get('link', ''),
                 entry.get('title', entry.get('link', '')),
                 entry.get('content', [{}])[0].get('value', entry.get('summary', '')),
                 'FALSE',
                 'FALSE',
                 parser.parse(entry.get('updated', ''))))
            print('ID:' + str(feed_id), cur.statusmessage)
        except psycopg2.Error as e:
            if e.pgcode == '23505':
                pass
            else:
                print('DB error ', e.pgcode, e.pgerror)
            pass
        except ValueError as e:
            print 'Value Error', e, entry
        except psycopg2.IntegrityError as e:
            pass

cur.close()
conn.close()

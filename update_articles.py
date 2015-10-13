#!/usr/bin/python
import feedparser
from dateutil import parser
import ConfigParser
import psycopg2
import socket

feedparser._HTMLSanitizer.acceptable_elements.add("object")
feedparser._HTMLSanitizer.acceptable_elements.add("embed")
feedparser._HTMLSanitizer.acceptable_elements.add("iframe")


def update_feeds():
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
            except psycopg2.Error as e:
                if e.pgcode == '23505':  # UNIQUE VIOLATION
                    pass
                else:
                    print('ID:' + str(feed_id), cur.statusmessage, '\n', 'DB error ', e.pgcode, e.pgerror)
                pass
            except ValueError as e:
                print('ID:' + str(feed_id), cur.statusmessage, '\n', 'Value Error', e, entry)
            except psycopg2.IntegrityError as e:
                pass


def update_stats():
    update_counts = '''
            update feeds
            SET
              unread_count = counts.unread_count
            from
              (
                SELECT
                  f.id,
                  count(*) AS unread_count
              FROM articles a
              JOIN feeds f
              ON a.feed_id = f.id
              WHERE a.viewed_flag is FALSE
                and f.active_flag is TRUE
              GROUP BY
              f.id
              ) counts
            where feeds.id = counts.id ;
            '''
    try:
        print('updating stats...')
        cur.execute(update_counts)
        print(cur.statusmessage)
    except psycopg2.Error as e:
        print(e)


if __name__ == "__main__":
    config = ConfigParser.RawConfigParser()
    config.read('reader.cfg')

    socket.setdefaulttimeout(30)

    conn = psycopg2.connect(host=config.get('Database', 'host'),
                            user=config.get('Database', 'username'),
                            password=config.get('Database', 'password'),
                            dbname="reader")
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    update_feeds()
    update_stats()

    cur.close()
    conn.close()

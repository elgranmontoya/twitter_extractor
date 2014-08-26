# -*- coding: utf-8 -*-
__author__ = 'artemkorhov'

import urllib
import urllib2
import re
import logging
import csv
import StringIO
import gzip
import json


# Patterns
pattern_twid = 'data-item-id="[0-9]+?"'
pattern_uid = 'data-user-id="[0-9]+?"'

# Initial options
twitter = 'https://twitter.com/search?q='
inititial_request = 'since:2013-08-15 until:2013-09-09 Навальный OR Собянин OR выборы OR мэр'

rec = urllib.quote(inititial_request)
url = twitter + rec

# Twitter AJAX URLs
ajax_page = 'https://twitter.com/i/timeline?include_available_features=1&include_entities=1&last_note_ts=0&max_id='  # % id
ajax_post_id = 'https://twitter.com/i/expanded/batch/'  # 'smth %s' % id
ajax_post_other = '?facepile_max=7&include%5B%5D=social_proof&include%5B%5D=ancestors&include%5B%5D=descendants&page_context=home&section_context=home'



pfd = 'https://twitter.com/i/search/timeline?q=since%3A2013-08-15%20until%3A2013-09-09%20%D0%9D%D0%B0%D0%B2%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9%20OR%20%D0%A1%D0%BE%D0%B1%D1%8F%D0%BD%D0%B8%D0%BD%20OR%20%D0%B2%D1%8B%D0%B1%D0%BE%D1%80%D1%8B%20OR%20%D0%BC%D1%8D%D1%80&src=savs&include_available_features=1&include_entities=1&last_note_ts=238&scroll_cursor=TWEET-376847233838497792-376855000489553920'

def get_raw_html(url):
    """
    Retrieving raw html data.
    Requires urllib2 package
    """
    try:
        handler = urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        # log
        return None

    if handler.code != 200:
        return None

    if handler is not None:
        html = handler.read()
        encoded_html = unicode(html, errors='ignore')
        return encoded_html

def perform_request(url, ajax=None):
    if ajax is not None:
        path = url[19:]
        headers = {
            'host': 'twitter.com',
            'method': 'GET',
            'path': path,
            'scheme': 'https',
            'version': 'HTTP/1.1',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-encoding': 'gzip,deflate,sdch',
            'accept-language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
            'cookie': 'guest_id=v1%3A139350866241665925; twid="u=939819955"; remember_checked_on=1; auth_token=c6c6733b8b07fca032c6ab7a7ce7e2ffcb239cb3; lang=ru; original_referer=padhuUp37zi4XoWogyFqcGgJdw+JPXpx; eu_cn=1; webn=939819955; __utma=43838368.1632479807.1393511412.1399588643.1399618362.246; __utmc=43838368; __utmz=43838368.1399199861.239.19.utmcsr=kinopoisk.ru|utmccn=(referral)|utmcmd=referral|utmcct=/name/607902/; __utmv=43838368.lang%3A%20ru; _twitter_sess=BAh7CzoMY3NyZl9pZCIlMjA4YzZjM2IxNDgxZGI0MDRiNTA2N2VkNTgzYjdh%250ANWI6CXVzZXJpBLODBDg6B2lkIiVhMjQ5MGNiN2E4ZGVmMjMzNWE0NDE0MGEw%250AMmJhYzU0MjoaY29udGFjdF9yZWZyZXNoX2NvdW50aQA6D2NyZWF0ZWRfYXRs%250AKwhIr8BzRAEiCmZsYXNoSUM6J0FjdGlvbkNvbnRyb2xsZXI6OkZsYXNoOjpG%250AbGFzaEhhc2h7AAY6CkB1c2VkewA%253D--bd6b8d757f3b7b21b46f2cf40ad1aa02f19053d4',
            'referer': 'https://twitter.com/',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }
    else:
        headers = {
            'host': 'twitter.com',
            'method': 'GET',
            'path': '/',
            'scheme': 'https',
            'version': 'HTTP/1.1',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-encoding': 'gzip,deflate,sdch',
            'accept-language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
            'cookie': 'guest_id=v1%3A139350866241665925; twid="u=939819955"; remember_checked_on=1; auth_token=c6c6733b8b07fca032c6ab7a7ce7e2ffcb239cb3; lang=ru; original_referer=padhuUp37zi4XoWogyFqcGgJdw+JPXpx; eu_cn=1; webn=939819955; __utma=43838368.1632479807.1393511412.1399588643.1399618362.246; __utmc=43838368; __utmz=43838368.1399199861.239.19.utmcsr=kinopoisk.ru|utmccn=(referral)|utmcmd=referral|utmcct=/name/607902/; __utmv=43838368.lang%3A%20ru; _twitter_sess=BAh7CzoMY3NyZl9pZCIlMjA4YzZjM2IxNDgxZGI0MDRiNTA2N2VkNTgzYjdh%250ANWI6CXVzZXJpBLODBDg6B2lkIiVhMjQ5MGNiN2E4ZGVmMjMzNWE0NDE0MGEw%250AMmJhYzU0MjoaY29udGFjdF9yZWZyZXNoX2NvdW50aQA6D2NyZWF0ZWRfYXRs%250AKwhIr8BzRAEiCmZsYXNoSUM6J0FjdGlvbkNvbnRyb2xsZXI6OkZsYXNoOjpG%250AbGFzaEhhc2h7AAY6CkB1c2VkewA%253D--bd6b8d757f3b7b21b46f2cf40ad1aa02f19053d4',
            'referer': 'https://twitter.com/',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }
    rec = urllib2.Request(url, headers=headers, origin_req_host='twitter.com')

    try:
        handler = urllib2.urlopen(rec)
        if handler.info().get('Content-Encoding') == 'gzip':
            buf = StringIO.StringIO(handler.read())
            gzip_f = gzip.GzipFile(fileobj=buf)
            content = gzip_f.read()
        else:
            content = handler.read()
    except urllib2.HTTPError, e:
        # log
        return None, None
    return handler, content

def get_ids(pattern, raw_html):
    """
    Retrieving tweet ids from raw html part.
    Returns array of ids
    """
    raw_list = re.findall(pattern, raw_html)  # Returns strings, that contain id's
    filtered_list = [int(el[14:-1]) for el in raw_list]

    return filtered_list

def parse_block(url, pattern_twid, pattern_uid):
    """
    Parse particular HTML block
    1) Perform url request
    2) retrieves html
    3) retrieves twids
    3) retrieves uids

    Returns:
    : Tuple  [twids], [uids]
    """
    html = get_raw_html(url)
    if html is not None:
        twids = get_ids(pattern_twid, html)
        uids = get_ids(pattern_uid, html)
        return twids, uids

    return None, None

def recursive_fill_list_of_ids(tw, tw_pattern, u_pattern):
    global rec
    global twit_ids
    global user_ids
    in_uri = 'https://twitter.com/i/search/timeline?q='
    q = rec
    rest = '&src=savs&include_available_features=1&include_entities=1&last_note_ts=238&scroll_cursor=TWEET-%s-%s' % (tw[-1], tw[0])
    url = in_uri + q + rest

    handler, content = perform_request(url, ajax=1)
    print '-------'
    print 'LOG: URL::: %s' % url
    print 'LOG: CODE::: %s' % handler.code
    if handler is not None and handler.code == 200:
        js_content = json.loads(content)
        cont = js_content.get('inner').get('items_html')
        twits = get_ids(tw_pattern, cont)
        users = get_ids(u_pattern, cont)
        print len(twits), len(users)
        twit_ids.extend(twits)
        user_ids.extend(users)
        print 'LOG: LENGTHS::: TW= %s,  U= %s' % (len(twit_ids), len(user_ids))
        if len(twit_ids) > 11000:
            return twit_ids, user_ids
        else:
            recursive_fill_list_of_ids(twits, tw_pattern, u_pattern)
    else:
        return twit_ids, user_ids

    return twit_ids, user_ids


if __name__ == '__main__':
    twit_ids = []
    user_ids = []
    source, content = perform_request(url)
    init_uids = get_ids(pattern_uid, content)
    init_twids = get_ids(pattern_twid, content)

    twit_ids.extend(init_twids)
    user_ids.extend(init_uids)
    print len(twit_ids)
    print 'START RECURSION'
    # Recursive step
    try:
        (rec_twids, rec_uids) = recursive_fill_list_of_ids(twit_ids, pattern_twid, pattern_uid)
    except Exception, e:
        print e

    print 'LENGTH OF TW = %s LENGTH OF UI = %s' % (len(rec_twids), len(rec_uids))
    print 'STARTING WRITE'

    with open('twitter_long.csv', 'w') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['twit_ids', 'user_ids'])
        for i in range(0, len(rec_twids)):
            data = [rec_twids[i], rec_uids[i]]
            writer.writerow(data)

    f.close()
    print 'FINISHED'
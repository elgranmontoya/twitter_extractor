__author__ = 'artemkorhov'
from birdy.twitter import UserClient
import csv
import json
from collections import deque

consumer_key = 'cqPq4cD2V4BiMeHIn0H4ZAArj'
consumer_secret = 'bHH14mWh7oAGzOX9RWRpe9j5nrXMROPzbHW3GnGyj6kXGOXVxk'
access_token_key = '939819955-HNlyWZbEwXq5GeTR0ZsgaxcDQ2fA8xsABahPVH0d'
access_token_secret = 'Pb33YWDCDISlq9tZo80qvyh8IjuK9Ebtk3290pYXDf7GR'

client = UserClient(consumer_key, consumer_secret, access_token_key, access_token_secret)

# Get tweet ids
with open('tweets.csv', 'rU') as f:
    reader = csv.reader(f)
    tweet_ids = []
    for row in reader:
        tweet_ids.extend(row)

    f.close()
print len(tweet_ids)

# tweet_ids - queue
queue = deque(tweet_ids)
for i in range(0, 15):
    tweet_id = queue.popleft()
    response = client.api.statuses.retweeters.ids.get(id=str(tweet_id))
    retweets = response.data.get('ids', [])
    obj = {tweet_id: retweets}
    obj = json.dumps(obj)

    with open('retweeters.json', 'a') as f:
        f.write(obj)
    f.close()

    with open('twits.csv', 'w') as f:
        writer = csv.writer(f)
        for m in queue:
            writer.writerow([m])

    f.close()

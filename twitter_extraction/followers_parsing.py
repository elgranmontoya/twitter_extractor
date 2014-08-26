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
with open('uids.csv', 'rU') as f:
    reader = csv.reader(f)
    user_ids = []
    for row in reader:
        user_ids.extend(row)

    f.close()
print len(user_ids)

# tweet_ids - queue
queue = deque(user_ids)
for i in range(0, 1):
    user_id = queue.popleft()
    response = client.api.followers.ids.get(id=str(user_id), count=5000)
    followers = response.data.get('ids', [])
    obj = {user_id: followers}
    obj = json.dumps(obj)

    with open('followers.json', 'a') as f:
        f.write(obj)
    f.close()

    with open('users.csv', 'w') as f:
        writer = csv.writer(f)
        # writer.writerow('rest ids')
        for m in queue:
            writer.writerow([m])

    f.close()

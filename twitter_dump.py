import argparse
import datetime
from dateutil import parser
import json
from pyquery import PyQuery
import sys
import re
import requests
import time
import urllib

def tweetPaser(tweets_html):
  tweetslist = []
  if tweets_html.strip() != '':
    scraped_tweets = PyQuery(tweets_html)
    scraped_tweets.remove('div.withheld-tweet')
    tweets = scraped_tweets('div.js-stream-tweet')
    if len(tweets) != 0:
      for tweet_html in tweets:
        t = {}
        tweetPQ = PyQuery(tweet_html)
        t['user'] = tweetPQ("span:first.username.u-dir b").text()
        txt = re.sub(r"\s+", " ", tweetPQ("p.js-tweet-text").text())
        txt = txt.replace('# ', '#')
        txt = txt.replace('@ ', '@')
        t['tweet'] = txt
        t['id'] = tweetPQ.attr("data-tweet-id")
        t['retweets'] = int(tweetPQ("span.ProfileTweet-action--retweet span.ProfileTweet-actionCount").attr("data-tweet-stat-count").replace(",", ""))
        t['favorites'] = int(tweetPQ("span.ProfileTweet-action--favorite span.ProfileTweet-actionCount").attr("data-tweet-stat-count").replace(",", ""))
        t['link'] = 'https://twitter.com' + tweetPQ.attr("data-permalink-path")
        t['mentions'] = re.compile('(@\\w*)').findall(t['tweet'])
        t['hashtags'] = re.compile('(#\\w*)').findall(t['tweet'])
        t['timestamp'] = int(tweetPQ("small.time span.js-short-timestamp").attr("data-time"))
        tweetslist.append(t)
  return tweetslist

def getCriteria(users, word, since, until):
  query = ''
  if word.strip() != '':
    query += word
  if len(users) == 1:
    query += ' from:' + users[0]
  elif len(users) > 1:
    query += ' from:' + ' OR from:'.join(users)
  if query == '':
    return query
  else:
    try:
      if since != None:
        since_day = parser.parse(since).strftime('%Y-%m-%d')
        query += ' since:' + since_day
      if until != None:
        until_day = parser.parse(until).strftime('%Y-%m-%d')
        query += ' until:' + until_day
    except ValueError:
      print('[-] Date Format Error')
  query = urllib.parse.quote_plus(query)
  return query

def getTweet(query, min_pos, max_count, tweets):
  url = 'https://twitter.com/i/search/timeline?f=tweets&q={query}&src=typd&max_position={min_pos}'.format(query=query, min_pos=min_pos)
  headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0',
    'Accept':"application/json, text/javascript, */*; q=0.01",
    'Accept-Language':"de,en-US;q=0.7,en;q=0.3",
    'X-Requested-With':"XMLHttpRequest",
    'Referer':url,
    'Connection':"keep-alive"
  }
  response = requests.get(url, headers=headers)
  statuscode = response.status_code
  json_response = response.json()
  if statuscode == 200:
    new_pos = None
    if 'min_position' in json_response:
      new_pos = json_response["min_position"]
    tweets += tweetPaser(json_response['items_html'])
    if new_pos == min_pos or len(tweets) > max_count:
      return tweets, statuscode
    else:
      proc = int((len(tweets) / max_count) * 100)
      print('[+] ' + str(proc) + '% Processing...')
      time.sleep(0.5)
      return getTweet(query, new_pos, max_count, tweets)
  else:
    print('[-] Something Wrong...\nStatus: ' + str(statuscode))
    return tweets, statuscode

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--query', type=str, default='', help='Twitter Query')
  parser.add_argument('--users', type=str, nargs='*', help='Twitter Users')
  parser.add_argument('--since', type=str, help='Search since that date')
  parser.add_argument('--until', type=str, help='Search until that date')
  parser.add_argument('--dump', action='store_true', help='Dump to File')
  parser.add_argument('-q', action='store_true', help='Do not show results')
  parser.add_argument('--max-count', type=int, default=1000, help='The number of Tweets')
  args = parser.parse_args()

  users = ''
  word = args.query
  if args.users != None:
    users = args.users
  since = args.since
  until = args.until
  query = getCriteria(users, word, since, until)
  max_count = args.max_count
  if query == '':
    print('[-] Query is Empty. Exit.')
    sys.exit(1)
  print('[+] Your Query is: ' + query)
  print('[+] Please Check Result in the following URL.')
  print('[+] https://twitter.com/search?f=tweets&vertical=news&q={q}&src=typd&'.format(q=query))
  print('[+] Gathering Tweets. Please Wait...')
  (tweets, statuscode) = getTweet(query, 'min_pos', max_count, [])
  print('[+] Get {num} Tweets '.format(num=str(len(tweets))))
  if args.dump:
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = 'tweets-' + timestamp + '.json'
    with open(filename, 'w') as f:
      json.dump(tweets, f, indent=4)
    print('[+] Tweets ware saved in ' + filename)
  if not args.q:
    print('[+] Print Twitter Search Result')
    for t in tweets:
      print('------')
      print('user: ' + t['user'])
      print('tweet: ' + t['tweet'])
      print('id: ' + t['id'])
      print('link: ' + t['link'])
      print('RT: ' + str(t['retweets']))
      print('fav: ' + str(t['favorites']))
      print('mentions: ' + ', '.join(t['mentions']))
      print('hashtags: ' + ', '.join(t['hashtags']))
      print(datetime.datetime.fromtimestamp(t['timestamp']))

if __name__ == "__main__":
  main()

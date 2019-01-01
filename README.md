# twitter-dump

## Description
Dump Tweets in JSON format without Twitter API.

## Requirements
Python 3 and the following libraries
 - requests
 - python-dateutil
 - pyquery

## Usage
- Get tweets from User 'piedpiper1616'
```sh
python3 twitter_dump.py --users piedpiper1616 --dump --max-count 300
```

- Get tweets by query 'test'
```sh
python3 twitter_dump.py --query 'test' --dump --max-count 300
```

Use '--dump' option to save file as JSON format.
Use '-q' option not to show results.
Use '--max-count' option not to show results.

## Author
[blueblue](https://twitter.com/piedpiper1616)

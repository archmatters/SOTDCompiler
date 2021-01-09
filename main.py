#!/usr/bin/env python3

import datetime

import praw

import scanner

# default to last month
sotd_month = datetime.date.today().month - 1
sotd_year = datetime.date.today().year
if sotd_month < 1:
    sotd_month = 12
    sotd_year -= 1

# credentials & agent read from praw.ini
reddit = praw.Reddit(site_name = 'SOTDScanner')

wssub = reddit.subreddit('Wetshaving')

subs00 = wssub.new( limit = None )

with open(file = 'sotd-{:0>4}-{:0>2}.csv'.format(sotd_year, sotd_month),
        mode = 'w', encoding = 'utf8') as dataFile:
    post_count = 0
    for post in subs00:
        post_count += 1
        post_date = scanner.getSOTDDate(post)
        if not post_date:
            continue

        if post_date.year < sotd_year or (post_date.month < sotd_month and post_date.year == sotd_year):
            print('Complete.')
            break

        if post_date.month != sotd_month or post_date.year != sotd_year:
            print(f'Skipping thread {post.title}; wrong month.')
            continue

        comment_count = 0
        for tlc in scanner.getThreadComments(post, post_date):
            comment_count += 1
            scanner.scanComment(tlc, post_date, dataFile)
        
        print(f"Processed {comment_count} comments in {post.title}.")

    print(f"Processed {post_count} posts.")


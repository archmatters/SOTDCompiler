#!/usr/bin/env python3

import argparse
from datetime import date
from enum import Enum

import praw

import scanner

class Mode(Enum):
    INCREMENTAL = 0
    COMPILE = 1

aparser = argparse.ArgumentParser(description='Load SOTD data from r/Wetshaving')
aparser.add_argument('command', choices=['compile', 'comp', 'incremental', 'inc'],
        help='Specify the command; a monthly compilation or incremental update.')
aparser.add_argument('--month', metavar='{mm|yyyy-mm}',
        help='Specify the month (current year) or month and year.\n'
        'The default is to compile data for the previous month, or perform\n'
        'an incremental update for the current month.')
args = aparser.parse_args()

if args.command in [ 'comp', 'compile' ]:
    arg_mode = Mode.COMPILE
elif args.command in [ 'inc', 'incremental' ]:
    arg_mode = Mode.INCREMENTAL
else:
    raise SystemExit(f"Invalid command \"{args['command']}\" specified.")

sotd_month = date.today().month
sotd_year = date.today().year
if arg_mode == Mode.COMPILE:
    # default to last month
    sotd_month -= 1
    if sotd_month < 1:
        sotd_month = 12
        sotd_year -= 1

if args.month:
    if len(args.month) > 5 and len(args.month) < 8:
        # year-month
        sotd_year = int(args.month[0:4])
        sotd_month = int(args.month[5:])
    elif len(args.month) < 3:
        sotd_month = int(args.month)
    else:
        raise SystemExit(f"{aparser.prog}: error: '{args.month}' is not a valid month or year-month.")
    if sotd_month < 1 or sotd_month > 12:
        raise SystemExit(f"{aparser.prog}: error: '{args.month}' is not a valid month or year-month.")
    if sotd_year < 2018:
        raise SystemExit(f"{aparser.prog}: error: '{args.month}' is too far in the past.")
    if sotd_year > date.today().year or (sotd_year == date.today().year
            and sotd_month > date.today().month):
        raise SystemExit(f"{aparser.prog}: error: '{args.month}' is in the future!")


def postLoop():
    post_count = 0
    post_proc_count = 0
    for post in subs00:
        post_count += 1
        post_date = scanner.getSOTDDate(post)
        if not post_date:
            continue
        if (post_date.month < sotd_month and post_date.year == sotd_year) or post_date.year < sotd_year:
            print('Complete.')
            break
        if post_date.month != sotd_month or post_date.year != sotd_year:
            print(f'Skipping thread {post.title}; wrong month.')
            continue
        if arg_mode == Mode.INCREMENTAL and (date.today() <= post_date):
            print(f'Skipping thread {post.title}; same day may not be complete.')
            continue

        post_proc_count += 1
        if arg_mode == Mode.INCREMENTAL:
            # getThreadComments() saves data
            scanner.getThreadComments(post, post_date, True)
        elif arg_mode == Mode.COMPILE:
            comment_count = 0
            for cmt in scanner.getThreadComments(post, post_date):
                comment_count += 1
                scanner.scanComment(cmt, post_date, dataFile)
            print(f"Processed {comment_count} comments in {post.title}.")

    print(f"Saw {post_count} posts, processed {post_proc_count}.")


# credentials & agent read from praw.ini
reddit = praw.Reddit(site_name = 'SOTDScanner')
wssub = reddit.subreddit('Wetshaving')
subs00 = wssub.new( limit = None )

if arg_mode == Mode.COMPILE:
    with open(file = 'sotd-{:0>4}-{:0>2}.csv'.format(sotd_year, sotd_month),
            mode = 'w', encoding = 'utf8') as dataFile:
        postLoop()
elif arg_mode == Mode.INCREMENTAL:
    postLoop()

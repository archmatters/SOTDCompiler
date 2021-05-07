#!/usr/bin/env python3

import argparse
import json
from datetime import date, timedelta, datetime
from enum import Enum
from pathlib import Path

import praw

import scanner

class Mode(Enum):
    INCREMENTAL = 0
    COMPILE = 1

aparser = argparse.ArgumentParser(description='Load SOTD data from r/Wetshaving')
aparser.add_argument('command', choices=['compile', 'comp', 'incremental', 'inc'],
        help='Specify the command; a monthly compilation or incremental update.')
aparser.add_argument('--delimiter', choices=[',', 'comma', '\\t', 'tab'],
        help='Specify the CSV delimiter for compilation only.')
aparser.add_argument('--month', metavar='{mm|yyyy-mm}',
        help='Specify the month (current year) or month and year.\n'
        'The default is to compile data for the previous month, or perform\n'
        'an incremental update for the current month.')
args = aparser.parse_args()

if args.command in [ 'comp', 'compile' ]:
    arg_mode = Mode.COMPILE
    if args.delimiter in [ ',', 'c', 'comma' ]:
        arg_delimiter = ','
    elif args.delimiter in [ '\t', '\\t', 't', 'tab' ]:
        arg_delimiter = '\t'
    else:
        raise SystemExit(f"Missing or invalid delimiter: select tab or comma with --delimiter.")
elif args.command in [ 'inc', 'incremental' ]:
    arg_mode = Mode.INCREMENTAL
else:
    raise SystemExit(f"Invalid command \"{args['command']}\" specified.")

# default to last month
sotd_month = date.today().month - 1
sotd_year = date.today().year
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


def get_cached_comments( post_id: str, post_date: date ):
    """ If the given post ID with the given date is found in the cache, the
        list of comments is returned.  Otherwise None is returned.
    """
    # note the filename generation MUST match save_comments_to_cache()!
    filename = f"postdata/{post_date.strftime('%Y-%m-%d')}-{post_id}.json"
    if Path(filename).exists():
        with open(file = filename, mode = 'r', encoding = 'utf8') as comments_file:
            try:
                jscoms = json.load(comments_file).get('comments')
            except Exception as e:
                print(f"Error loading cache file {filename}: {e}")
                return None
            rdcoms = [ ]
            for cmt in jscoms:
                if not cmt['author']:
                    cmt['author'] = '[deleted]'
                rdcoms.append(praw.reddit.models.Comment(reddit='Reddit', _data=cmt))
            return rdcoms
    return None


def save_comments_to_cache( post_id: str, post_date: date, comments ):
    """ Saves the given collection of comments to the file cache.  This will
        overwrite any existing cache for the post.
    """
    # note the filename generation MUST match get_cached_comments()!
    filename = f"postdata/{post_date.strftime('%Y-%m-%d')}-{post_id}.json"
    Path('postdata').mkdir(exist_ok = True)
    with open(file = filename, mode = 'w', encoding = 'utf8') as comment_file:
        comment_count = 0
        comment_file.write('{"comments": [\n')
        for tlc in comments:
            comment_count += 1
            author_name = None
            if tlc.author:
                author_name = tlc.author.name
            # apparently created_utc is actually created CST?
            # at least for me it is, and for other posts the conversion is
            # the same from web -> created_utc
            # edited appears to work the same despite not being named _utc
            map = {
                'author': author_name,
                'id': tlc.id,
                'body': tlc.body,
                'body_html': tlc.body_html,
                'created_utc': tlc.created_utc,
                'edited': tlc.edited,
                'link_id': tlc.link_id,
                'parent_id': tlc.parent_id,
                'permalink': tlc.permalink,
                'saved': tlc.saved,
                'score': tlc.score,
                'subreddit_id': tlc.subreddit_id
            }
            if tlc.edited:
                map['edited'] = tlc.edited
            if comment_count > 1:
                comment_file.write(',\n')
            comment_file.write(json.dumps(map))
        comment_file.write('\n]}')


def ensure_loaded( post: praw.models.Submission ):
    """ Returns a list of all top-level comments in the given submission.
        Reddit does not guarantee all top-level comments are loaded; this
        function will.
    """
    complete = False
    while not complete:
        complete = True
        for tlc in post.comments:
            if isinstance(tlc, praw.models.MoreComments):
                complete = False
                post.comments.replace_more(limit=None)
                break


def update_cache_comments( cached: list, reddit_comments ):
    """ Adds any missing comments to the cached list, from the Reddit comments
        collection.  Returns True if the list was added to, or False if not.
    """
    updated = False
    for comment in reddit_comments:
        found = False
        for cc in cached:
            if cc.id == comment.id:
                found = True
                break
        if not found:
            cached.append(comment)
            updated = True
    return updated

# if incremental: loop over posts until you go back one week, or two days prior to last known
# TODO see if new comments have been posted
# if compile: visit all posts in one month
def do_the_work( subreddit: praw.models.Subreddit, mode: Mode ):
    post_count = 0
    post_proc_count = 0
    inc_limit = date.today() - timedelta(days=7)
    last_inc_loaded = None
    for post in subreddit.hot(limit=None):
        post_count += 1
        post_date = scanner.get_sotd_date(post)
        if not post_date:
            continue
        if mode == Mode.INCREMENTAL:
            if post_date >= date.today():
                print(f'Skipping thread {post.title}; too recent and it may not be complete.')
                continue
            #elif post_date >= inc_limit:
                # TODO merge
            elif post_date <= inc_limit and (not last_inc_loaded or (last_inc_loaded
                        and post_date < last_inc_loaded - timedelta(days=7))):
                print('Looks like we\'re finished loading.')
                break
            else:
                comments = get_cached_comments(post.id, post_date)
                if comments:
                    ensure_loaded(post)
                    if update_cache_comments(comments, post.comments):
                        print(f"Found new/updated comments in {post.title}.")
                        last_inc_loaded = post_date
                        save_comments_to_cache(post.id, post_date, comments)
                    else:
                        print(f"Loaded cache for {post.title}.")
                else:
                    post_proc_count += 1
                    ensure_loaded(post)
                    save_comments_to_cache(post.id, post_date, post.comments)
                    last_inc_loaded = post_date
                    print(f"Saved {len(post.comments)} comments from {post.title}.")
        elif mode == Mode.COMPILE:
            if post_date.year < sotd_year or (post_date.month < sotd_month
                    and post_date.year == sotd_year):
                print('Complete.')
                break
            elif post_date.month != sotd_month or post_date.year != sotd_year:
                print(f'Skipping thread {post.title}; wrong month.')
                continue
            comment_count = 0
            comments = get_cached_comments(post.id, post_date)
            if not comments:
                ensure_loaded(post)
                comments = post.comments
                save_comments_to_cache(post.id, post_date, comments)
            post_proc_count += 1
            for cmt in comments:
                comment_count += 1
                scanner.scanComment(cmt, post_date, dataFile, arg_delimiter)
            print(f"Processed {comment_count} comments in {post.title}.")
        else:
            raise SystemExit(f"Unknown mode '{mode}'")

    print(f"Saw {post_count} posts, processed {post_proc_count}.")


# credentials & agent read from praw.ini
reddit = praw.Reddit(site_name='SOTDScanner')
wssub = reddit.subreddit('Wetshaving')

if arg_mode == Mode.COMPILE:
    with open(file='sotd-{:0>4}-{:0>2}.csv'.format(sotd_year, sotd_month),
            mode='w', encoding='utf8') as dataFile:
        do_the_work(wssub, arg_mode)
elif arg_mode == Mode.INCREMENTAL:
    do_the_work(wssub, arg_mode)

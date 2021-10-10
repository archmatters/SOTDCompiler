#!/usr/bin/env python3

import argparse
import json
import re
from datetime import date, timedelta, datetime
from enum import Enum, auto
from pathlib import Path

import praw
from prawcore.exceptions import NotFound

import scanner

class Mode(Enum):
    INCREMENTAL = auto()
    COMPILE = auto()
    ONE = auto()

aparser = argparse.ArgumentParser(description='Load SOTD data from r/Wetshaving')
aparser.add_argument('command', choices=['compile', 'comp', 'incremental', 'inc', 'one'],
        help='Specify the command; a monthly compilation, incremental update, or single post.')
aparser.add_argument('--id', help='Specify the post ID for mode "one."')
aparser.add_argument('--delimiter', choices=[',', 'comma', '\\t', 'tab'],
        help='Specify the CSV delimiter for compilation only.')
aparser.add_argument('--month', metavar='{mm|yyyy-mm}',
        help='Specify the month (current year) or month and year.\n'
        'The default is to compile data for the previous month, or perform\n'
        'an incremental update for the current month.')
aparser.add_argument('--live', action='store_true',
        help='Look for posts on Reddit, not in file cache (compilation only).')
aparser.add_argument('--date', 
        help='Specify a post date ("one" mode only).')
aparser.add_argument('--days', default=5,
        help='Specify how many days to go back (incremental mode only).')
args = aparser.parse_args()

if args.command in [ 'comp', 'compile' ]:
    arg_mode = Mode.COMPILE
    if args.delimiter in [ ',', 'c', 'comma' ]:
        arg_delimiter = ','
    elif args.delimiter in [ '\t', '\\t', 't', 'tab' ]:
        arg_delimiter = '\t'
    else:
        raise SystemExit("Missing or invalid delimiter: select tab or comma with --delimiter.")
elif args.command in [ 'inc', 'incremental' ]:
    arg_mode = Mode.INCREMENTAL
    if args.days < 1:
        raise SystemExit("Days to check must be a positive integer.")
elif args.command in [ 'one' ]:
    arg_mode = Mode.ONE
    if not args.id or not args.date:
        raise SystemExit("You must specify the post ID and date when using mode \"one\"")
    result = re.match('^(\\d{4})[\\-\\.]?(\\d{,2})[\\-\\.]?(\\d{,2})', args.date)
    if not result:
        raise SystemExit(f"Post date '{args.post_date}' not in a valid format")
    arg_date = date(int(result.group(1)), int(result.group(2)), int(result.group(3)))
    if arg_date.year < 2020 or arg_date > date.today():
        raise SystemExit(f"Post date '{args.post_date}' is not expected: too early or in the future")
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


def comp_from_file():
    # TODO duplicate detection:
    # same lather info & posts within a few minutes of each other (10?)
    # or same lather & posts to multiple threads on the same day
    file_pat = re.compile('^(\\d{4})-(\\d\\d)-(\\d\\d)-(\\w+).json$')
    post_proc_count = 0
    comment_count = 0
    for fp in Path('postdata').glob("*json"):
        result = file_pat.match(fp.name)
        if not result or sotd_year != int(result.group(1)) or sotd_month != int(result.group(2)):
            continue
        post_date = date(int(result.group(1)), int(result.group(2)), int(result.group(3)))
        comments = get_cached_comments(result.group(4), post_date)
        if not comments:
            print(f"ERROR: failed to load comments from '{fp}'")
        else:
            post_proc_count += 1
        for cmt in comments:
            comment_count += 1
            scanner.scanComment(cmt, post_date, dataFile, arg_delimiter)
    print(f"Processed {comment_count} comments in {post_proc_count} files.")



# if incremental: loop over posts until you go back one week, or two days prior to last known
# if compile: visit all posts in one month
def do_the_work( subreddit: praw.models.Subreddit, mode: Mode ):
    limit_days = args.days
    post_count = 0
    post_proc_count = 0
    inc_limit = date.today() - timedelta(days=limit_days)
    last_inc_loaded = date.today()
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
            elif abs((last_inc_loaded - post_date).days) > 3 * limit_days:
                print(f'Weird date on {post.id} "{post.title}"; skipping.')
                continue
            elif post_date <= inc_limit and (last_inc_loaded - post_date).days > 7:
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
            # TODO duplicate detection:
            # same lather info & posts within a few minutes of each other (10?)
            # or same lather & posts to multiple threads on the same day
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

if arg_mode is Mode.COMPILE:
    with open(file='sotd-{:0>4}-{:0>2}.csv'.format(sotd_year, sotd_month),
            mode='w', encoding='utf8') as dataFile:
        # TODO put this together with scanner.scanComment(...)
        headers = [ 'Date', 'Time', 'Author', 'Maker', 'Scent', 'Confidence',
                'Lather', 'ID', 'Plaintext', 'URL' ]
        if arg_delimiter == ',':
            dataFile.write('"')
        for i in range(len(headers)):
            if arg_delimiter == '\t' and i >= 8:
                continue
            if i > 0:
                if arg_delimiter == ',':
                    dataFile.write('","')
                else:
                    dataFile.write(arg_delimiter)
            dataFile.write(headers[i])
        if arg_delimiter == ',':
            dataFile.write('"')
        dataFile.write('\n')
        # end TODO
        if args.live:
            do_the_work(wssub, arg_mode)
        else:
            comp_from_file()
elif arg_mode is Mode.INCREMENTAL:
    do_the_work(wssub, arg_mode)
elif arg_mode is Mode.ONE:
    post = reddit.submission(id=args.id)
    if post:
        try:
            # copied from do_the_work
            ensure_loaded(post)
            save_comments_to_cache(post.id, arg_date, post.comments)
            print(f"Saved {len(post.comments)} comments from {post.title}.")
        except NotFound as e:
            print("The post was not found: " + str(e))
    else:
        print(f"No post found for {args.post_id}")

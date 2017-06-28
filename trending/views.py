from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader

import feedparser
import re

from .models import RSSFeed


'''Note:
   Chapter 10 of the O'Reilly book "Collective Intelligence" by
   Toby Segaran (2007) served as the inspiration for this application.
   Much of this code was borrowed from there, so it would be wrong
   not to provide credit to its true author; thanks Toby!
'''

feedlist = []

def index(request):
    '''Render default page for the Trending app.'''
    global feedlist

    feedlist = []

    context = {}

    update_feedlist(request)

    if feedlist:
        allw, artw, artt = get_article_words()
        wordmatrix, wordvec = make_matrix(allw, artw)

        context['keywords'] = wordvec[0:10]
        context['titles'] = artt[0:30]

    context['feedlist'] = feedlist

    return render(request, 'trending/trending.html', context)


def update_feedlist(request):
    '''Add urls to global var feedlist.'''
    global feedlist
    if request.user.is_authenticated():
        user = request.user
        # Get all the RSS Feed objects from db.
        rss_list = RSSFeed.objects.filter(user=user.id)
        if rss_list:
            # Store all RSS urls in var feedlist.
            for feed in rss_list:
                feedlist.append(feed.url)


def remove_feed(request):
    if request.POST:
        if request.user.is_authenticated():
            if 'removed_feed' in request.POST:
                removed_feed = request.POST['removed_feed']
                user = request.user
                try:
                    feed_inst = RSSFeed.objects.get(url=removed_feed, user=user)
                    feed_inst.delete()
                except Exception as e:
                    print '%s' % e
    return index(request)


def add_feed(request):
    if request.POST:
        if request.user.is_authenticated():
            if 'added_feed' in request.POST:
                added_feed = request.POST['added_feed']
                user = request.user
                store_feed_in_db(added_feed, user)
    return index(request)


def store_feed_in_db(added_feed, user):

    # Check if RSSFeed is already in database.
    if RSSFeed.objects.filter(url=added_feed, user=user).exists():
        # Warn user.
        print '[!] Feed already in database: %s with %s' % (added_feed, user.username)

    else:
        # RSSFeed doesn't exist in our db, so create a new one.
        rss = RSSFeed(url=added_feed, user=user)

        # Save RSSFeed to db
        try:
            rss.save()

        # Error, don't save and warn the user.
        except Exception as e:
            print '[!] %s' % e


def strip_html(h):
    '''Remove images and markup from an article.'''
    p = ''
    s = 0
    for c in h:
        if c == '<':
            s = 1
        elif c == '>':
            s = 0
            p += ' '
        elif s == 0:
            p += c
    return p


def separate_words(text):
    '''Simple alphanumeric regex to separate words in an article.'''
    splitter = re.compile('\\W*')
    return [s.lower() for s in splitter.split(text) if len(s) > 3]


def get_article_words():
    '''Iterates through articles and extracts individual words.'''
    all_words = {}
    article_words = []
    article_titles = []
    ec = 0

    # Loop over every feed.
    for feed in feedlist:
        f = feedparser.parse(feed)

        # Loop over every article.
        for e in f.entries:
            # Omit duplicate articles.
            if e.title in article_titles:
                continue

            # Extract the words.
            title = e.title.encode('utf8')
            content = strip_html(e.description.encode('utf8'))
            txt = title + content
            words = separate_words(txt)
            article_words.append({})
            article_titles.append(e.title)

            # Increase counts for this word in
            # all_words and in article_words.
            for word in words:
                all_words.setdefault(word, 0)
                all_words[word] += 1
                article_words[ec].setdefault(word, 0)
                article_words[ec][word] += 1
            ec += 1
    return all_words, article_words, article_titles


def make_matrix(allw, articlew):
    wordvec = []

    # Used for searching words that appear in more than 3 articles,
    # and but fewer than 60% of the total.
    MIN_ART = 3
    PERCENT = 0.6

    # Only take words that are common but not too common
    for w, c in allw.items():
        if c > MIN_ART and c < len(articlew) * PERCENT:
            wordvec.append(w)

    # Create word matrix.
    l1 = [[(word in f and f[word] or 0) for word in wordvec] for f in articlew]
    return l1, wordvec

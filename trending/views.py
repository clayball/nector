from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader

import feedparser
import re


'''Note:
   Chapter 10 of the O'Reilly book "Collective Intelligence" by
   Toby Segaran (2007) served as the inspiration for this application.
   Much of this code was borrowed from there, so it would be wrong
   not to provide credit to its true author; thanks Toby!
'''

feedlist = ['http://feeds.reuters.com/reuters/topNews',
            'http://feeds.reuters.com/reuters/domesticNews',
            'http://feeds.reuters.com/reuters/technologyNews',]

def index(request):
    '''Render default page for the Trending app.'''
    context = {}

    # Testing.
    allw, artw, artt = get_article_words()
    wordmatrix, wordvec = make_matrix(allw, artw)

    context['vector'] = wordvec[0:10]
    context['title'] = artt[1]

    print wordmatrix

    return render(request, 'trending/trending.html', context)


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

"""Provides function to scrape the D*A*M Forum Buy/Sell & Trade thread posts"""

import robotparser
import urllib2
import lxml.html
from lxml.cssselect import CSSSelector

from post import *

_dam_url = "http://stompboxes.co.uk/"
_forum_url = _dam_url + "forum/"
_bst_thread = _forum_url + "viewforum.php?f=9"

rp = robotparser.RobotFileParser()
rp.set_url(_dam_url + "robots.txt")

def scrape_dam_forum():
    """Scrapes D*A*M forum Buy/Sell & Trade thread posts.
    Return list of Posts"""

    rp.read()
    if rp.can_fetch("*", _bst_thread):
        page = _get_page(_bst_thread)
        html = lxml.html.fromstring(page)

        post_listings = _get_post_listings(html)

        posts = []
        for listing in post_listings:
            posts.append(_get_post_details(listing))

        return posts
    else:
        _robots_not_allowed(_bst_thread)
        return None

def _robots_not_allowed(url):
    print "robots.txt does not allow fetching of: " + url

def _get_page(url):
    """Opens and reads web page. Return page as string."""

    response = urllib2.urlopen(url)
    page = response.read()
    return page

def _get_post_listings(html):
    """Scrapes thread listings. Return list of post listing nodes."""

    topics = CSSSelector("ul.topiclist.topics")(html)

    post_listings = CSSSelector("li.row:not(.sticky)")(topics[1])
    return post_listings

def _get_post_details(post_listing):
    """Scrape a post and return as a Post object."""

    title_node = CSSSelector("a.topictitle")(post_listing)[0]
    title = title_node.text_content()

    url = _forum_url + title_node.get("href")[2:]

    if rp.can_fetch("*", url):
        
        print "Scraping post: " + title

        post_page = lxml.html.fromstring(_get_page(url))

        author = _get_post_author(post_page)
        content = _get_post_content(post_page)
        images = _get_post_images(post_page)
        privateMessageLink = _get_private_message_link(post_page)

        return Post(title, author, url, content, images, privateMessageLink)
    else:
        _robots_not_allowed(url)
        return None

def _get_post_author(post_page):
    """Scrape the author name from a post."""

    author = CSSSelector(".username")(post_page)[1].text_content()
    return author

def _get_post_content(post_page):
    """Scrape the main body of a post."""

    content = CSSSelector(".content")(post_page)[0].text_content()
    return content

def _get_post_images(post_page):
    """Scrape the images from a post"""

    images = CSSSelector(".postbody img")(post_page)

    # filter out forum images that are not part of the post
    images = [img for img in images if "smilies" not in img.get("src") and "styles" not in img.get("src")]

    # add base url for relative urls
    images = [_forum_url + img.get("src")[2:] if img.get("src")[0:2] == "./" else img.get("src") for img in images]
    return images

def _get_private_message_link(post_page):
    """Scrape the private message link to the author of the post."""

    postID = CSSSelector("dl.postprofile")(post_page)[0].get("id")[7:]
    link = _forum_url + "ucp.php?i=pm&mode=compose&action=quotepost&p=" + postID
    return link
    
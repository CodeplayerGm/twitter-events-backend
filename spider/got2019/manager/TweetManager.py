import urllib,urllib.request,urllib.parse,json,re,datetime,sys,http.cookiejar
from .. import models
from pyquery import PyQuery
import requests
import random
random.seed(1)

def fetch_activities(tweet_id):
    retusers = []
    favorusers = []
    re_url = 'https://twitter.com/i/activity/retweeted_popup?id=%s' % (tweet_id)
    favor_url = 'https://twitter.com/i/activity/favorited_popup?id=%s' % (tweet_id)
    headers = {
        'Host': "twitter.com",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.%s' % (
            random.randint(0, 999)),
        'Accept': "application/json, text/javascript, */*; q=0.01",
        'Accept-Language': "de,en-US;q=0.7,en;q=0.3",
        'X-Requested-With': "XMLHttpRequest",
        'Referer': 'https://twitter.com/',
        'Connection': "keep-alive",
    }
    re_users = PyQuery(requests.get(re_url, headers=headers).json()['htmlUsers'])('ol.activity-popup-users')
    for re_user in re_users('div.account'):
        userPQ = PyQuery(re_user)
        userd = {
            'screen_name': userPQ.attr('data-screen-name'),
            'user_id': userPQ.attr('data-user-id'),
            'data_name': userPQ.attr('data-name'),
            'avatar_src': userPQ('img.avatar').attr('src'),
            'userbadges': userPQ('span.UserBadges').text(),
            'bio': userPQ('p.bio').text(),
        }
        retusers.append({userd['screen_name']: userd})
    favor_users = PyQuery(requests.get(favor_url, headers=headers).json()['htmlUsers'])('ol.activity-popup-users')
    for favor_user in favor_users('div.account'):
        userPQ = PyQuery(favor_user)
        userd = {
            'screen_name': userPQ.attr('data-screen-name'),
            'user_id': userPQ.attr('data-user-id'),
            'data_name': userPQ.attr('data-name'),
            'avatar_src': userPQ('img.avatar').attr('src'),
            'userbadges': userPQ('span.UserBadges').text(),
            'bio': userPQ('p.bio').text(),
        }
        favorusers.append({userd['screen_name']: userd})

    return retusers, favorusers

def fetch_entities(tweetPQ):
    hashtags = []
    urls = []
    for url in tweetPQ('p.js-tweet-text a'):
        d = dict(url.items())
        if 'data-expanded-url' in d.keys():  # d['class'] == 'twitter-timeline-link'
            # pdb.set_trace()
            urls.append({'href': d['href'], 'expanded_url': d['data-expanded-url']})
        if d['href'].startswith('/hashtag/'):
            hashtags.append(d['href'].split('?')[0].split('/')[-1])
    tweetPQ('p.js-tweet-text a.twitter-timeline-link').remove()
    return hashtags, urls

def getTweet(tweetHTML):
    tweetPQ = PyQuery(tweetHTML)
    tweet = models.Tweet()

    # 基本信息：推文id、会话id、
    id = tweetPQ.attr("data-tweet-id")
    conversation_id = tweetPQ.attr('data-conversation-id')
    createdTimeStamp = int(tweetPQ("small.time span.js-short-timestamp").attr("data-time"))

    # 用户基本信息：规范网名、用户id、网名、头像链接、账号认证信息
    screen_name = tweetPQ.attr('data-screen-name')
    user_id = tweetPQ.attr('data-user-id')
    data_name = tweetPQ.attr('data-name')
    avatar_src = tweetPQ('img.avatar').attr('src')
    userbadges = tweetPQ('span.UserBadges').text()

    # 在发送一次请求，补充用户信息
    userRequestURL = 'https://twitter.com/' + screen_name
    userJson = getJsonResponseWithURL(userRequestURL)
    print('get user:' + screen_name + ' info')
    print(userJson)


    # 推文主体 话题、url、推文回复原作者、语言、原文、后续过滤后的内容、
    hashtags, urls = fetch_entities(tweetPQ)
    mentions = tweetPQ.attr("data-mentions")
    lang = tweetPQ("p.js-tweet-text").attr('lang')
    raw_text = re.sub(r"\s+", " ", tweetPQ("p.js-tweet-text").text().replace('# ', '#').replace('@ ', '@'))
    # standard_text = re.sub(r"\s+", " ", tweetPQ("p.js-tweet-text").text().replace('# ', '').replace('@ ', ''))
    standard_text = ''
    # tweetPQ('p.js-tweet-text')('a').remove()
    # tweetPQ('p.js-tweet-text')('img').remove()
    # clean_text = tweetPQ("p.js-tweet-text").text()

    # 推文中的媒体信息：会话推文的最初发布文id、是否包含蓝色链接、图片url、是否有视频数据
    quote_id = tweetPQ('div.QuoteTweet a.QuoteTweet-link').attr('data-conversation-id')
    has_cards = tweetPQ.attr('data-has-cards')
    card_url = tweetPQ('div.js-macaw-cards-iframe-container').attr('data-card-url')
    img_src = tweetPQ('div.AdaptiveMedia-container img').attr('src')
    video_src = True if tweetPQ('div.AdaptiveMedia-video') else False

    # 推文动作信息：转发原作者id、原作者、回复量、转发量、喜欢量
    retweet_id = tweetPQ.attr('data-retweet-id')
    retweeter = tweetPQ.attr('data-retweeter')
    replies = int(
        tweetPQ("span.ProfileTweet-action--reply span.ProfileTweet-actionCount").attr("data-tweet-stat-count").replace(
            ",", ""))
    retweets = int(tweetPQ("span.ProfileTweet-action--retweet span.ProfileTweet-actionCount").attr(
        "data-tweet-stat-count").replace(",", ""))
    favorites = int(tweetPQ("span.ProfileTweet-action--favorite span.ProfileTweet-actionCount").attr(
        "data-tweet-stat-count").replace(",", ""))

    ## tweet数据类型
    tweet.id = id
    tweet.conversation_id = conversation_id
    tweet.is_reply = tweet.id != tweet.conversation_id
    tweet.created_at = datetime.datetime.fromtimestamp(createdTimeStamp)

    # user
    tweet.user = {
        'screen_name': screen_name,
        'user_id': user_id,
        'data_name': data_name,
        'avatar_src': avatar_src,
        'userbadges': userbadges,
    }

    # media
    tweet.media = {
        'quote_id': quote_id,
        'has_cards': has_cards,
        'card_url': card_url,
        'img_src': img_src,
        'has_video': video_src
    }

    # text
    tweet.hashtags = hashtags
    tweet.urls = urls
    tweet.mentions = mentions.split(' ') if mentions is not None else None
    tweet.lang = lang
    tweet.raw_text = raw_text
    tweet.standard_text = standard_text

    # action
    tweet.action = {
        'replies': replies,
        'retweets': retweets,
        'favorites': favorites,
        'retweet_id': retweet_id,
        'retweeter': retweeter,
        'is_retweet': True if retweet_id is not None else False,
    }

    return tweet

class TweetManager:

    def __init__(self):
        pass

    @staticmethod
    def getTweets(tweetCriteria, receiveBuffer=None, bufferLength=100, proxy=None):
        refreshCursor = ''
        results = []
        resultsAux = []
        cookieJar = http.cookiejar.CookieJar()

        # if hasattr(tweetCriteria, 'username') and (tweetCriteria.username.startswith("\'") or tweetCriteria.username.startswith("\"")) and (tweetCriteria.username.endswith("\'") or tweetCriteria.username.endswith("\"")):
        #     tweetCriteria.username = tweetCriteria.username[1:-1]

        active = True

        while active:
            json = TweetManager.getJsonReponse(tweetCriteria, refreshCursor, cookieJar, proxy)
            if len(json['items_html'].strip()) == 0:
                break
            if 'min_position' not in json.keys():
                break
            refreshCursor = json['min_position']
            tweets = PyQuery(json['items_html'])('div.js-stream-tweet')
            if len(tweets) == 0:
                break
            # 遍历网页中的tweet数据
            for tweetHTML in tweets:
                # try:
                tweet = getTweet(tweetHTML)
                # except:
                #     continue
                if hasattr(tweetCriteria, 'sinceTimeStamp'):
                    if tweet.created_at < tweetCriteria.sinceTimeStamp:
                        active = False
                        break
                if hasattr(tweetCriteria, 'untilTimeStamp'):
                    if tweet.created_at <= tweetCriteria.untilTimeStamp:
                        results.append(tweet.__dict__)
                else:
                    results.append(tweet.__dict__)

                if receiveBuffer and len(resultsAux) >= bufferLength:
                    receiveBuffer(resultsAux)
                    resultsAux = []

                if 0 < tweetCriteria.maxTweets <= len(results):
                    active = False
                    break

        if receiveBuffer and len(resultsAux) > 0:
            receiveBuffer(resultsAux)

        return results

    @staticmethod
    def getJsonReponse(tweetCriteria, refreshCursor, cookieJar, proxy):
        url = "https://twitter.com/i/search/timeline?f=tweets&q=%s&src=typd&%smax_position=%s"
        urlGetData = ''
        if hasattr(tweetCriteria, 'username'):
            urlGetData += ' from:' + tweetCriteria.username
        if hasattr(tweetCriteria, 'since'):
            urlGetData += ' since:' + tweetCriteria.since
        if hasattr(tweetCriteria, 'until'):
            urlGetData += ' until:' + tweetCriteria.until
        if hasattr(tweetCriteria, 'querySearch'):
            urlGetData += ' ' + tweetCriteria.querySearch
        if hasattr(tweetCriteria, 'lang'):
            urlLang = 'lang=' + tweetCriteria.lang + '&'
        else:
            urlLang = ''

        url = url % (urllib.parse.quote(urlGetData), urlLang, refreshCursor)
        headers = [
            ('Host', "twitter.com"),
            ('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"),
            ('Accept', "application/json, text/javascript, */*; q=0.01"),
            ('Accept-Language', "de,en-US;q=0.7,en;q=0.3"),
            ('X-Requested-With', "XMLHttpRequest"),
            ('Referer', url),
            ('Connection', "keep-alive")
        ]
        if proxy:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({'http': proxy, 'https': proxy}), urllib.request.HTTPCookieProcessor(cookieJar))
        else:
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookieJar))
        opener.addheaders = headers

        try:
            response = opener.open(url)
            jsonResponse = response.read()
        except:
            print("Twitter weird response. Try to see on browser: https://twitter.com/search?q=%s&src=typd" % urllib.parse.quote(urlGetData))
            print("Unexpected error:", sys.exc_info()[0])
            sys.exit()

        dataJson = json.loads(jsonResponse.decode())

        return dataJson


def getJsonResponseWithURL(url):
    cookieJar = http.cookiejar.CookieJar()
    headers = [
        ('Host', "twitter.com"),
        ('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"),
        ('Accept', "application/json, text/javascript, */*; q=0.01"),
        ('Accept-Language', "de,en-US;q=0.7,en;q=0.3"),
        ('X-Requested-With', "XMLHttpRequest"),
        ('Referer', url),
        ('Connection', "keep-alive")
    ]
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookieJar))
    opener.addheaders = headers
    response = opener.open(url)
    jsonResponse = response.read()
    dataJson = json.loads(jsonResponse.decode())

    return dataJson

if __name__ == '__main__':
    userRequestURL = 'https://twitter.com/' + 'Uyghurspeaker'
    userJson = getJsonResponseWithURL(userRequestURL)
    print(userJson)
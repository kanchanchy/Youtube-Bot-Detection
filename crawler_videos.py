from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import pandas as pd
import json
import csv


DEVELOPER_KEY = YOUR_API_KEY
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
REGION_CODE = 'US'
MAX_DATA = 100
MAX_RESULT = 50
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

def get_video_categories():
    categories = youtube.videoCategories().list(
        part='id,snippet',
        regionCode='US',
        ).execute()
    result = []
    for c in categories.get('items', []):
        id, name = c['id'], c['snippet']['title']
        result.append((id, name))
    return result
    
def youtube_search():
    # Call the search.list method to retrieve results matching the specified
    # query term.
    categories = get_video_categories()
    for category in categories: 
        id, name = category
        print("Search youtube for category {}".format(name))
        search_response = youtube.search().list(
            type='video',
            part="id",
            videoCategoryId=id,
            maxResults=MAX_RESULT,
        ).execute()
        yield search_response.get("items", [])
        token = search_response.get('nextPageToken', None)
        num = MAX_DATA - MAX_RESULT
        while token is not None and num > 0:
            search_response = youtube.search().list(
                type='video',
                part="id",
                maxResults=MAX_RESULT,
                videoCategoryId=id,
                pageToken=token
            ).execute()
            token = search_response.get('nextPageToken', None)
            num -= MAX_RESULT
            yield search_response.get("items", [])


def get_id_list():
    #data = youtube_search()
    data = video_list_by_channel_id()
    for d in data:
        ids = []
        for item in d:
            ids.append(item['id']['videoId'])
        yield ','.join(ids)


def get_video_detail():
    ids = get_id_list()
    for id in ids:
        response = youtube.videos().list(
        part='snippet,statistics',
        id=id,
        maxResults=MAX_RESULT
        ).execute()
        yield response


def unicode_encode(s):
    return s.encode('utf-8')

def format_video(row):
    video_id=row.get('id')
    channel_id = row.get('snippet').get('channelId')
    subscription_count = 0
    subscription_response = channels_list_by_id(part='statistics', id=channel_id)
    subscription_item = subscription_response['items']
    for item in subscription_item:
        subscription_count = item.get('statistics').get('subscriberCount')
        break

    max_comment_one_user, comment_per_user = get_all_comments_by_vedio_id(video_id)
    
    d = dict(
        id=video_id,
        title=unicode_encode(row.get('snippet').get('title')),
        thumbnails=row.get('snippet').get('thumbnails').get('default').get('url'),
        channelId=channel_id,
        categoryId=row.get('snippet').get('categoryId'),
        channelSubscription = subscription_count,
        viewCount=row.get('statistics').get('viewCount'),
        likeCount=row.get('statistics').get('likeCount'),
        dislikeCount=row.get('statistics').get('dislikeCount'),
        favoriteCount=row.get('statistics').get('favoriteCount'),
        commentCount=row.get('statistics').get('commentCount'),
        maxCommentOneUser = max_comment_one_user,
        commentPerUser = comment_per_user
    )
    return d

def remove_empty_kwargs(**kwargs):
    good_kwargs = {}
    if kwargs is not None:
        for key, value in kwargs.items():
            if value:
                good_kwargs[key] = value
    return good_kwargs

def channels_list_by_id(**kwargs):
  # See full sample for function
  kwargs = remove_empty_kwargs(**kwargs)

  response = youtube.channels().list(
    **kwargs
  ).execute()

  res = json.dumps(response)
  res = json.loads(res)
  return res


def parse_comments_json(comments_item, author_dict, author_list):
    for item in comments_item:
        authorName = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
        publishTime = item['snippet']['topLevelComment']['snippet']['publishedAt']
        if authorName not in author_dict:
            author_dict[authorName] = 1
            author_list.extend(authorName)
        else:
            author_dict[authorName] = author_dict.get(authorName) + 1
        
    return author_dict, author_list


def video_list_by_channel_id():
    channel_ids = ['UCLXo7UDZvByw2ixzpQCufnA', 'UCBi2mrWuNuyYy4gbM6fU18Q', 'UCpVm7bg6pXKo1Pr6k5kxG9A', 'UCsT0YIqwnpJCM-mx7-gSA4Q',
                   'UCFFbwnve3yF62-tVXkTyHqg', 'UCKqH_9mk1waLgBiL2vT5b9g', 'UCq-Fj5jknLsUf-MWSy4_brA']
    
    for channel_id in channel_ids:
        search_response = youtube.search().list(
            part='id', maxResults=MAX_RESULT, type = 'video', channelId=channel_id
        ).execute()

        yield search_response.get("items", [])
        token = search_response.get('nextPageToken', None)
        num = MAX_DATA - MAX_RESULT
        while token is not None and num > 0:
            search_response = youtube.search().list(
                part='id', maxResults=MAX_RESULT, type = 'video', channelId=channel_id, pageToken=token
            ).execute()
            token = search_response.get('nextPageToken', None)
            num -= MAX_RESULT
            yield search_response.get("items", [])


def get_all_comments_by_vedio_id(video_id):
    author_list = []
    author_dict = {}
    max_comment_one_user = 0
    comment_per_user = 0
    
    try:
        response = youtube.commentThreads().list(
            part='snippet,replies', videoId=video_id, maxResults=100
        ).execute()
        if response:
            author_dict, author_list = parse_comments_json(response.get("items", []), author_dict, author_list)

        token = response.get('nextPageToken', None)
        while token is not None:
            try:
                response = youtube.commentThreads().list(
                    part='snippet,replies', videoId=video_id, maxResults=100, pageToken=token
                ).execute()
                token = response.get('nextPageToken', None)
                if response:
                    author_dict, author_list = parse_comments_json(response.get("items", []), author_dict, author_list)
            except:
                break
    except:
        return max_comment_one_user, comment_per_user
        
    if len(author_list) == 0:
        return max_comment_one_user, comment_per_user
    else:
        sum_comment = 0
        count = 0
        for author in author_list:
            if author in author_dict:
                sum_comment = sum_comment + author_dict.get(author)
                if author_dict.get(author) > max_comment_one_user:
                    max_comment_one_user = author_dict.get(author)
                count = count + 1

        if count > 0:
            comment_per_user = sum_comment/count
        return max_comment_one_user, comment_per_user

def get_video_id_by_channel(channel_id):
    subscription_count = 0
    subscription_response = channels_list_by_id(part='statistics', id=channel_id)
    subscription_item = subscription_response['items']
    for item in subscription_item:
        subscription_count = item.get('statistics').get('subscriberCount')
        viewCount = item.get('statistics').get('viewCount')
        likeCount = item.get('statistics').get('likeCount')
        dislikeCount = item.get('statistics').get('dislikeCount')
        commentCount = item.get('statistics').get('commentCount')


def crawl_video():
    res_pd = pd.DataFrame(columns=['id', 'title', 'thumbnails', 'channelId', 'categoryId', 'channelSubscription', 'viewCount', 'likeCount',
                                   'dislikeCount', 'favoriteCount', 'commentCount', 'maxCommentOneUser', 'commentPerUser'])
    res = get_video_detail()
    for r in res:
        for row in r.get('items', []):
            if row:
                video = format_video(row)
                res_pd = res_pd.append({'id' : video.get('id') , 'title' : video.get('title'), 'thumbnails' : video.get('thumbnails'),
                                        'channelId' : video.get('channelId'), 'categoryId' : video.get('categoryId'),
                                        'channelSubscription' : video.get('channelSubscription'), 'viewCount' : video.get('viewCount'),
                                        'likeCount' : video.get('likeCount'), 'dislikeCount' : video.get('dislikeCount'),
                                        'favoriteCount' : video.get('favoriteCount'), 'commentCount' : video.get('commentCount'),
                                        'maxCommentOneUser' : video.get('maxCommentOneUser'), 'commentPerUser' : video.get('commentPerUser')}, ignore_index=True)
    res_pd.to_csv("youtube_data_verified_comments.csv")


if __name__ == "__main__":
    argparser.add_argument("--q", help="Search term", default="Google")
    argparser.add_argument("--max-results", help="Max results", default=25)
    args = argparser.parse_args()
    try:
        crawl_video()
    except HttpError as e:
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))

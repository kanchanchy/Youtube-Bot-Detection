
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 20:30:54 2018

@author: Lihui Liu
"""

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import json
import csv
import pandas as pd
import time
#import treq
# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyAG7NfffU5qEpMK0-E_OnNbktGKwH6byXk"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
REGION_CODE = 'US'
MAX_DATA = 100
MAX_RESULT = 50
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

def remove_empty_kwargs(**kwargs):
    good_kwargs = {}
    if kwargs is not None:
        for key, value in kwargs.items():
            if value:
                good_kwargs[key] = value
    return good_kwargs


def comment_threads_list_by_video_id(client, **kwargs):
  # See full sample for function
  kwargs = remove_empty_kwargs(**kwargs)

  response = client.commentThreads().list(
    **kwargs
  ).execute()

  res = json.dumps(response)
  res = json.loads(res)
  return res


def get_new_dataframe():
    res = pd.DataFrame(columns=['vedio_id', 'author_name', 'time'])
    return res

def unicode_encode(s):
    return s.encode('utf-8')

def parse_comments_json(comments_json, vedioId):
    res = get_new_dataframe()
    comments_item = comments_json['items']
    for item in comments_item:
        authorName = unicode_encode(item['snippet']['topLevelComment']['snippet']['authorDisplayName'])
        publishTime = unicode_encode(item['snippet']['topLevelComment']['snippet']['publishedAt'])
        res = res.append({'vedio_id' : vedioId , 'author_name' : authorName, 'time' : publishTime}, ignore_index=True)
        
    return res
        
    
def get_all_comments_by_vedio_id(vedio_id):
    res = get_new_dataframe()
    query_response = comment_threads_list_by_video_id(youtube, part='snippet,replies', videoId=vedio_id, maxResults=100)
    if query_response:
        tmp_df = parse_comments_json(query_response, vedio_id)
        res = pd.concat([res, tmp_df])
        
    try:
        next_page_token = query_response["nextPageToken"]
    except:
        return res
        
    i = 0
    while next_page_token:
        retry = 3
        while retry > 0:
            try:
                query_response = comment_threads_list_by_video_id(youtube, part='snippet,replies', videoId=vedio_id, pageToken=next_page_token, maxResults=100)
                break
            except:
                retry = retry - 1
        if retry == 0:
            print(next_page_token)
            time.sleep(0.05)
            continue
        tmp_df = parse_comments_json(query_response, vedio_id)
        res = pd.concat([res, tmp_df])
        try:
            next_page_token = query_response["nextPageToken"]
        except:
            break
        print(i)
        i = i + 1
        time.sleep(0.005)
        
    return res
        
#res_df = get_all_comments_by_vedio_id("b73BI9eUkjM")
#res_df = res_df.reset_index()
#res_df.to_csv("comments.csv")

id_list = ['_KE_-EdMhDI']

for y_id in id_list:
    res_df = get_all_comments_by_vedio_id(y_id)
    res_df = res_df.reset_index()
    res_df.to_csv("Comments-just-author/comments-just-author-" + y_id + ".csv")
# m7Bc3pLyij0

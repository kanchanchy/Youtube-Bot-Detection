import matplotlib.pyplot as plt
import math
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.cluster import SpectralClustering
from sklearn import svm
from sklearn.preprocessing import MinMaxScaler

def filterData(train_pd):
    data_frame = pd.DataFrame(columns=['id', 'subscriber_count', 'view_count', 'like_count', 'dislike_count', 'comment_count', 'like_vs_view', 'comment_vs_view', 'dislike_vs_like', 'subscriber_vs_view'])
    train_array = []

    for row in train_pd.itertuples():
        video_id = getattr(row, "id")
        subscriber_count = getattr(row, "channelSubscription")
        view_count = getattr(row, "viewCount")
        like_count = getattr(row, "likeCount")
        dislike_count = getattr(row, "dislikeCount")
        comment_count = getattr(row, "commentCount")

        if (np.isnan(subscriber_count) or np.isnan(view_count) or np.isnan(like_count) or np.isnan(dislike_count) or np.isnan(comment_count)):
            continue
        
        like_vs_view = 0
        comment_vs_view = 0
        dislike_vs_like = 0
        subscriber_vs_view = 0
        if view_count > 300:
            like_vs_view = like_count/view_count
            comment_vs_view = comment_count/view_count
            subscriber_vs_view = subscriber_count/view_count
        else:
            continue
        if like_count > 0:
            dislike_vs_like = dislike_count/like_count
        else:
            dislike_vs_like = dislike_count

        train_array.append([like_vs_view, comment_vs_view, dislike_vs_like])
        data_frame = data_frame.append({'id' : video_id, 'subscriber_count' : subscriber_count, 'view_count' : view_count, 'like_count' : like_count, 'dislike_count' : dislike_count, 'comment_count' : comment_count, 'like_vs_view' : like_vs_view, 'comment_vs_view' : comment_vs_view, 'dislike_vs_like' : dislike_vs_like, 'subscriber_vs_view' : subscriber_vs_view}, ignore_index=True)
        
    train_array = np.array(train_array)
    return train_array, data_frame


def performKMeans(train_array, data_frame):
    kmeans = KMeans(n_clusters=2)
    kmeans.fit(train_array)

    labels = kmeans.labels_

    cluster_0 = []
    cluster_1 = []
    print("\n")

    for i in range(len(train_array)):
        if labels[i] == 0:
            cluster_0.append([i, data_frame.at[i, 'id']])
        else:
            cluster_1.append([i, data_frame.at[i, 'id']])
    
    bot_cluster = []
    if len(cluster_0) < len(cluster_1):
        bot_cluster = cluster_0
    else:
        bot_cluster = cluster_1

    for i in range(len(bot_cluster)):
        print(bot_cluster[i][0], ": ", bot_cluster[i][1])

    print("\nNumber of 0: ", len(cluster_0))
    print("Number of 1: ", len(cluster_1))


#start of main block where execution will begin
if __name__ == '__main__':

    #reading csv files
    train_pd = pd.read_csv('youtube_data.csv')
    train_array, data_frame = filterData(train_pd)
    scaler = MinMaxScaler()
    train_array = scaler.fit_transform(train_array)
    data_frame.to_csv("youtube_data_filtered.csv")

    performKMeans(train_array, data_frame)



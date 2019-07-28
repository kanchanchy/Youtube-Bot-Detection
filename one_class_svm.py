import matplotlib.pyplot as plt
import math
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
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
            '''if subscriber_count > 0:
                subscriber_vs_view = view_count/subscriber_count
            else:
                subscriber_vs_view = view_count'''
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


def perform_one_class_svm(train_array, train_data_frame, test_array, test_data_frame):
    model = svm.OneClassSVM(nu=0.001, kernel="rbf", gamma=0.1)
    model.fit(train_array)
    y_pred_train = model.predict(train_array)
    n_error_train = y_pred_train[y_pred_train == -1].size
    y_pred_test = model.predict(test_array)
    n_error_test = y_pred_test[y_pred_test == -1].size
    print("Different Train Data: ", n_error_train)
    print("Different Test Data: ", n_error_test)
    for i in range(len(y_pred_test)):
        if y_pred_test[i] == -1:
            print(i, ": ", test_data_frame.at[i, 'id'])


#start of main block where execution will begin
if __name__ == '__main__':

    #reading csv files
    train_pd = pd.read_csv('youtube_data_verified.csv')
    train_array, train_data_frame = filterData(train_pd)
    scaler = MinMaxScaler()
    train_array = scaler.fit_transform(train_array)
    train_data_frame.to_csv("youtube_data_verified_filtered.csv")

    test_pd = pd.read_csv('youtube_data.csv')
    test_array, test_data_frame = filterData(test_pd)
    scaler = MinMaxScaler()
    test_array = scaler.fit_transform(test_array)
    test_data_frame.to_csv("youtube_data_filtered.csv")

    perform_one_class_svm(train_array, train_data_frame, test_array, test_data_frame)



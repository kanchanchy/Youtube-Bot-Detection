import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import math
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.cluster import SpectralClustering
from sklearn import svm
from sklearn.preprocessing import MinMaxScaler

def filterData(train_pd):
    #data_frame = pd.DataFrame(columns=['time'])
    train_array = []

    for row in train_pd.itertuples():
        time = getattr(row, "time")
        time = datetime.strptime(time)
        train_array.append(time)
        
    return train_array


def performKMeans(train_array, data_frame):
    #kmeans = KMeans(n_clusters=2)
    kmeans = SpectralClustering(n_clusters=2, assign_labels="kmeans", gamma=2.0)
    kmeans.fit(train_array)

    #print(kmeans.cluster_centers_)
    #print(kmeans.labels_)
    labels = kmeans.labels_

    cluster_0 = []
    cluster_1 = []
    print("\n")
    '''for i in range(len(train_array)):
        predict_me = train_array[i].reshape(-1, len(train_array[i]))
        label = kmeans.predict(predict_me)
        if label[0] == 0:
            cluster_0.append([i, data_frame.at[i, 'id']])
        else:
            cluster_1.append([i, data_frame.at[i, 'id']])'''

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
    train_pd = pd.read_csv('Comments-just-author/comments-just-author-_eQLFVpOYm4.csv')
    train_array = filterData(train_pd)
    print(train_array)
    '''scaler = MinMaxScaler()
    train_array = scaler.fit_transform(train_array)
    data_frame.to_csv("youtube_data_filtered.csv")
    performKMeans(train_array, data_frame)'''

    '''plt.scatter(X[:,0],X[:,1], label='True Position')
    #plt.show()'''



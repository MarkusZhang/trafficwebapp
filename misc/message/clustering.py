"""
Utility for clustering message points
"""
from time import time

from sklearn.cluster import MiniBatchKMeans

def get_clusters(src_fname,cluster_size):
    """
    :param src_fname: file name of the source file, which should contain lines like "103.67835\t1.32451\t1"
    :param cluster_size:the average size of a cluster
    :return: a list of [longitude,latitude,status], status is 0 or 1
    """
    lines = open(src_fname).readlines()

    X = [[float(line.split("\t")[0]),float(line.split("\t")[1])]
            for line in lines]

    y = [int(line.split("\t")[2]) for line in lines]

    print (len(X))

    # knn_graph = kneighbors_graph(X, 30, include_self=False)
    n_clusters = len(X) / cluster_size
    model = MiniBatchKMeans(n_clusters=n_clusters, init='k-means++', n_init=1,
                             init_size=1000, batch_size=1000).fit(X)

    labels = model.labels_
    cluster_centers = model.cluster_centers_

    # find the cluster 0/1
    condition_dict = {i:0 for i in range(len(cluster_centers))}

    for j in range(len(labels)):
        label = labels[j] # label of this point
        y_value = y[j] # y value of this point
        if (y_value == 1):
            condition_dict[label] += 1
        else:
            condition_dict[label] -= 1

    condition_dict = {key:(0 if value < 0 else 1) for key,value in condition_dict.items()}

    centers_with_condition = [[cluster_centers[i][0],cluster_centers[i][1],condition_dict[i]] for i in range(len(cluster_centers))]

    return centers_with_condition

if __name__ == "__main__":
    clusters = get_clusters(src_fname="D:/fyp/data_repo/message/slotmsg_6-8-30.txt",cluster_size=16)
    cluster_strs = ["\t".join(map(str,item)) for item in clusters]
    with open("D:/fyp/data_repo/message/slotmsg_6-8-30_clusters_16.txt","w") as f:
        f.write("\n".join(cluster_strs))
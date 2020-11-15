import networkx as nx
import vk as vk
from vk.exceptions import VkAPIError
import time
import matplotlib.pyplot as plt
import datetime
import csv
import ast
from sklearn.cluster import KMeans
import pandas as pd
import numpy as np
from csv import DictReader
from scipy.cluster.hierarchy import dendrogram, ward, complete
from multiprocessing import Pool

self_id, friends_id, friends_friends_id, friends_friends_id_dict = None, [], [], {}
G = nx.Graph()
varieties = list()


def get_self_id(vk_api):
    global self_id
    self_id = vk_api.users.get(v=5.92)[0]['id']


def get_friends_id(vk_api):
    global friends_id
    friends_id = vk_api.friends.get(v=5.92)['items']


def get_friends_of_friends(vk_api):
    global friends_friends_id
    for friends in friends_id:
        time.sleep(0.333)
        try:
            resp = vk_api.friends.get(user_id=friends, v=5.92)
            friends_friends_id += resp.get('items')
            friend_id = str(resp.get('items')).replace('[', "").replace(']', "").split(', ')
            friends_friends_id_dict[friends] = friend_id
        except VkAPIError:
            time.sleep(0.5)
            resp = vk_api.users.get(user_ids=friends, v=5.92)
        if 'deactivated' in resp:
            continue


def building_graph():
    global G
    fill_graph()
    plt.figure(figsize=(50, 50))
    nx.draw_networkx(G, with_labels=False)
    plt.show()


def get_info(vk_api, user):
    users_information = []
    try:
        req_per_sec = time.time()
        users_information.append(user)
        users_information.append(vk_api.photos.get(owner_id=user, album_id='profile', v=5.92)['count'])
        user_info = vk_api.users.get(user_id=user, fields='bdate, city, status', v=5.92)
        try:
            users_information.append(2020 -
                                     int(datetime.datetime.strptime(user_info[0]
                                                                    ['bdate'], '%d.%m.%Y').strftime('%Y')))
        except:
            users_information.append('')
        try:
            users_information.append(user_info[0]['city']['id'])
            users_information.append(user_info[0]['city']['title'])
        except:
            users_information.append('')
            users_information.append('')
        users_information.append(user_info[0]['status'])
        users_information.append(vk_api.wall.get(owner_id=user, v=5.92)['count'])
        time.sleep(1 - (time.time() - req_per_sec))
        print(users_information)
        return users_information
    except:
        pass


def write_users_dict():
    with open('users_dict.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Friends_id','Friends_Friends_id'])
        for key, value in friends_friends_id_dict.items():
            writer.writerow([key, value])


def write_users_info(friends_inf):
    with open('users_info.csv', 'a+', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(friends_inf)


def fill_user_info(api):
    write_users_info(['Id', 'Photos', 'Age', 'City_id', 'City', 'Status', 'Profile_entries'])
    for user in friends_friends_id:
        a = get_info(api, user)
        try:
            if a is not None:
                write_users_info(a)
        except:
            pass


def fill_graph():
    global G
    infile = DictReader(open('users_dict.csv', 'r'))
    for row in infile:
        x = ast.literal_eval(row['Friends_Friends_id'])
        for i in x:
            G.add_nodes_from([row['Friends_id'], i])
            G.add_edge(row['Friends_id'], i)


def fill_cluster():
    global varieties
    with open('users_info.csv', 'r') as read_obj:
        csv_dict_reader = DictReader(read_obj)
        for row in csv_dict_reader:
            if row['Age'] != '' and row['City'] != '' and row['City_id'] != '':
                try:
                    varieties.append([int(row['Photos']), int(row['Age'])])
                except:
                    pass


def k_mean():
    cluster_data = np.array(varieties)
    plt.scatter(cluster_data[:, 0], cluster_data[:, 1], s = 15, cmap = 'summer')
    plt.show()
    kmeans = KMeans(n_clusters=7)
    kmeans.fit(cluster_data)
    y_kmeans = kmeans.predict(cluster_data)
    plt.scatter(cluster_data[:, 0], cluster_data[:, 1], c=y_kmeans, s=20, cmap='summer')
    centers = kmeans.cluster_centers_
    plt.scatter(centers[:, 0], centers[:, 1], c='blue', s=100, alpha=0.9);
    plt.show()


def main():
    token = 'ae27ac0014e9212b3779574bbb1039b92a57bec8d06b2523231c56676582f96243d1b7d97455840b60719'
    session = vk.Session(access_token=token)  # Авторизация
    api = vk.API(session)
    # get_self_id(api)
    # get_friends_id(api)
    # get_friends_of_friends(api)
    # write_users_dict()
    # building_graph()
    # fill_user_info(api)
    # k_mean()
    fill_cluster()
    k_mean()


if __name__ == "__main__":
    main()


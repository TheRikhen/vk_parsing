import networkx as nx
import vk as vk
from vk.exceptions import VkAPIError
import time
import matplotlib.pyplot as plt
import datetime
import csv
import ast
from sklearn import datasets
from sklearn.cluster import KMeans
import pandas as pd

self_id, friends_id, friends_friends_id, friends_friends_id_dict = None, [], [], {}
G = nx.Graph()


def get_self_id(vk_api):
    global self_id
    self_id = vk_api.users.get(v=5.92)[0]['id']


def get_friends_id(vk_api):
    response = vk_api.friends.get(v=5.92)
    global friends_id
    friends_id = response.get('items')


def get_friends_of_friends(vk_api):
    global friends_friends_id
    for friends in friends_id:
        time.sleep(0.333)
        try:
            resp = vk_api.friends.get(user_id=friends, v=5.92)
            friends_friends_id += resp.get('items')
            print(friends_friends_id)
            friend_id = str(resp.get('items')).replace('[', "").replace(']', "").split(', ')
            friends_friends_id_dict[friends] = friend_id
        except VkAPIError:
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
        return users_information
    except:
        pass


def write_users_dict():
    with open('users_dict.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in friends_friends_id_dict.items():
            writer.writerow([key, value])


def write_users_info(friends_inf):
    with open('users_info.csv', 'a+', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(friends_inf)


def fill_graph():
    global G
    infile = csv.reader(open('users_dict.csv', 'r'))
    for row in infile:
        x = ast.literal_eval(row[1])
        for i in x:
            G.add_nodes_from([row[0], i])
            G.add_edge(row[0], i)


def k_mean():
    # Загружаем набор данных
    seeds_df = pd.read_csv(
        "users_info.csv")
    varieties = list(seeds_df)
    # Описываем модель
    model = KMeans(n_clusters=7)
    # Проводим моделирование
    print(varieties)
    model.fit(varieties)
    # Предсказание на единичном примере
    predicted_label = model.predict([[7.2, 3.5, 0.8, 1.6]])
    # Предсказание на всем наборе данных
    # all_predictions = model.predict(iris_df.data)
    # Выводим предсказания
    print(predicted_label)
    # print(all_predictions)


def main():
    token = 'cf4ba26222fc4d42bb85d43009234463ee3314a0cad35d9f0b32848ca0de5fa0a849f89c30f2a17956e4c'
    session = vk.Session(access_token=token)  # Авторизация
    api = vk.API(session)
    # get_self_id(api)
    # get_friends_id(api)
    # get_friends_of_friends(api)
    # write_users_dict()
    # building_graph()
    k_mean()
    # for user in friends_friends_id:
    #     a = get_info(api, user)
    #     if a is not None:
    #         write_users_info(a)




if __name__ == "__main__":
    main()

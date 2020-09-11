import networkx as nx
import vk as vk
from vk.exceptions import VkAPIError
import time
import matplotlib.pyplot as plt
import datetime
import csv
import ast

self_id, friends_id, friends_friends_id, friends_friends_id_dict = None, [], [], {}
G = nx.DiGraph


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
    G.add_node(self_id, level=1)
    for friends in friends_id:
        G.add_edge(self_id, friends)
    read_friends_friends_dict()

    plt.figure(figsize=(80, 80))
    nx.draw_networkx(G)
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


def write_friends_friends_dict():
    with open('dict.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in friends_friends_id_dict.items():
            writer.writerow([key, value])


def write_friends_friends_info(friends_inf):
    with open('friends_friends_info.csv', 'a+', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(friends_inf)


def read_friends_friends_dict():
    global G
    infile = csv.reader(open('dict.csv', 'r'))
    for row in infile:
        for friend in friends_id:
            print(friend)
            if row[0] == str(friend):
                x = ast.literal_eval(row[1])
                print(x)
                for i in x:
                    print(i)
                    G.add_edge(friend, i)


def main():
    token = '4d055480df2872b494e1781087faa01a8ff8b313565a7505937f6ac34688e9b53780081d752a381ad8373'
    session = vk.Session(access_token=token)  # Авторизация
    api = vk.API(session)
    get_self_id(api)
    get_friends_id(api)
    # get_friends_of_friends(api)
    # write_friends_friends_dict()
    # building_graph()
    read_friends_friends_dict()
    # for user in friends_friends_id:
    #     a = get_info(api, user)
    #     if a is not None:
    #         write_friends_friends_info(a)


if __name__ == "__main__":
    main()

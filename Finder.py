import requests
import vk_api
from datetime import date
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange
import random
import time
from BD import User, Partners, Photo, session


token = ' '
token_search = ' '
vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)
headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Content-Encoding': 'utf-8'}


class Friend_Finder():
    def __init__(self, app_token, personal_token):
        self.app_token = app_token
        self.personal_token = personal_token


    def write_msg(self, user_id, message):
        vk.method('messages.send', {'user_id': user_id, 'message': message, "random_id": randrange(10 ** 7)})


    def user_info(self, id):
        params_user = {'access_token': self.personal_token, 'user_ids': id,
                       'fields': 'sex, bdate, city', 'v': 5.124}
        request = requests.get(f'https://api.vk.com/method/users.get', params=params_user).json()['response'][0]
        self.about_user = {'first_name': '',
                           'last_name': '',
                           'gender': '',
                           'age': '',
                           'city': '',}
        today = date.today()
        self.about_user['first_name'] = request['first_name']
        self.about_user['last_name'] = request['last_name']
        if 'sex' in request.keys():
            self.about_user['gender'] = request['sex']
        else:
            self.write_msg(id, "Пожалуйста, укажите свой пол (1 - м, 2 - ж)")
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    if event.from_user:
                        self.about_user['gender'] = int(event.text)
                        break
        if 'bdate' in request.keys():
            bdate_year = request['bdate'].split('.')
            if len(bdate_year) == 3:
                self.about_user['age'] = today.year - int(bdate_year[-1])
            else:
                self.write_msg(id, 'Пожалуйста, укажите свой возраст: ')
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        if event.from_user:
                            self.about_user['age'] = int(event.text)
                            break
        else:
            self.write_msg(id, 'Пожалуйста, укажите свой возраст: ')
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    self.about_user['age'] = int(event.text)
                    break
        if 'city' in request.keys():
            self.about_user['city'] = request['city']
        else:
            self.write_msg(id, 'Пожалуйста, введите название города')
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    city_name = event.text
                    param_city = {'access_token': token_search, 'country_id': '1',
                                  'q': city_name, 'count': '1', 'v': 5.124}
                    city = requests.get(f'https://api.vk.com/method/database.getCities', params=param_city,
                                        headers=headers).json()['response']['items']
                    self.about_user['city'] = city
                    break
        # self.write_msg(id, 'Отлично, вся необходимая информация получена')
        # print(self.about_user)
        return self.about_user


    def  prefered_ages(self, id):
        self.write_msg(id, "Введи нижний предел возраста")
        self.age_range = []
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.from_user:
                    self.age_range.append(int(event.text))
                    break
        self.write_msg(id, "Введи верхний предел возраста")
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.from_user:
                    self.age_range.append(int(event.text))
                    break
        # print(self.age_range)
        return self.age_range


    def  prefered_sex_choose(self, id):
        self.write_msg(id, "Введи пол парнтера: 1 - ж, 2 - м")
        self.prefered_sex = int()
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.from_user:
                    self.prefered_sex = int(event.text)
                    break
        return self.prefered_sex


    def search_friend(self):
        future_friend_param = {'access_token': token_search, 'is_closed': 'False', 'has_photo': '1', 'count': '10',
                               'hometown': self.about_user['city']['title'], 'age_from': self.age_range[0],
                         'age_to': self.age_range[1], 'sex': self.prefered_sex, 'v': 5.124}
        candidate_list = requests.get(f'https://api.vk.com/method/users.search',
                                      params=future_friend_param, headers=headers).json()['response']['items']
        self.future_friend_list = []
        for people in candidate_list:
            if people['is_closed'] is False:
                self.future_friend_list.append([people['id'], people['last_name'], people['first_name']])
        # print(candidate_list)
        # print(len(self.future_friend_list))
        # print(self.future_friend_list)
        return self.future_friend_list


    def choose_3photo(self, partner_id):
        photo_param = {'access_token': token_search, 'owner_id': partner_id, 'album_id': 'profile',
                       'extended': '1', 'count': '20', 'photo_sizes': '0', 'v': 5.124}
        photo_list_all = requests.get(f'https://api.vk.com/method/photos.get',
                                  params=photo_param, headers=headers).json()['response']
        photo_list = photo_list_all['items']
        self.best_photo = []
        if len(photo_list) >= 3:
            like_count = []
            for photo in photo_list:
                like_count.append(photo['likes']['count'])

            like_count_sorted = sorted(like_count, reverse=True)
            most_likes = like_count_sorted[0:3]
            for photo in photo_list:
                if photo['likes']['count'] in most_likes:
                    self.best_photo.append([photo['id'], photo['likes']['count'], photo['sizes'][-1]['url']])
        else:
            self.best_photo = photo_list
        # print(self.best_photo)
        # print(len(self.best_photo))
        return self.best_photo


    def send_photo(self, your_id, id, photo_id, messages):
        photo_param = {'access_token': token, 'user_id': your_id,
                        'message': messages,
                    'random_id': random.getrandbits(64),'attachment': f'photo{id}_{photo_id}', 'v': 5.124}
        response = requests.get(f'https://api.vk.com/method/messages.send',
                                params=photo_param, headers=headers).json()
        return response


    def friend_or_not(self, main_user, vk_user):
        bot.write_msg(main_user, "Понравился ли тебе кандидат? Напиши да или нет")
        time.sleep(10)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.from_user:
                    if event.text == 'да':
                        friend.append(vk_user)
                        break
                    if event.text == 'нет':
                        black_list.append(vk_user)
                        break


    def choose_partner(self, user_id):
        i = 1
        future_friend_list = self.search_friend()
        for user in future_friend_list:
            bot.write_msg(user_id, f"Высылаю кандидата № {i}")
            list_photo =self.choose_3photo(user[0])
            if len(list_photo) >= 3:
                for photo in  list_photo:
                    self.send_photo(user_id, user[0], photo[0], '')
                    time.sleep(1)
                self.friend_or_not(user_id, user[0])
                # print(friend, black_list)
                i += 1
            else:
                pass
        self.write_msg(user_id, f"Выберите наиболее понравившегоя кандидата. Нажмите число в интервале от 1 до 10")
        number = int()
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.from_user:
                    number = int(event.text)
                    break
        self.best_partner = future_friend_list[number-1]
        # print(self.best_partner)
        return self.best_partner


    def best_partner_age(self):
        best_partner_info = self.user_info(self.best_partner[0])
        self.best_partner_age = best_partner_info['age']
        return self.best_partner_age


    def save_user(self, client_id):
        table_user = User(client_id, self.about_user['first_name'], self.about_user['last_name'], self.about_user['city']['title'])
        session.add(table_user)
        session.commit()
        return table_user


    def save_partner(self, client_id):
        table_datinguser = Partners(self.best_partner[0], self.best_partner[2], self.best_partner[1], self.best_partner_age, client_id)
        session.add(table_datinguser)
        session.commit()
        return table_datinguser


    def photo_save(self):
        best_photo = self.choose_3photo(self.best_partner[0])
        for photo in best_photo:
            table_Photos = Photo(self.best_partner[0], photo[1], photo[2])
            session.add(table_Photos)
        session.commit()
        return "Фотография занесена в базу данных"


if __name__ == '__main__':
    for event in longpoll.listen():
        friend = []
        black_list = []
        bot = Friend_Finder(token, token_search)
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.from_user:
                bot.write_msg(event.user_id, "Привет, давай знакомиться, чтобы помочь найти тебе пару")
                info = bot.user_info(event.user_id)
                bot.write_msg(event.user_id, "Отлично, у нас имеется вся нужная информация для поиска")
                print(info)
                bot.prefered_ages(event.user_id)
                bot.prefered_sex_choose(event.user_id)
                bot.write_msg(event.user_id, "Сейчас начнется поиск партнера")
                best_partner = bot.choose_partner(event.user_id)
                print(bot.best_partner_age())
                bot.save_partner(event.user_id)
                bot.photo_save()
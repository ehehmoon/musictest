import requests

nickname = input('ur nickname: ')
button = input('ur button(only int): ')
url = f'https://v-archive.net/api/archive/{nickname}/tier/{button}'

response = requests.get(url)

if response.status_code != 200:
    print('error!')
else:
    data = response.json()
    tier = data['tier']['name']
    rating = data['tier']['rating']

    print(f"{nickname}'s tier: {tier} - {rating}\n####################\n...and his/her best record: ")


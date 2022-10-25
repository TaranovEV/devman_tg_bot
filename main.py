import argparse
import requests
import telegram
from environs import Env
from requests.exceptions import ConnectionError, ReadTimeout


env = Env()
env.read_env()
TELEGRAM_TOKEN = env.str('TELEGRAM_TOKEN')
DEVMAN_TOKEN = env.str('DEVMAN_TOKEN')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('chat_id',
                        help='id чата, куда бот будет присылать сообщения',
                        type=int)
    args = parser.parse_args()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    params = {}
    url = 'https://dvmn.org/api/long_polling/'
    headers = {
                'Authorization': DEVMAN_TOKEN
            }
    while True:
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            response_json = response.json()
            if response_json['status'] == 'timeout':
                params = {'timestamp': response_json['timestamp_to_request']}
            else:
                params = {'timestamp': response_json['last_attempt_timestamp']}
                attempt = response_json['new_attempts'][0]
                if attempt['is_negative']:
                    decision = 'К сожалению, в работе нашлись ошибки =('
                else:
                    decision = 'Замечаний нет =)'
                text = (
                        f'''Урок "{attempt['lesson_title']}" проверен
                        \n{decision}
                        \nПодробнее: {attempt['lesson_url']}'''
                )

                bot.send_message(text=text, chat_id=args.chat_id)
        except (ReadTimeout, ConnectionError):
            continue


if __name__ in '__main__':
    main()

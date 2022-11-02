import argparse
import requests
import telegram

from textwrap import dedent
from time import sleep
from environs import Env
from requests.exceptions import ConnectionError, ReadTimeout


def main():
    env = Env()
    env.read_env()
    telegram_token = env.str('TELEGRAM_TOKEN')
    devman_token = env.str('DEVMAN_TOKEN')
    parser = argparse.ArgumentParser()
    parser.add_argument('chat_id',
                        help='id чата, куда бот будет присылать сообщения',
                        type=int)
    args = parser.parse_args()
    bot = telegram.Bot(token=telegram_token)
    params = {}
    url = 'https://dvmn.org/api/long_polling/'
    headers = {'Authorization': devman_token}

    while True:
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            review_information = response.json()
            if review_information['status'] == 'timeout':
                params = {'timestamp': review_information['timestamp_to_request']}
            else:
                params = {'timestamp': review_information['last_attempt_timestamp']}
                attempt = review_information['new_attempts'][0]
                if attempt['is_negative']:
                    decision = 'К сожалению, в работе нашлись ошибки =('
                else:
                    decision = 'Замечаний нет =)'
                text = (
                        f'''
                        Урок "{attempt['lesson_title']}" проверен
                        {decision}
                        Подробнее: {attempt['lesson_url']}
                        '''
                )

                bot.send_message(text=dedent(text), chat_id=args.chat_id)
        except (ReadTimeout, ConnectionError):
            sleep(60)
            continue


if __name__ in '__main__':
    main()

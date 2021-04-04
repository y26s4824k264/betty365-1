"""
    Bet365 Web Session Manager
    · Fetch session ID, D_ token, etc.

    Author: @ElJaviLuki
"""
import requests
from html.parser import HTMLParser
from deobfuscator365.d_fetcher import fetch_D_token


def normalize_host_url(host):
    return host[:-1] if host.endswith('/') else host

class WebSessionManager():
    def __init__(self, host : str, userAgent : str):
        self.host = normalize_host_url(host)
        self.userAgent = userAgent
        self.cookies = {}
        self.__main_page = None
        self.__bootjs = None
        self.__sports_configuration = None
        self.__d_token = None

    def __fetch_main_page(self):
        headers = {
            'Connection': 'keep-alive',
            'sec-ch-ua': '^\\^Google',
            'sec-ch-ua-mobile': '?0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.userAgent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            # TODO Make Universal
            'Accept-Language': 'es-ES,es;q=0.9',
        }

        response = requests.get(self.host + '/', headers=headers, cookies=self.cookies)
        self.cookies |= response.cookies
        return response

    def __fetch_sports_configuration(self):
        if self.cookies in [{}, None]:
            # Get main page to fetch cookies
            self.__save_main_page()

        headers = {
            'Connection': 'keep-alive',
            'sec-ch-ua': '^\\^Google',
            'Origin': self.host,
            'sec-ch-ua-mobile': '?0',
            'User-Agent': self.userAgent,
            'Accept': '*/*',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': self.host + '/',
            # TODO Make Universal
            'Accept-Language': 'es-ES,es;q=0.9',
        }

        return requests.get(self.host + '/defaultapi/sports-configuration', headers=headers, cookies=self.cookies)


    def __save_main_page(self):
        response = self.__fetch_main_page()

        self.__main_page = response.text

    def __save_bootjs(self):
        if self.__main_page is None:
            self.__save_main_page()

        class Bet365_HTMLParser(HTMLParser):
            bootjs = ''

            def handle_data(self, data):
                if self.cdata_elem == 'script':
                    self.bootjs = data
                    return

        parser = Bet365_HTMLParser()
        parser.feed(self.__main_page)
        self.__bootjs = parser.bootjs

    def __save_sports_configuration(self):
        response = self.__fetch_sports_configuration()
        self.cookies |= response.cookies

        self.__sports_configuration = response.json()

    def __save_d_token(self):
       self.__d_token = fetch_D_token(self.bootjs())

    def main_page(self):
        if self.__main_page is None:
            self.__save_main_page()

        return self.__main_page

    def bootjs(self):
        if self.__bootjs is None:
            self.__save_bootjs()

        return self.__bootjs

    def sports_configuration(self):
        if self.__sports_configuration is None:
            self.__save_sports_configuration()

        return self.__sports_configuration

    def session_id(self):
        return self.sports_configuration()['flashvars']['SESSION_ID']

    def d_token(self):
        if self.__d_token is None:
            self.__save_d_token()

        return self.__d_token
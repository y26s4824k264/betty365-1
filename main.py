'''
    Fetch session ID and D_ token and use them for the WebSocket connection.
    Author: @ElJaviLuki
'''

# DEPENDENCIES
import asyncio
from betty365 import SubscriptionStreamDataProcessor
from utils.web_session_manager import WebSessionManager


# CONSTANTS
MAIN_PAGE_HOST = 'https://www.bet365.es'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'


sm = WebSessionManager(MAIN_PAGE_HOST, USER_AGENT)
s365 = SubscriptionStreamDataProcessor(sm.session_id(), sm.d_token(), user_agent=USER_AGENT)
asyncio.run(s365.coroutine())
"""
    readit - Port from original JavaScript module 'readit'
    Original JS Authors: Bet365 developers
    Port Author: @ElJaviLuki
"""

class ReaditMessage:
    def __init__(self, type, topic, message, user_headers):
        self.type = type
        self.topic = topic
        self.message = message
        self.user_headers = user_headers


class StandardProtocolConstants():
    RECORD_DELIM = "\x01"
    FIELD_DELIM = "\x02"
    HANDSHAKE_MESSAGE_DELIM = "\x03"
    MESSAGE_DELIM = "\b"
    CLIENT_CONNECT = 0
    CLIENT_POLL = 1
    CLIENT_SEND = 2
    CLIENT_CONNECT_FAST = 3
    INITIAL_TOPIC_LOAD = 20
    DELTA = 21
    CLIENT_SUBSCRIBE = 22
    CLIENT_UNSUBSCRIBE = 23
    CLIENT_SWAP_SUBSCRIPTIONS = 26
    NONE_ENCODING = 0
    ENCRYPTED_ENCODING = 17
    COMPRESSED_ENCODING = 18
    BASE64_ENCODING = 19
    SERVER_PING = 24
    CLIENT_PING = 25
    CLIENT_ABORT = 28
    CLIENT_CLOSE = 29
    ACK_ITL = 30
    ACK_DELTA = 31
    ACK_RESPONSE = 32
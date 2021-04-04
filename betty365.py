"""
    Betty365 - Unofficial Bet365 WebSocket Stream Data Processor
    Author: @ElJaviLuki
"""

# DEPENDENCIES
from random import random
import websockets
from readit import StandardProtocolConstants, ReaditMessage

# Generate URIs
def generate_uid():
    return str(random())[2:]


def generate_premws_uri():
    return 'wss://premws-pt3.365lpodds.com/zap/?uid=' + generate_uid()


def generate_pshudws_uri():
    return 'wss://pshudws.365lpodds.com/zap/?uid=' + generate_uid()


# WebSocket stuff
class WebSocketWrapper:
    def __init__(self, socket, name):
        self.socket = socket
        self.name = name

    async def send(self, message):
        print(f"{self.name} <- {message}")
        await self.socket.send(message)

    async def recv(self):
        message = await self.socket.recv()
        print(f"{self.name} -> {message}")
        return message


class SubscriptionStreamDataProcessor:
    """
        Own implementation of Bet365's WebSocket Stream Data Processor.
        Note that other parts are directly ported from the original JS code.
    """

    def __init__(self, session_id, d_token, *, user_agent):
        self.session_id = session_id
        self.d_token = d_token

        self.user_agent = user_agent

    async def handshake(self):
        """
            Perform a handshake to both 'premws' and 'pshudws' websockets and return their respective responses.

            :return: Handshake response in the format [<premws Handshake Response>, <pshudws Handshake Response>]
        """

        def get_handshake_data(session_id, d_token):
            handshake_data = ""
            handshake_data += chr(SubscriptionStreamDataProcessor.HANDSHAKE_PROTOCOL)
            handshake_data += chr(SubscriptionStreamDataProcessor.HANDSHAKE_VERSION)
            handshake_data += chr(SubscriptionStreamDataProcessor.HANDSHAKE_CONNECTION_TYPE)
            handshake_data += chr(SubscriptionStreamDataProcessor.HANDSHAKE_CAPABILITIES_FLAG)

            # Connection Details - Default Topic '__time'
            handshake_data += "__time" + ","

            handshake_data += "S_" + session_id
            if d_token:
                handshake_data += ",D_" + d_token
            handshake_data += chr(0)

            return handshake_data

        handshake_data = get_handshake_data(self.session_id, self.d_token)
        await self._premws.send(handshake_data)
        await self._pshudws.send(handshake_data)
        return [await self._premws.recv(), await self._pshudws.recv()]

    async def subscribe(self, batches):
        """

            :param batches: Array of topics to subscribe to.
            :return:
        """
        if batches not in [[], None]:
            data = ""
            data += chr(StandardProtocolConstants.CLIENT_SUBSCRIBE)
            data += chr(StandardProtocolConstants.NONE_ENCODING)
            data += ','.join(batches)
            data += StandardProtocolConstants.RECORD_DELIM

            return await self._premws.send(data)

    async def forward_nst(self):
        """
            Read and decrypt NST from 'pshudws' and send it to 'premws'.
            Without this your session will be too short.
            :return:
        """

        def decrypt_nst(data):
            char_map = [
                ["A", "d"],
                ["B", "e"],
                ["C", "f"],
                ["D", "g"],
                ["E", "h"],
                ["F", "i"],
                ["G", "j"],
                ["H", "k"],
                ["I", "l"],
                ["J", "m"],
                ["K", "n"],
                ["L", "o"],
                ["M", "p"],
                ["N", "q"],
                ["O", "r"],
                ["P", "s"],
                ["Q", "t"],
                ["R", "u"],
                ["S", "v"],
                ["T", "w"],
                ["U", "x"],
                ["V", "y"],
                ["W", "z"],
                ["X", "a"],
                ["Y", "b"],
                ["Z", "c"],
                ["a", "Q"],
                ["b", "R"],
                ["c", "S"],
                ["d", "T"],
                ["e", "U"],
                ["f", "V"],
                ["g", "W"],
                ["h", "X"],
                ["i", "Y"],
                ["j", "Z"],
                ["k", "A"],
                ["l", "B"],
                ["m", "C"],
                ["n", "D"],
                ["o", "E"],
                ["p", "F"],
                ["q", "0"],
                ["r", "1"],
                ["s", "2"],
                ["t", "3"],
                ["u", "4"],
                ["v", "5"],
                ["w", "6"],
                ["x", "7"],
                ["y", "8"],
                ["z", "9"],
                ["0", "G"],
                ["1", "H"],
                ["2", "I"],
                ["3", "J"],
                ["4", "K"],
                ["5", "L"],
                ["6", "M"],
                ["7", "N"],
                ["8", "O"],
                ["9", "P"],
                ["\n", ":|~"],
                ["\r", ""]
            ]
            decrypted = ""
            for index in range(0, len(data)):
                new_char = data[index]
                for char_unit in char_map:
                    if ":" == new_char and ":|~" == data[index:index + 3]:
                        new_char = "\n"
                        index += 2
                        break

                    if new_char == char_unit[1]:
                        new_char = char_unit[0]
                        break
                decrypted += new_char
            return decrypted

        def to_readit_msg(data) -> list[ReaditMessage]:
            rd_msgs = []
            if data:
                messages = data.split(StandardProtocolConstants.MESSAGE_DELIM)
                for message in messages:
                    type = ord(message[0])

                    if type in [StandardProtocolConstants.INITIAL_TOPIC_LOAD,
                                StandardProtocolConstants.DELTA]:
                        records = message.split(StandardProtocolConstants.RECORD_DELIM)
                        fields = records[0].split(StandardProtocolConstants.FIELD_DELIM)

                        topic = fields[0][1:]
                        payload = ''.join(records[1:])
                        user_headers = fields[1:]

                        rd_msgs.append(ReaditMessage(str(type), topic, payload, user_headers))
                    elif type in [StandardProtocolConstants.CLIENT_ABORT,
                                  StandardProtocolConstants.CLIENT_CLOSE]:
                        raise (
                                "Connection close/abort message type sent from publisher. Message type: " + str(
                            type))
                    else:
                        raise ("Unrecognised message type sent from publisher: " + str(type))
            return rd_msgs

        async def read_encrypted_nst(socket: WebSocketWrapper):
            while True:
                rd_msgs = to_readit_msg(await socket.recv())
                for rd_msg in rd_msgs:
                    if rd_msg.topic[rd_msg.topic.rfind('_') + 1:] == "D23":
                        return rd_msg.message

        def make_nst_message(decrypted_nst):
            data = ""
            data += chr(StandardProtocolConstants.CLIENT_SEND)
            data += chr(StandardProtocolConstants.NONE_ENCODING)
            data += "command"
            data += StandardProtocolConstants.RECORD_DELIM
            data += "nst" + StandardProtocolConstants.RECORD_DELIM + decrypted_nst + StandardProtocolConstants.FIELD_DELIM + "SPTBK"
            return data

        encrypted_nst = await read_encrypted_nst(self._pshudws)
        decrypted_nst = decrypt_nst(encrypted_nst)
        nst_message = make_nst_message(decrypted_nst)
        await self._premws.send(nst_message)

    async def coroutine(self):
        self._premws = WebSocketWrapper(await websockets.connect(uri=generate_premws_uri(),
                                                                 subprotocols=['zap-protocol-v1'],
                                                                 extra_headers={'User-Agent': self.user_agent}), 'PREMWS')
        self._pshudws = WebSocketWrapper(await websockets.connect(uri=generate_pshudws_uri(),
                                                                  subprotocols=['zap-protocol-v1'],
                                                                  extra_headers={'User-Agent': self.user_agent}), 'PSHUDWS')
        # zap-protocol-v1 Handshake
        await self.handshake()

        # Subscribe to topic(s)
        await self.subscribe(
            [
                'CONFIG_3_0',
                'OVInPlay_3_0'
            ]
        )

        # Decrypt 'pshudws' NST token and forward it to 'premws'
        await self.forward_nst()

        while True:
            recv = await self._premws.recv()
            #TODO Handle data

    TRAILING = "/zap/"
    CONNECTION_TIMEOUT_LIMIT = 15e3
    HANDSHAKE_TIMEOUT_LIMIT = 15e3
    HANDSHAKE_PROTOCOL = 35
    HANDSHAKE_VERSION = 3
    HANDSHAKE_CONNECTION_TYPE = 80
    HANDSHAKE_CAPABILITIES_FLAG = 1
    HANDSHAKE_STATUS_CONNECTED = "100"
    HANDSHAKE_STATUS_REJECTED = "111"

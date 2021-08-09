import asyncio
import signal
import getpass
import argparse
from datetime import datetime

import aioxmpp
from aioxmpp.dispatcher import SimpleMessageDispatcher


class TimeServer:
    language_key = aioxmpp.structs.LanguageTag.fromstr('en')

    def __init__(self, local_jid, password, no_verify=True):
        if type(local_jid) == str:
            self.local_jid = aioxmpp.JID.fromstr(local_jid)
        else:
            self.local_jid = local_jid
        security_layer = aioxmpp.make_security_layer(
            password,
            no_verify=no_verify,
        )
        self.client = aioxmpp.PresenceManagedClient(
            self.local_jid,
            security_layer,
        )
        dispatcher = SimpleMessageDispatcher(self.client)
        dispatcher.register_callback(
            aioxmpp.MessageType.CHAT,
            None,
            self.message_received,
        )

        self.stop_event = asyncio.Event()
        loop = asyncio.get_event_loop()
        loop.add_signal_handler(
            signal.SIGINT,
            self.stop_event.set
        )

        self.customers = []

    def register(self, customer_id):
        self.customers.append(customer_id)

    def unregister(self, customer_id):
        self.customers.remove(customer_id)

    def message_received(self, msg: aioxmpp.Message):
        if msg.type_ != aioxmpp.MessageType.CHAT:
            return

        if not msg.body:
            return

        print(msg.body)

        if msg.body[self.language_key] == 'time':
            self.register(msg.from_)
        elif msg.body[self.language_key] == 'off':
            self.unregister(msg.from_)

    async def say_time(self):
        reply = aioxmpp.Message(
            type_=aioxmpp.MessageType.CHAT,
        )
        while True:
            await asyncio.sleep(1)
            reply.body[None] = datetime.now().__str__()
            for customer in self.customers:
                reply.to = customer
                self.client.enqueue(reply)

    async def run(self):
        async with self.client.connected():
            asyncio.create_task(self.say_time())
            await self.stop_event.wait()

    @staticmethod
    def jid(s):
        return aioxmpp.JID.fromstr(s)


def main() -> None:
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument(
        "-j", "--local-jid",
        type=TimeServer.jid,
        help="JID to authenticate with (only required if not in config)"
    )
    arg_parse.add_argument(
            "-p", "--password",
            type=str,
            help="password",
        )
    args = arg_parse.parse_args()
    time_server = TimeServer(args.local_jid, args.password)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(time_server.run())
    finally:
        loop.close()


if __name__ == '__main__':
    main()


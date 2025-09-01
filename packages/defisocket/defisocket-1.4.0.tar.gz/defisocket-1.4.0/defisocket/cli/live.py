import asyncio
import json
from dataclasses import asdict
import os
import logging
from defisocket.event_stream import LiveEventStream
from defisocket.block_stream import LiveBlockStream

from dotenv import load_dotenv

from defisocket.models import Substream

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if logger.hasHandlers(): logger.handlers.clear()
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
logger.addHandler(handler)
logger.propagate = False

if __name__ == '__main__':
    load_dotenv()
    import argparse

    async def main():

        DEFISOCKET_URL= os.getenv('DEFISOCKET_URL')
        if not DEFISOCKET_URL:
            error = 'Please set DEFISOCKET_URL in .env file'
            logger.error(error)
            raise Exception(error)

        parser = argparse.ArgumentParser(description='Historical Stream Management')

        command = parser.add_subparsers(dest='command')

        create_parser = command.add_parser('create', help='Create a new historical stream')
        create_parser.add_argument('-name', type=str, required=True, help='Name of the historical stream to create')
        create_parser.add_argument('-networks', type=str, nargs='+', required=True, help='Networks for the historical stream (e.g., ETH BSC)')
        create_parser.add_argument('-event-name', type=str, required=True, help='Event name for the historical stream (e.g., erc_20_all_events)')
        create_parser.add_argument('-client-name', type=str, required=True, help='Client name for the historical stream (e.g., erc20)')
        create_parser.add_argument('-listen', action="store_true", help='Wait for the stream to finish before returning')
        create_parser.add_argument('-timeout', type=int, help='Timeout for listening to the stream (in seconds, default is 60)', default=60, required=False)
        create_parser.add_argument('-extra-args', type=str, default='{}', help='Extra arguments for the substream in JSON format (e.g., \'{"tokens": ["USDT", "USDC"], "exclude_zero_transfers": true}\')')

        listen_parser = command.add_parser('listen', help='Listen on a running stream')
        listen_parser.add_argument('-name', type=str, required=True, help='Name of the historical stream to get listen to')
        listen_parser.add_argument('-timeout', type=int, help='Timeout for listening to the stream (in seconds, default is 60)', default=60, required=False)

        block_listen_parser = command.add_parser('listen_block', help='Listen on a running block stream')
        block_listen_parser.add_argument('-network', type=str, required=True, help='Name of the network whose block we want to list')
        block_listen_parser.add_argument('-timeout', type=int, help='Timeout for listening to the block stream (in seconds, default is 60)', default=60, required=False)

        running_parser = command.add_parser('running', help='Get whether a historical stream is running or not')
        running_parser.add_argument('-name', type=str, required=True, help='Name of the historical stream to get running status for')

        stop_parser = command.add_parser('stop', help='Stop a historical stream')
        stop_parser.add_argument('-name', type=str, required=True, help='Name of the historical stream to stop')

        args = parser.parse_args()
        logger.info(args)

        async def callback(data: str):
            """
            Callback function to handle incoming data.
            """
            logger.info(f"Received data: {data}")

        if args.command == 'create':
            networks = args.networks
            listen = args.listen
            print(listen)

            extra_args = json.loads(args.extra_args)


            substream = Substream(
                client_name=args.client_name,
                name=args.event_name,
                networks=networks,
                extra_args=extra_args
            )

            logger.info(f"Creating live stream: {args.name} with networks {networks}")
            logger.info(asdict(substream))

            stream = LiveEventStream(name=args.name, server_address=DEFISOCKET_URL)
            if listen:
                timeout = args.timeout
                res = await stream.start_and_listen(substream=substream, callback=callback, timeout=timeout)
            else:
                res = stream.start(substream=substream)
            logger.info(res)

        elif args.command == 'listen':
            timeout = args.timeout
            print(timeout)
            stream = LiveEventStream(name=args.name, server_address=DEFISOCKET_URL)
            await stream.listen(callback, timeout)

        elif args.command == 'listen_block':
            network = args.network
            block_stream = LiveBlockStream(network, DEFISOCKET_URL)
            await block_stream.listen(callback)

        elif args.command == 'running':
            stream = LiveEventStream(name=args.name, server_address=DEFISOCKET_URL)
            res = stream.is_running()
            logger.info(res)

        elif args.command == 'stop':
            stream = LiveEventStream(name=args.name, server_address=DEFISOCKET_URL)
            res = stream.stop()
            logger.info(res)

    asyncio.run(main())

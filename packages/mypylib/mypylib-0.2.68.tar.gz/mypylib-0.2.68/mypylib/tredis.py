import redis
import threading
import json
import math
from loguru import logger
import traceback
from time import sleep
from typing import Union
import queue


class redis_channel:
    RAYIN_ORDER_CHANNEL_TEST = 'RAYIN_ORDER_CHANNEL_TEST'
    RAYIN_ORDER_CHANNEL_FORMAL = 'RAYIN_ORDER_CHANNEL_FORMAL'


class base_tredis_msg_sender:
    def __init__(self, tredis=None):
        self.tredis: Tredis = tredis

    def redis_msg_sender(self, channel, data):
        logger.info(f'This is what I got: {data} from {channel}')
        if self.tredis is not None and self.tredis.r is not None:
            ret = self.tredis.r.get(str(data))
            if ret is not None:
                logger.info(f'This is what I have found {ret} {type(ret)}')
                return ret
            else:
                logger.info(f'Cannot find {data} on server')
        return None


class Tredis_publish(threading.Thread):
    CONTROL_CHANNEL = '__tredis_control__'

    def __init__(self,
                 server='localhost',
                 port=6379,
                 db=0,
                 password=''):
        threading.Thread.__init__(self)
        self.server = server
        self.port = port
        self.db = db
        self.password = password
        self.queue_publish = queue.Queue()
        self._stop_event = threading.Event()
        
        # Initialize Redis with timeouts
        self.r = redis.StrictRedis(host=self.server,
                                 port=self.port,
                                 db=self.db,
                                 charset="utf-8",
                                 decode_responses=True,
                                 password=self.password,
                                 socket_connect_timeout=30,
                                 socket_timeout=30)
        self.start()

    def run(self):
        retry_count = 0
        max_retries = 5
        base_delay = 0.1

        while not self._stop_event.is_set():
            try:
                messages_to_process = []
                for _ in range(100):  # Process up to 100 messages
                    try:
                        channel, message = self.queue_publish.get(timeout=0.1)
                        messages_to_process.append((channel, message))
                    except queue.Empty:
                        break

                if messages_to_process:
                    with self.r.pipeline() as pipe:
                        for channel, message in messages_to_process:
                            pipe.publish(channel, message)
                        pipe.execute()
                    
                    for _ in messages_to_process:
                        self.queue_publish.task_done()

                retry_count = 0
                sleep(0.01)

            except Exception as e:
                retry_count += 1
                if retry_count > max_retries:
                    logger.error(f"Max retries ({max_retries}) exceeded in Tredis_publish: {e}")
                    break
                delay = min(base_delay * (2 ** (retry_count - 1)), 5.0)
                logger.exception(f"Error in Tredis_publish (retry {retry_count}/{max_retries} after {delay}s): {e}")
                sleep(delay)

        # Cleanup
        try:
            if self.r:
                logger.info(f"Closing Redis connection in Tredis_publish")
                self.r.close()
        except Exception as e:
            logger.exception(f'Error during cleanup: {e}')

    def publish(self, channel, message):
        self.queue_publish.put((channel, message), block=True)

    def stop(self):
        if not self._stop_event.is_set():
            self._stop_event.set()
            control_msg = json.dumps({'action': 'stop', 'thread': 'publish', 'id': str(self)})
            try:
                self.r.publish(self.CONTROL_CHANNEL, control_msg)
            except Exception as e:
                logger.warning(f"Failed to publish stop message in Tredis_publish: {e}")


class Tredis_subscribe(threading.Thread):
    CONTROL_CHANNEL = '__tredis_control__'

    def __init__(self,
                 server='localhost',
                 port=6379,
                 db=0,
                 password='',
                 channel='test',
                 prefix='test',
                 redis_msg_sender=base_tredis_msg_sender()):
        threading.Thread.__init__(self)
        self.server = server
        self.port = port
        self.db = db
        self.password = password
        self.channel = channel
        self.prefix = prefix
        self.redis_msg_sender = redis_msg_sender
        self.message_queue = queue.Queue(maxsize=10000)
        
        # Initialize Redis with timeouts
        self.r = redis.StrictRedis(
            host=self.server,
            port=self.port,
            db=self.db,
            charset="utf-8",
            decode_responses=True,
            password=self.password,
            socket_keepalive=True,
            socket_connect_timeout=30,
            socket_timeout=30,
            health_check_interval=30
        )

        logger.info(f'Redis connected to {self.server}, port {self.port}, db: {self.db}')
        self.sub = self.r.pubsub(ignore_subscribe_messages=True)
        logger.info(f'Redis subscribe to channel [{self.channel}]')
        
        # Subscribe to channels
        self.sub.subscribe(self.channel)
        self.sub.subscribe(self.CONTROL_CHANNEL)
        
        self._stop_event = threading.Event()
        self._stopped = False  # Flag to prevent redundant stops
        
        # Start message processing thread
        self._processor_thread = threading.Thread(target=self._process_messages, daemon=True)
        self._processor_thread.start()
        self.start()

    def _process_messages(self):
        while not self._stop_event.is_set():
            try:
                channel, data = self.message_queue.get(timeout=0.1)
                function_send = getattr(self.redis_msg_sender, 'redis_msg_sender', None)
                if function_send is not None and callable(function_send):
                    function_send(channel, data)
                self.message_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                if not self._stop_event.is_set():
                    logger.exception(f'Error processing message: {e}')

    def run(self):
        retry_count = 0
        max_retries = 5
        base_delay = 0.1

        while not self._stop_event.is_set():
            try:
                messages = self.sub.get_message(timeout=0.1)
                if messages:
                    channel = messages['channel']
                    data = messages['data']

                    if channel == self.CONTROL_CHANNEL:
                        try:
                            control_msg = json.loads(data)
                            if (control_msg.get('action') == 'stop' and 
                                control_msg.get('thread') == 'subscribe' and 
                                control_msg.get('id') == str(self)):
                                logger.info(f'{self} to exit')
                                self._stop_event.set()
                                break
                        except json.JSONDecodeError:
                            logger.warning(f'Invalid control message: {data}')
                            continue

                    try:
                        self.message_queue.put((channel, data), timeout=1.0)
                    except queue.Full:
                        logger.warning(f'Message queue full, dropping message: {data}')

                retry_count = 0
                sleep(0.01)

            except Exception as e:
                retry_count += 1
                if retry_count > max_retries:
                    logger.error(f"Max retries ({max_retries}) exceeded in Tredis_subscribe: {e}")
                    self._stop_event.set()
                    break
                delay = min(base_delay * (2 ** ( retry_count - 1)), 5.0)
                logger.exception(f"Redis subscribe error (retry {retry_count}/{max_retries} after {delay}s): {e}")
                sleep(delay)

        # Cleanup
        self._stopped = True
        try:
            if self.sub:
                logger.info(f"Unsubscribing and closing pubsub in Tredis_subscribe")
                self.sub.unsubscribe()
                self.sub.close()
            if self.r:
                logger.info(f"Closing Redis connection in Tredis_subscribe")
                self.r.close()
        except Exception as e:
            logger.exception(f'Error during cleanup: {e}')

    def subscribe(self, channel):
        if not self._stop_event.is_set():
            logger.info(f'Redis subscribe to extra channel [{channel}]')
            self.sub.subscribe(channel)

    @logger.catch()
    def stop(self):
        if not self._stopped and not self._stop_event.is_set():
            control_msg = json.dumps({'action': 'stop', 'thread': 'subscribe', 'id': str(self)})
            try:
                if self.r and self.channel:
                    self.r.publish(self.CONTROL_CHANNEL, control_msg)
            except Exception as e:
                logger.warning(f"Failed to publish stop message in Tredis_subscribe: {e}")
            self._stop_event.set()


class Tredis:
    default_port = 6379
    default_db = 0

    def __init__(self,
                 server='localhost',
                 port=6379,
                 db=0,
                 password='',
                 channel='test',
                 prefix='test',
                 redis_msg_sender=base_tredis_msg_sender()):
        self.tredis_subscribe = Tredis_subscribe(server, port, db, password, channel, prefix, redis_msg_sender)
        self.tredis_publish = Tredis_publish(server, port, db, password)
        self.r = self.tredis_publish.r

    def subscribe(self, channel):
        self.tredis_subscribe.subscribe(channel)

    def publish(self, channel, message):
        self.tredis_publish.publish(channel, message)

    def stop(self):
        self.tredis_subscribe.stop()
        self.tredis_publish.stop()

    def join(self):
        self.tredis_subscribe.join()
        self.tredis_publish.join()


if __name__ == '__main__':

    class warrant_channel:
       ALL = 'WARRANT_ALL'
       DEALER = 'WARRANT_DEALER'
       LARGE_VOLUME = 'WARRANT_LARGE_VOLUME'
       BURST = 'WARRANT_BURST'
 
       AMOUNT_STOCK_AND_WARRANT = 'AMOUNT_STOCK_AND_WARRANT'
       AMOUNT_WARRANT = 'AMOUNT_WARRANT'
       AMOUNT_STOCK = 'AMOUNT_STOCK'


    sender = base_tredis_msg_sender()

    tredis = Tredis(server='livewithjoyday.com',
                    port=Tredis.default_port,
                    db=Tredis.default_db,
                    password='5k4g4redisau4a83',
                    channel='warrant_command',
                    prefix='warrant',
                    redis_msg_sender=sender)
    tredis_shioaji = Tredis(server='localhost',
                            port=Tredis.default_port,
                            db=Tredis.default_db,
                            password='',
                            channel='shioaji_wrapper',
                            prefix='shioaji',
                            redis_msg_sender=sender)

    tredis.subscribe(warrant_channel.ALL)
    tredis.subscribe(warrant_channel.DEALER)
    tredis.subscribe(warrant_channel.LARGE_VOLUME)
    tredis.subscribe(warrant_channel.BURST)

    tredis.publish(warrant_channel.ALL, warrant_channel.ALL)
    tredis_shioaji.publish(warrant_channel.ALL, warrant_channel.ALL + ' tredis_shioaji')
    tredis.publish(warrant_channel.DEALER, warrant_channel.DEALER)
    tredis_shioaji.publish(warrant_channel.DEALER, warrant_channel.DEALER + ' tredis_shioaji')
    tredis.publish(warrant_channel.LARGE_VOLUME, warrant_channel.LARGE_VOLUME)
    tredis_shioaji.publish(warrant_channel.LARGE_VOLUME, warrant_channel.LARGE_VOLUME + ' tredis_shioaji')
    tredis.publish(warrant_channel.BURST, warrant_channel.BURST)
    tredis_shioaji.publish(warrant_channel.BURST, warrant_channel.BURST + ' tredis_shioaji')

    index = 0
    while True:
        try:
            sleep(1)
            index += 1
            if index == 3:
                break
        except KeyboardInterrupt:
            break

    tredis_shioaji.stop()
    tredis.stop()


import threading
import queue
import os
from playsound import playsound
from loguru import logger
import datetime
from collections import defaultdict


if os.name == 'nt':
    import winsound

_MYPYLIB_ROOT = os.path.abspath(os.path.dirname(__file__))

class tplaysound(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

        self.time_block = 2

        self.queue = queue.Queue()
        self.queue.maxsize = 2


        self.file_sound_alert = f'{_MYPYLIB_ROOT}/../data/alert.wav'

        self.start()

        self.dict_filename_to_datetime = defaultdict(datetime.datetime.now)

    def block_or_not(self, filename):
        return (datetime.datetime.now() - self.dict_filename_to_datetime[filename]).seconds < self.time_block

    def play(self, filename=None):
        self.play_file(filename=filename)

    def play_file(self, filename=None):
        if filename is None:
            filename = self.file_sound_alert

        if self.block_or_not(filename):
            return

        command = ('play', filename)
        try:
            self.queue.put(command, False)
        except queue.Full:
            pass
        # print(f'send command {command}')

    def run(self):
        while True:
            try:
                (cmd, arg) = self.queue.get(timeout=1)
            except queue.Empty:
                pass
            else:
                if cmd == 'stop':
                    break

                if cmd == 'play':
                    # print('got Play')
                    if not os.path.isfile(arg):
                        logger.error(f'{arg} does not exist.')
                    else:

                        try:
                            if os.name == 'nt':
                                # print('NT play')
                                winsound.PlaySound(arg, winsound.SND_FILENAME)
                            else:
                                # print('POSIX play')
                                playsound(arg)
                        except Exception as e:
                            logger.error(e)
                            logger.error(f'Somehow play {arg} error...')

    def stop(self):
        self.queue.put(('stop', 'stop'))



if __name__ == '__main__':
    from time import sleep


    tps = tplaysound()
    index = 0
    while True:
        tps.play_file()
        tps.play_file()
        tps.play_file()
        tps.play_file()
        sleep(3)
        index += 1
        if index == 3:
            break
    tps.stop()
    tps.join()

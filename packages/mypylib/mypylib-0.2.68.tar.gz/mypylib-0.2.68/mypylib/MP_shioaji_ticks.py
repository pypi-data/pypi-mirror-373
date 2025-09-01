import multiprocessing as mp
from time import sleep
import queue
import os


class base_parameter:
    def __init__(self):
        self.dir_shioaji_ticks = ''


class MP_queue:
    def __init__(self):
        self.queue_in: mp.Queue = mp.Queue()
        self.queue_out: mp.Queue = mp.Queue()
        self.queue_debug: mp.Queue = mp.Queue()


class MP_mother(object):

    def __init__(self, mp_queue: MP_queue, parameters: base_parameter):
        self.mp_queue: MP_queue = mp_queue
        self.parameters: base_parameter = parameters
        self.list_out = []
        self.list_out_debug = []

    def do_something(self, index):
        sleep(0.2)
        self.mp_queue.queue_debug.put(f'This is process {index}, {self}')

    @staticmethod
    def load_all_files(dir_source):
        all_files = []
        for d in os.listdir(dir_source):
            if not os.path.isdir(f'{dir_source}/{d}'):
                continue
            if d[0] == '.':
                continue
            if not d[0] in '1234567890':
                continue
            for f in os.listdir(f'{dir_source}/{d}'):
                if not f.startswith('20'):
                    continue
                full_path = f'{d} {dir_source}/{d}/{f}'
                all_files.append(full_path)
        return all_files


    def run(self):
        all_files = self.load_all_files(dir_source=self.parameters.dir_shioaji_ticks)
        print(f'There are {len(all_files)} files.')
        for file in all_files:
            self.mp_queue.queue_in.put(file)
        print('All file queued')

        processes = []
        for i in range(mp.cpu_count()):
            p = mp.Process(target=self.do_something, args=(i,))
            processes.append(p)

        [x.start() for x in processes]

        [x.join() for x in processes]

        while True:
            try:
                out = self.mp_queue.queue_debug.get(block=True, timeout=0)
                self.list_out_debug.append(out)
            except queue.Empty:
                break

        while True:
            try:
                out = self.mp_queue.queue_out.get(block=True, timeout=0)
                self.list_out.append(out)
            except queue.Empty:
                break


# class user_parameters(base_parameter):
#     def __init__(self):
#         super(user_parameters, self).__init__()
#         self.dir_shioaji_ticks = '../../shioaji_ticks'
#
#
#
# class ML_user(MP_mother):
#     def __init__(self, mp_queue: MP_queue, parameters: base_parameter):
#         super(ML_user, self).__init__(mp_queue, parameters)
#
#
#
#     def do_something(self, index):
#         super(ML_user, self).do_something(index)
#
#         while True:
#             try:
#                 file = self.mp_queue.queue_in.get(block=True, timeout=0)
#
#                 self.mp_queue.queue_out.put((index, file))
#
#             except queue.Empty:
#                 break
#
#
# if __name__ == '__main__':
#
#     mp_queue = MP_queue()
#
#     mpm = ML_user(mp_queue, parameters=user_parameters())
#     mpm.run()
#
#     for x in mpm.list_out_debug:
#         print(f'list debug: {x}')
#
#     for x in mpm.list_out:
#         print(f'list out: {x}')
#
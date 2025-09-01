
# Refer to this page:
# https://huichen-cs.github.io/course/CISC7334X/20FA/lecture/pymcast/#the-receiver-program-mcastrecvpy

import asyncio
import socket
import struct
import select

class metadata_t:
    def __init__(self, name, IP_local, IP_multicast, port, callback):
        self.name = name
        self.IP_local = IP_local
        self.IP_multicast = IP_multicast
        self.port = port
        self.callback = callback

def stock_quote_unpacker(data, len, arg, tv):
    pass

def future_quote_parser(data, len, arg, tv):
    pass

data_mapping = [
    metadata_t("TSE 股票即時行情及證券基本料", "10.71.17.74", "224.0.100.100", 10000, stock_quote_unpacker),
    metadata_t("TSE 權證即時行情及證券基本料", "10.71.17.74", "224.2.100.100", 10002, stock_quote_unpacker),
    metadata_t("TSE 股票5秒行情快照及證券基本料", "10.71.17.74", "224.4.100.100", 10004, stock_quote_unpacker),
    metadata_t("TSE 其它資訊(統計、公告類資訊)", "10.71.17.74", "224.6.100.100", 10006, stock_quote_unpacker),
    metadata_t("TSE 盤中零股即時行情及盤中零股證券基本資料", "10.71.17.74", "224.8.100.100", 10008, stock_quote_unpacker),
    metadata_t("OTC 股票即時行情及證券基本料", "10.71.17.74", "224.0.30.30", 3000, stock_quote_unpacker),
    metadata_t("權證即時行情及證券基本料", "10.71.17.74", "224.2.30.30", 3002, stock_quote_unpacker),
    metadata_t("股票5秒行情快照及證券基本料", "10.71.17.74", "224.4.30.30", 3004, stock_quote_unpacker),
    metadata_t("其它資訊(統計、公告類資訊)", "10.71.17.74", "224.6.30.30", 3006, stock_quote_unpacker),
    metadata_t("盤中零股即時行情及盤中零股證券基本資料", "10.71.17.74", "224.8.30.30", 3008, stock_quote_unpacker),
    metadata_t("一般交易選擇權資訊", "10.71.17.74", "225.0.30.30", 3000, future_quote_parser),
    metadata_t("Night 一般交易選擇權資訊", "10.71.17.74", "225.10.30.30", 3000, future_quote_parser)
]


meta: metadata_t

list_read = []

for meta in data_mapping:
    receiver = socket.socket(family=socket.AF_INET,
                             type=socket.SOCK_DGRAM,
                             proto=socket.IPPROTO_UDP,
                             fileno=None)

    receiver.setblocking(False)
    receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    bindaddr = (meta.IP_multicast, meta.port)
    receiver.bind(bindaddr)


    mreq = struct.pack("=4s4s",
                       socket.inet_aton(meta.IP_multicast),
                       socket.inet_aton(meta.IP_local))

    receiver.setsockopt(socket.IPPROTO_IP,
                        socket.IP_ADD_MEMBERSHIP,
                        mreq)

    list_read.append(receiver)

    print(meta.name)

while True:

    readable, _, _ = select.select(list_read, [], [], 0)

    for sck in readable:
        buf, sender_addr = sck.recvfrom(1024)
        # msg = buf.decode()


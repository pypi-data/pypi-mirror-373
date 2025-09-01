import os
import ctypes
import sys
import json

# Load the shared library
lib_path = os.path.join(os.path.dirname(__file__), 'libquote_module.so')
quote_module = ctypes.CDLL(lib_path)

class QuoteS(ctypes.Structure):
    _fields_ = [
        ("code_str", ctypes.c_char * 8),
        ("timestamp_str", ctypes.c_char * 32),
        ("close_price", ctypes.c_double),
        ("bool_close", ctypes.c_int),
        ("close_volume", ctypes.c_int),
        ("volume_acc", ctypes.c_int),
        ("ask_price", ctypes.c_double * 5),
        ("ask_volume", ctypes.c_int * 5),
        ("bid_price", ctypes.c_double * 5),
        ("bid_volume", ctypes.c_int * 5),
        ("bool_continue", ctypes.c_int),
        ("bool_bid_price", ctypes.c_int),
        ("bool_ask_price", ctypes.c_int),
        ("bool_odd", ctypes.c_int),
        ("number_best_ask", ctypes.c_int),
        ("number_best_bid", ctypes.c_int),
        ("tick_type", ctypes.c_int),
        ("bool_simtrade", ctypes.c_int),
    ]


multicast_source_mapping = [
    {
        "description": "TSE 股票即時行情及證券基本料",
        "multicast_address": "224.0.100.100",
        "port": 10000,
    },
    {
        "description": "TSE 權證即時行情及證券基本料",
        "multicast_address": "224.2.100.100",
        "port": 10002,
    },
    {
        "description": "TSE 股票5秒行情快照及證券基本料",
        "multicast_address": "224.4.100.100",
        "port": 10004,
    },
    {
        "description": "TSE 其它資訊(統計、公告類資訊)",
        "multicast_address": "224.6.100.100",
        "port": 10006,
    },
    {
        "description": "TSE 盤中零股即時行情及盤中零股證券基本資料",
        "multicast_address": "224.8.100.100",
        "port": 10008,
    },
    {
        "description": "OTC 股票即時行情及證券基本料",
        "multicast_address": "224.0.30.30",
        "port": 3000,
    },
    {
        "description": "OTC 權證即時行情及證券基本料",
        "multicast_address": "224.2.30.30",
        "port": 3002,
    },
    {
        "description": "OTC 股票5秒行情快照及證券基本料",
        "multicast_address": "224.4.30.30",
        "port": 3004,
    },
    {
        "description": "OTC 其它資訊(統計、公告類資訊)",
        "multicast_address": "224.6.30.30",
        "port": 3006,
    },
    {
        "description": "OTC 盤中零股即時行情及盤中零股證券基本資料",
        "multicast_address": "224.8.30.30",
        "port": 3008,
    },
    {
        "description": "FUT 一般交易選擇權資訊",
        "multicast_address": "225.0.30.30",
        "port": 3000,
    },
    {
        "description": "FUT 夜盤一般交易選擇權資訊",
        "multicast_address": "225.10.30.30",
        "port": 3000,
    },
]


CALLBACK_TYPE = ctypes.CFUNCTYPE(None, ctypes.POINTER(QuoteS))

#########################################
# Multicast quote reader 
#########################################

py_mc_live_pcap_callback = None

INTERFACE_IP_TSE = '10.175.2.17'    # COLO TSE
INTERFACE_IP_OTC = '10.175.1.17'    # COLO OTC
INTERFACE_IP_FUT = '10.71.17.74'    # 4 In 1

def py_mc_live_pcap_callback_wrapper(quote_ptr):
    if py_mc_live_pcap_callback:
        quote = quote_ptr.contents
        py_mc_live_pcap_callback(quote)

c_mc_live_pcap_callback = CALLBACK_TYPE(py_mc_live_pcap_callback_wrapper)

quote_module.start_mc_live_pcap_read.argtypes = [ctypes.c_char_p]
quote_module.stop_mc_live_pcap_read.argtypes = []
quote_module.set_mc_live_pcap_callback.argtypes = [CALLBACK_TYPE]

def set_mc_live_pcap_callback(callback):
    global py_mc_live_pcap_callback
    py_mc_live_pcap_callback = callback
    quote_module.set_mc_live_pcap_callback(c_mc_live_pcap_callback)

def start_mc_live_pcap_read(mapping=multicast_source_mapping):
    source: dict
    for source in multicast_source_mapping:
        if source['description'].startswith('TSE'):
            source['interface'] = INTERFACE_IP_TSE
        elif source['description'].startswith('OTC'):
            source['interface'] = INTERFACE_IP_OTC
        if source['description'].startswith('FUT'):
            source['interface'] = INTERFACE_IP_FUT

    quote_module.start_mc_live_pcap_read(ctypes.c_char_p(json.dumps(multicast_source_mapping).encode('utf-8')))

def stop_mc_live_pcap_read():
    quote_module.stop_mc_live_pcap_read()


#########################################
# Offline pcap reader 
#########################################
py_offline_pcap_callback = None

def py_offline_pcap_callback_wrapper(quote_ptr):
    if py_offline_pcap_callback:
        quote = quote_ptr.contents
        py_offline_pcap_callback(quote)

c_offline_pcap_callback = CALLBACK_TYPE(py_offline_pcap_callback_wrapper)

quote_module.start_offline_pcap_read.argtypes = [ctypes.c_char_p]
quote_module.stop_offline_pcap_read.argtypes = []
quote_module.set_offline_pcap_callback.argtypes = [CALLBACK_TYPE]

def set_offline_pcap_callback(callback):
    global py_offline_pcap_callback
    py_offline_pcap_callback = callback
    quote_module.set_offline_pcap_callback(c_offline_pcap_callback)

def start_offline_pcap_read(path_pcap):
    quote_module.start_offline_pcap_read(ctypes.c_char_p(path_pcap.encode('utf-8')))

def stop_offline_pcap_read():
    quote_module.stop_offline_pcap_read()

#########################################
# Dummy
#########################################
py_callback = None

def py_callback_wrapper(value):
    if py_callback:
        py_callback(value.decode('utf-8'))

c_callback = CALLBACK_TYPE(py_callback_wrapper)

quote_module.start_thread.argtypes = []
quote_module.stop_thread.argtypes = []
quote_module.set_callback.argtypes = [CALLBACK_TYPE]

def set_callback(callback):
    global py_callback
    py_callback = callback
    quote_module.set_callback(c_callback)

def start():
    quote_module.start_thread()

def stop():
    quote_module.stop_thread()

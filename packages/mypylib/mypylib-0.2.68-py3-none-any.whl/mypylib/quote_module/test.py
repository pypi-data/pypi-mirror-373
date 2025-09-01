
import datetime
import time
import mypylib.quote_module as qm
from mypylib.quote_module import QuoteS

def callback_pcap_read(quote: QuoteS):
    pass
    print(f'Symbol: {quote.code_str.decode()} {quote.close_price}')

if True:
    qm.INTERFACE_IP_TSE = '10.175.2.17' 
    qm.INTERFACE_IP_OTC = '10.175.1.17' 
    qm.INTERFACE_IP_FUT = '10.71.17.74'
    qm.set_mc_live_pcap_callback(callback_pcap_read)
    qm.start_mc_live_pcap_read()


if True:
    qm.set_offline_pcap_callback(callback_pcap_read)
    qm.start_offline_pcap_read('/home/william/ken/UDP/tcpdump/TSE-2024-06-07-08-25.pcap')

while True:
    time.sleep(1)
    print(datetime.datetime.now())

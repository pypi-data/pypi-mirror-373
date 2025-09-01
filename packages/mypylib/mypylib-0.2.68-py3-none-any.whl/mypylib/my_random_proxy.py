from random import randrange

from proxy_randomizer import RegisteredProviders
rp = RegisteredProviders()
rp.parse_providers()
list_proxy = list(rp.proxies)

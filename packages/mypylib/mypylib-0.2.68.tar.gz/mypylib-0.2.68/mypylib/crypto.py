
skip_list_quote_forex = ["法幣", "AUD", "BIDR", "BRL", "EUR", "GBP", "RUB", "TRY", "UAH", "VAI", "IDRT" ,"NGN"]
skip_list_base_stable = ["穩定幣", "DAI", "TUSD", "USDC", "USDT", "BUSD", "TUSD", "USDP"]
skip_list_base_goods = ["金融商品", "PAXG", "TUSD", "USDC", "USDT", "BUSD", "TUSD", "USDP"]

class Base_Quote_parser:
    list_quote = ['AUD', 'BIDR', 'BNB', 'BRL', 'BTC', 'BUSD', 'DAI', 'DOGE',
                  'DOT', 'ETH', 'EUR', 'GBP', 'IDRT', 'NGN', 'RUB', 'TRX',
                  'TRY', 'TUSD', 'UAH', 'USDC', 'USDP', 'USDT', 'VAI', 'XRP']

    def __init__(self):
        self.cache: dict = {}

    def split(self, base_on_quote):
        base = quote = None
        if self.cache.get(base_on_quote, None) is None:
            for quote in Base_Quote_parser.list_quote:
                if base_on_quote.endswith(quote):
                    base = base_on_quote[:-len(quote)]
                    self.cache[base_on_quote] = (base, quote)
                    break
        else:
            base, quote = self.cache.get(base_on_quote)

        return base, quote


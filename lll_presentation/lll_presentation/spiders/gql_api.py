import scrapy
import json
from time import sleep


class GqlApiSpider(scrapy.Spider):
    name = 'gql_api'
    allowed_domains = ['shop.lululemon.com']
    start_urls = ['https://shop.lululemon.com/']

    headers = {
    'Host': 'shop.lululemon.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Referer': 'https://shop.lululemon.com/p/men-joggers/Abc-Jogger/_/prod8530240?color=50878',
    'Content-Type': 'application/json',
    'Origin': 'https://shop.lululemon.com',
    'Dnt': '1',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Te': 'trailers'}

    cookies = {'ltmo':'1', 'UsrLocale':'en_US', 'Country':'US'}

    def start_requests(self):
        with open('/home/guid/Work/lll_presentation/lll_presentation/lll_presentation/data_inputs/gql_sku_list.txt', 'r') as f:
            skus = f.readlines()
            end = round(len(skus),-3)
            start = 0

        while start < end: 
            sku_list = skus[start:start+500]
            payload = {"query":"query GetInventoryDetails($productId: String!, $skus: [String!]!) {\n  inventoryDetails(productId: $productId, skus: $skus) {\n    sku {\n      id\n      available\n      isLowStock\n      lowStockMessage\n      __typename\n    }\n    __typename\n  }\n}\n","operationName":"GetInventoryDetails","variables":{"productId":"prod10720035","skus":f"{sku_list}"}}

            gql = GqlApiSpider.start_urls[0] + "cne/graphql"
            yield scrapy.http.JsonRequest(url=gql, headers=GqlApiSpider.headers, cookies=GqlApiSpider.cookies, data=payload)
            start += 500
            sleep(3)
            
    def parse(self, response):
        yield response.json()
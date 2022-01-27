import scrapy
from lll_presentation.items import LllPresentationItem
import json


product = LllPresentationItem() 
detail_skuList = open('/home/guid/Work/lll_presentation/lll_presentation/lll_presentation/data_collected/gql_sku_list.txt', 'w')
counts = open('/home/guid/Work/lll_presentation/lll_presentation/lll_presentation/data_collected/cat_counts.txt', 'w')


class JsonApiSpider(scrapy.Spider):
    name = 'json_api'
    allowed_domains = ['lululemon.com']
    start_urls = ['https://shop.lululemon.com/api/c/women/_/N-7vf',
    'https://shop.lululemon.com/api/c/men/_/N-7tu',
    'https://shop.lululemon.com/api/c/accessories/_/N-8pb',
    'https://shop.lululemon.com/api/c/sale/_/N-8t6'
    ]

    def parse(self, response):
        # load api response as json
        r = response.json()

        # collecting category item counts and url navigation information
        count = r['data']['attributes']['main-content'][0]['total-num-recs']
        url = response.url
        part = (url.split("/"))[5]
        last = r['links']['last']
        p = r['links']['self']
        this_page = int((p.split("="))[1])
        last_page = int((last.split("="))[1])
        partial = r['links']['next'][:-1]

        # if it is a sale page do extra processing to get item details
        for i in range(this_page, last_page+1): 
            # generate url for next page request
            new_url = "/api" + partial + str(i) + "&page_size=20"
            yield response.follow(new_url, callback=self.gather_sale_details)
        item_counts = part+", "+str(count)
        counts.write(item_counts+'\n')

    def gather_sale_details(self, response):
        # collect item details for sale products
        rr = json.loads(response.text)
        url = response.url
        part = (url.split("/"))[5]
        sku_list = []
        start, end = 0, len(rr['data']['attributes']['main-content'][0]['records'])

        while start < end:
            
            sku = rr['data']['attributes']['main-content'][0]['records'][start]['default-sku']
            all_detail = rr['data']['attributes']['main-content'][0]['records'][start]
            sku = sku.replace("us_", "")
            sku_list.append(sku)

                # collect the style level skus
            first, last = 0, len(rr['data']['attributes']['main-content'][0]['records'][start]['sku-style-order'])
            while first < last:
                isku = rr['data']['attributes']['main-content'][0]['records'][start]['sku-style-order'][first]['sku']
                spec_sku = isku.replace("us_","")
               # spec_sku = json.dumps(spec_sku)
                detail_skuList.write(spec_sku+'\n')
                first += 1
                sku_list.append(spec_sku)
            
            product['all_detail'] = all_detail 
            #sku = json.dumps(sku)
            detail_skuList.write(sku+'\n')
            start += 1
            yield product

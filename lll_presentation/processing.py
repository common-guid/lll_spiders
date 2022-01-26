import pandas as pd
import jsonlines
import json
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None

data_df = pd.DataFrame(columns=["item_name", "sku", "list_price", "on_sale", "min_sale", "max_sale", 
                    "sizes", "hierarchy"])

with jsonlines.open('/home/guid/Work/lll_presentation/lll_presentation/lll_presentation/output/run1.jl', 'r') as f: 
    for item in f:
        raw = json.dumps(item['all_detail'])
        data = json.loads(raw)
        data_df = data_df.append({
            "item_name": data['unified-id'],
            "sku": data['default-sku'].replace("us_",""), 
            "list_price": float(data['list-price'][0]),
            "on_sale": data['product-on-sale'],
            "min_sale": float(data['product-sale-price'][0]) if 
                                data['product-on-sale'] == '1' else 'n/a',
            "max_sale": float(data['product-sale-price'][1]) if 
                                data['product-on-sale'] == '1' and len(data['product-sale-price']) == 2 
                                else float(data['product-sale-price'][0]) if
                                data['product-on-sale'] == '1' and len(data['product-sale-price']) == 1
                                else 'n/a',
            "sizes": data['all-available-sizes'],
            "hierarchy": data['product-category-hierarchy']
        }, ignore_index=True)


df = data_df[data_df['on_sale'] == '1']
df['avg_sale'] = (df['min_sale'] + df['max_sale']) / 2
df['pct_redux'] = (df['avg_sale'] - df['list_price']) / df['list_price']
print("Average Discount % :", df['pct_redux'].mean() * 100)


## parsing scrapying gql_spider output

gdf = pd.DataFrame(columns=['sku', 'low_stock', 'availability'])

fp = open('/home/guid/Work/lll_presentation/lll_presentation/lll_presentation/output/fulltestGQL.jl','r')
reader = jsonlines.Reader(fp)
first = reader.read()

for item in reader:
    raw = json.dumps(item['data'])
    data = json.loads(raw)
    for obj in data['inventoryDetails']['sku']: 
        gdf = gdf.append({"sku": obj['id'],
                        "low_stock": obj['isLowStock'],
                        "availability": obj['available']},
                        ignore_index=True) 

all_sku = pd.merge(left=data_df, right=gdf, how='left')

print("number unique sku: ", gdf['sku'].nunique())
dedupe = gdf.drop_duplicates(subset='sku')
print("count low stock: ", dedupe['low_stock'].value_counts())
print("count available: ", dedupe['availability'].value_counts())

## category counts

counts = {}
with open('/home/guid/Work/lll_presentation/lll_presentation/lll_presentation/output/TESTcat_counts.json', 'r') as c: 
    for item in c:
        category, count = item.split(", ")[0], int(item.split(", ")[1])
        counts[category] = count

not_sale = counts['accessories'] + counts['men'] + counts['women']
sale_pct_invn = (counts['sale'] / not_sale) * 100
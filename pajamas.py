import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

rng = np.random.default_rng(42)
#Table 1: Products table, catalog like
def generate_products(n=600):
    size_a = [4, 6, 8, 10, 12, 14, 16]
    size_b = ['XS', 'X', 'M', 'L', 'XL']

    size_by_segment = {'kids' : size_a, 'women' : size_b, 'men': size_b}

    base_price = 12000
    segment_at = {'kids' :- 2000,'women' : 2000, 'men' : 1500 }
    material_at ={'acetate' : 1000,'cotton' : 3000}
    type_at = {'long sleeved' : 1250, 'short sleeved' : 500, 'no sleeved' : 500}
    print_at = {'Yes' : 2500, 'No' : 0} 
    ownership_at = {'Own' : 0, 'Resell' : 1500}

    segment = rng.choice(['women', 'kids', 'men'], n)
    re = rng.integers(50, 100, size = n)
    ini = rng.integers(100, 200, size = n)
    material = rng.choice(['acetate', 'cotton'], n)
    ty= rng.choice(['short sleeved', 'long sleeved', 'no sleeved'], n)
    printed = rng.choice(['Yes', 'No'], n)
    origin = rng.choice(['Own', 'Resell'], n)

    size = []
    for s in segment: size.append(rng.choice(size_by_segment[s]))

    price = []
    for i in range(n):
        p = base_price
        p += segment_at[segment[i]]
        p += material_at[material[i]]
        p += type_at[ty[i]]
        p += print_at[printed[i]]
        p += ownership_at[origin[i]]
        p += rng.integers(-500, 500)   
        price.append(int(p))

    pajamas = {
        'Segment' : pd.Series(segment),
        'Size' : pd.Series(size),
        'Material' : pd.Series(material, dtype = 'object'),
        'Type' : pd.Series(ty),
        'Print': pd.Series(printed),
        'Origin' : pd.Series(origin),
        'Reorder Point': pd.Series(re),
        'Initial Stock': pd.Series(ini),
        'Unit Price' : pd.Series(price, dtype = 'int64'),
    }

    df = pd.DataFrame(pajamas)
    df = df.drop_duplicates(subset=['Segment','Size','Material','Type','Print','Origin'])  
    df = df.head(250).reset_index(drop=True)
    df.insert(0, 'SKU', ['PJ-%03d' % i for i in range(1, 251)])
    return df
df = generate_products()
print(df.head())


#Table 2: Movements Generator, ledger like
def generate_movements(products):
    months = pd.date_range('2015-03-01', '2019-11-01', freq='MS')
    seasonality = {1: 1.5, 2: 1.2, 3: 1.3, 4: 1, 5: 0.5, 6: 1, 7: 0.8, 8: 0.7, 9: 1.1, 10: 0.9, 11: 1.4, 12: 2}   
    def random_day_in(m): 
        day = m + pd.Timedelta(days=int(rng.integers(0, 28))) 
        return day

    events = []
    price_by_sku = dict(zip(products['SKU'], products['Unit Price']))     
    for sku in df['SKU']:                                     
        for m in months:                                      
            season = seasonality[m.month]                 
            for sell_ in range(rng.integers(1, 4)):              
                events.append({'date': random_day_in(m), 'sku_id': sku, 'type': 'Sell',
                            'quantity': int(rng.integers(2,10) * season),
                            'unit_price': price_by_sku[sku]})
            for restock_ in range(rng.integers(1, 3)):              
                events.append({'date': random_day_in(m), 'sku_id': sku, 'type': 'Restock',
                            'quantity': int(rng.integers(10,50)),
                            'unit_price': price_by_sku[sku]})
             
    df2 = pd.DataFrame(events)
    return df2 
df2 = generate_movements(df)

#QA
print(df2.head())
print((df2['quantity'] > 0).all())
print(df2['type'].value_counts())
print(df2['sku_id'].nunique())
print(df2['sku_id'].isin(df['SKU']).all())
print(df2['date'].min())
print(df2['date'].max())
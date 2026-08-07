import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


#Table 1: Products table, catalog like
def generate_products(n=600):
    global rng
    rng = np.random.default_rng(42)
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

#Monthly Sales Trend
def sales_trend(movements):
    sales = movements[movements['type'] == 'Sell'].copy()
    sales['revenue'] = sales['quantity'] * sales['unit_price']
    return sales.groupby(sales['date'].dt.to_period('M'))['revenue'].sum()   # filter ROWS with the mask
monthly = sales_trend(df2)

def plot_trends(monthly):
    g = monthly.groupby(monthly.index.year)   # group by the year of each Period
    peak_month = g.idxmax()                   # year -> the peak month (Period)
    peak_val   = g.max()                      # year -> the peak revenue
    x = monthly.index.to_timestamp()          # Period -> real datetimes    
    y = monthly.values / 1_000_000            # revenue in millions

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(x, y, marker='o', markersize=4)
    ax.grid(True)
    ax.set_title('Monthly sales revenue 2015-2019')
    ax.set_xlabel('Months')
    ax.set_ylabel('COP (millions)')
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))         # tick every 6 months
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))        
    ax.figure.autofmt_xdate()
    peak_x = monthly.idxmax().to_timestamp()                            # x of the max (Dec 2015)
    peak_y = monthly.max() / 1_000_000                                  # y of the max, in millions
    for yr in peak_val.index:
        px = peak_month[yr].to_timestamp()
        py = peak_val[yr] / 1e6
        ax.annotate(str(peak_month[yr]), xy=(px, py), xytext=(px, py + 1), horizontalalignment='left')
    plt.show()  


    cum = monthly.cumsum()
    gc = cum.groupby(cum.index.year)
    ye_month = gc.idxmax()                                              # Dec of each year
    ye_val   = gc.max()                                                 # cumulative total at that Dec

    ax = (cum/1e9).plot(marker='o', markersize=3, figsize = (10, 4))   
    ax.grid(True);
    ax.set_title('Total revenue accumulated 2015-2019');
    ax.set_xlabel('Dates');
    ax.set_ylabel('COP (billions)');
    for yr in ye_val.index:
        px = ye_month[yr].to_timestamp()
        py = ye_val[yr] / 1e9
        ax.annotate(f'{ye_val[yr]/1e9:.1f}B', xy=(px, py), xytext=(px, py -0.4), horizontalalignment='right',
                    arrowprops=dict(arrowstyle='->'))
    plt.show()
plot_trends(monthly)   
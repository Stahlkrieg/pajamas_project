import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
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
#print(df.head())

#Table 2: Movements Generator, ledger like
def generate_movements(products):
    months = pd.date_range('2015-03-01', '2019-11-01', freq='MS')
    seasonality = {1: 1.5, 2: 1.2, 3: 1.3, 4: 1, 5: 0.5, 6: 1, 7: 0.8, 8: 0.7, 9: 1.1, 10: 0.9, 11: 1.4, 12: 2}   
    def random_day_in(m): 
        day = m + pd.Timedelta(days=int(rng.integers(0, 28))) 
        return day

    events = []
    price_by_sku = dict(zip(products['SKU'], products['Unit Price']))     
    popularity = {sku: rng.choice([1, 3, 10,60], p=[0.6, 0.25, 0.10, 0.05]) for sku in products['SKU']}
    init_by_sku  = dict(zip(products['SKU'], products['Initial Stock']))
    reorder_by_sku = dict(zip(products['SKU'], products['Reorder Point']))
    
    for sku in df['SKU']:      
        shelf = init_by_sku[sku]                 
        for m in months:
            season = seasonality[m.month]
            month_sells = [(random_day_in(m), int(rng.integers(2,10)*season)) for _ in range(int(rng.integers(1,4)*popularity[sku]))]
            month_sells.sort(key=lambda t: t[0])

            for day, quantity in month_sells:
                shelf -= quantity
                events.append({'date': day, 'sku_id': sku, 'type':'Sell',
                            'quantity': quantity, 'unit_price': price_by_sku[sku]})
                if shelf < reorder_by_sku[sku]:
                    amount = init_by_sku[sku] - shelf
                    shelf += amount
                    events.append({'date': day + pd.Timedelta(days=1), 'sku_id': sku,
                                'type':'Restock', 'quantity': amount, 'unit_price': price_by_sku[sku]})
    df2 = pd.DataFrame(events)
    return df2 
df2 = generate_movements(df)
print(df2)

'''#QA
print(df2.head())
print((df2['quantity'] > 0).all())
print(df2['type'].value_counts())
print(df2['sku_id'].nunique())
print(df2['sku_id'].isin(df['SKU']).all())
print(df2['date'].min())
print(df2['date'].max())'''

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

    fig, ax = plt.subplots(figsize=(14, 6))
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

    ax = (cum/1e9).plot(marker='o', markersize=3, figsize = (14, 6))   
    ax.grid(True);
    ax.set_title('Total revenue accumulated 2015-2019');
    ax.set_xlabel('Dates');
    ax.set_ylabel('COP (billions)');
    for yr in ye_val.index:
        px = ye_month[yr].to_timestamp()
        py = ye_val[yr] / 1e9
        ax.annotate(f'{ye_val[yr]/1e9:.1f}B', xy=(px, py), xytext=(px, py + 0.2), horizontalalignment='right',
                    arrowprops=dict(arrowstyle='->'))
    plt.show()
#plot_trends(monthly)  


#ABC and Pareto Chart
def sales_revenue(abc):
    t_sales = abc[abc['type']=='Sell'].copy()
    t_sales['revenue'] = t_sales['quantity'] * t_sales['unit_price']
    return t_sales.groupby(t_sales['sku_id'])['revenue'].sum().sort_values(ascending = False)
pareto = sales_revenue(df2)
run_total = pd.Series(pareto).cumsum()
cum_per = pd.Series(pareto).cumsum()/pareto.sum()*100
bucket = []

for i in cum_per:
    if i <= 80:  bucket.append('A')    
    elif i <= 95: bucket.append('B')     
    else: bucket.append('C')     

dar = {
    'revenue' : pd.Series(pareto),
    'running total' : pd.Series(run_total),
    'cummulative %' : pd.Series(cum_per),
    'bucket': pd.Series(bucket, index=pareto.index)

}
df3 = pd.DataFrame(dar)
#print(df3)


def plot_pareto(df3, top_n=30):
    pareto  = df3['revenue']
    cum_per = df3['cummulative %']
    colors  = df3['bucket'].map({'A':'#d62728','B':'#ff7f0e','C':'#1f77b4'})
    x = range(len(pareto))

    # full view
    fig, ax = plt.subplots(figsize=(14,6))
    ax.bar(x, pareto.values/1e6, color=colors);
    ax2 = ax.twinx()
    ax2.plot(x, cum_per.values, color='green');
    ax2.axhline(80, color='gray', linestyle='--');
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v,_: f'{int(v)}%'));
    ticks = range(0, len(pareto), 50)
    ax.set_xticks(ticks);
    ax.set_xticklabels([pareto.index[i] for i in ticks], rotation=45);
    pos = int((cum_per.values >= 80).argmax())
    ax.axvline(pos, color='gray', linestyle=':');
    ax.annotate(f'top {pos} SKUs ≈ 80%', xy=(pos, pareto.values[pos]/1e6),
                xytext=(pos+20, 600), arrowprops=dict(arrowstyle='->'));
    handles = [Patch(color='#d62728',label='A'), Patch(color='#ff7f0e',label='B'),
               Patch(color='#1f77b4',label='C'), Line2D([0],[0],color='green',label='Cumulative %')]
    ax.legend(handles=handles, loc='center right');
    ax.set_title('Pareto: SKU revenue concentration');
    ax.grid(True);
    ax.set_xlabel('TOP SKU');
    ax.set_ylabel('Revenue (Millions)');
    ax2.set_ylabel('Cummulative [%]');
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(5))
    ax2.yaxis.set_minor_locator(ticker.AutoMinorLocator(5))

    # zoom view
    top = pareto.head(top_n)
    fig, axz = plt.subplots(figsize=(14,6))
    axz.bar(range(top_n), top.values/1e6, color=colors.head(top_n));
    axz.set_xticks(range(top_n));
    axz.set_xticklabels(top.index, rotation=45);
    axz.set_title(f'Top {top_n} SKUs by revenue');
    axz.grid(True);
    axz.yaxis.set_minor_locator(ticker.AutoMinorLocator(5))
    axz2 = axz.twinx()
    axz2.plot(range(top_n), cum_per.head(top_n).values, color='green');
    axz2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f'{int(v)}%'));
    axz2.yaxis.set_minor_locator(ticker.AutoMinorLocator(5))
    axz.set_ylabel('Revenue (Millions)');
    axz2.set_ylabel('Cumulative [%]');
    plt.show()
#plot_pareto(df3)

#stock levels + restocking cycles
def build_stock_flow(df2, df):
    flow = df2.copy()
    event = []
    flow['flow'] = np.where(flow['type'] == 'Sell', -flow['quantity'], flow['quantity'])
    flow = flow.sort_values('date')
    flow['cum_sum'] = flow.groupby('sku_id')['flow'].cumsum()
    new_stock = dict(zip(df['SKU'], df['Initial Stock']))
    flow['stock'] = flow['sku_id'].map(new_stock)
    flow['stock_level'] = flow['stock'] + flow['cum_sum']
    return flow 
flow = build_stock_flow(df2, df)            

hit  = df3.index[0]
tail = df3.index[-1]

def plot_flow(flow):
    hit_1 = (flow['sku_id'] == hit) & (flow['date'].dt.year == 2017) & (flow['date'].dt.month >= 10)
    tail_1 =(flow['sku_id']==tail) & (flow['date'].dt.year==2017) & (flow['date'].dt.month >= 10)
    sel = flow[hit_1]
    tel = flow[tail_1]
    x_hit = sel['date'].values 
    y_hit = sel['stock_level'].values
    x_tail = tel['date'].values 
    y_tail = tel['stock_level'].values

    rp = dict(zip(df['SKU'], df['Reorder Point']))   # SKU -> reorder point

    fig, ax = plt.subplots(figsize=(14,6))
    ax.plot(x_hit, y_hit, color='red', label = 'PJ-221')
    ax.legend()  
    ax2 = ax.twinx()
    ax2.plot(x_tail, y_tail, color='orange', label = 'PJ-151')
    ax.set_xlabel('Date')
    ax.set_ylabel('Stock Level Value')
    ax.set_title('PJ-221 vs PJ-151') 
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(5))
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(5))
    ax.grid()
    ax.axhline(rp[hit],  color='red',    ls='--')
    ax2.axhline(rp[tail], color='orange', ls='--')   
    ax2.legend()    
    plt.show()
plot_flow(flow)

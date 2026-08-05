import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

n = 600
size_a = [4, 6, 8, 10, 12, 14, 16]
size_b = ['XS', 'X', 'M', 'L', 'XL']

size_by_segment = {
    'kids' : size_a,     
    'women' : size_b,  
    'men': size_b,      
}

base_price = 12000
segment_at = {'kids' :- 2000,'women' : 2000, 'men' : 1500 }
material_at ={'acetate' : 1000,'cotton' : 3000}
type_at = {'long sleeved' : 1250, 'short sleeved' : 500, 'no sleeved' : 500}
print_at = {'Yes' : 2500, 'No' : 0} 
ownership_at = {'Own' : 0, 'Resell' : 1500}


rng = np.random.default_rng()
#index= rng.integers(low=100, high=999, size= 250)
segment = rng.choice(['women', 'kids', 'men'], n)
re = rng.integers(50, 100, size = n)
ini = rng.integers(100, 200, size = n)
material = rng.choice(['acetate', 'cotton'], n)
ty= rng.choice(['short sleeved', 'long sleeved', 'no sleeved'], n)
printed = rng.choice(['Yes', 'No'], n)
origin = rng.choice(['Own', 'Resell'], n)

size = []
for s in segment:
    size.append(rng.choice(size_by_segment[s]))

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

pajamas_k = {
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

df =pd.DataFrame(pajamas_k)
df = df.drop_duplicates(subset=['Segment','Size','Material','Type','Print','Origin'])  
df = df.head(250).reset_index(drop=True)
df.insert(0, 'SKU', ['PJ-%03d' % i for i in range(1, 251)])   # PJ-001 … PJ-250
print(df)
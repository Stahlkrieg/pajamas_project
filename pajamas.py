import pandas as pd
import matplotlib as plt
import numpy as np


size_a = (4, 6, 8, 10, 12, 14, 16)
size_b = ['XS', 'X', 'M', 'L', 'XL']

rng = np.random.default_rng()
#index= rng.integers(low=100, high=999, size= 250)
segmento = rng.choice(size_a, 250)
uni = rng.integers(8000, 30000, size = 250)
re = rng.integers(50, 100, size = 250)
ini = rng.integers(100, 200, size = 250)
material = rng.choice(['acetate', 'cotton'], 250)
ty= rng.choice(['short sleeved', 'long sleeved', 'no sleeves'], 250)
printed = rng.choice(['Yes', 'No'], 250)
origin = rng.choice(['Own', 'Resell'], 250)
pajamas_k = {
    'Size' : pd.Series(segmento),
    'Material' : pd.Series(material),
    'Type' : pd.Series(ty),
    'Print': pd.Series(printed),
    'Origin' : pd.Series(origin),
    'Unit Price' : pd.Series(uni),
    'Reorder Point': pd.Series(re),
    'Initial Stock': pd.Series(ini)
}

pajamas_s = {
    'size' : size_b,
    'material' : ('acetate', 'cotton'),
    'type' : ('short sleeved', 'long sleeved', 'no sleeves'),
    'print': ['Yes', 'No'],
    'origin' : ['Own', 'Resell']
}


df = pd.DataFrame(pajamas_k)
#df1 = pd.concat([df, price_k, reorder_k, stock_k], axis=1)

print(df)

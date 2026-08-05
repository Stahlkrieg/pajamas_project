import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


size_a = [4, 6, 8, 10, 12, 14, 16]
size_b = ['XS', 'X', 'M', 'L', 'XL']

size_by_segment = {
    'kids' : size_a,     
    'women' : size_b,  
    'men': size_b,      
}

rng = np.random.default_rng()
#index= rng.integers(low=100, high=999, size= 250)
segment = rng.choice(['women', 'kids', 'men'], 250)
uni = rng.integers(8000, 30000, size = 250)
re = rng.integers(50, 100, size = 250)
ini = rng.integers(100, 200, size = 250)
material = rng.choice(['acetate', 'cotton'], 250)
ty= rng.choice(['short sleeved', 'long sleeved', 'no sleeves'], 250)
printed = rng.choice(['Yes', 'No'], 250)
origin = rng.choice(['Own', 'Resell'], 250)

size = []
for seg in segment:
    size.append(rng.choice(size_by_segment[seg]))

pajamas_k = {
    'Segment' : pd.Series(segment),
    'Size' : pd.Series(size),
    'Material' : pd.Series(material),
    'Type' : pd.Series(ty),
    'Print': pd.Series(printed),
    'Origin' : pd.Series(origin),
    'Unit Price' : pd.Series(uni),
    'Reorder Point': pd.Series(re),
    'Initial Stock': pd.Series(ini)
}

df = pd.DataFrame(pajamas_k)

print(df)

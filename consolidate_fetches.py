import os
import datetime
import numpy as np

files = [filename for filename in os.listdir("data/small_fetches") if 'yak_grab' in filename]

total = []
for f in files:
    arr = np.load('data/small_fetches/' + f).tolist()
    total += arr

np.save(("data/consolidations/yak_cons_" + str(datetime.datetime.now())), total)
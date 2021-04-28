import numpy as np
x = np.load('output.npz', mmap_mode='r')
for i in x.files:
  print(i)
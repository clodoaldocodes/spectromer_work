#%%
import numpy as np

a =  np.array([0, 1, 2, 3])
b = np.array([1, 1, 1, 1])
c = np.array([3, 4, 5, 6])

a.append(b)
a.append(c)
aux = np.matrix(a.reshape((np.size(a, axis=0), 3)))
print(aux)
# %%

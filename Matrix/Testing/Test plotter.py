import numpy as np

import NBodyLib as nbl
import matplotlib.pyplot as plt

# --- --- PLOT DRAWING --- ---

data = nbl.pd.read_csv('Testing/Time test.csv')
data2 = nbl.pd.read_csv('Testing/Time loop.csv')
ns = data["Number"]
ts = data["Time"]
ns2 = data2["Number"]
ts2 = data2["Time"]

highres_ns = np.linspace(1, 40, 200)
# print(highres_ns)

aprx1 = lambda x: 0.1*(x**(-9/5)) # Approximation with POWER
aprx2 = lambda x: 0.723 * np.exp(-0.4529*x) # Approximation with EXP

# tsa = list(map(aprx1, ns))
tsa = list(map(aprx1, highres_ns))
# tsa2 = list(map(aprx2, ns))

plt.style.use('dark_background')
plt.rcParams['text.usetex'] = True
fig, ax = plt.subplots()

ax.set(xlabel=r'Number of objects (1)', ylabel=r'$1/T \quad (sec^{-1})$',
       title='Performance')
ax.grid(True, color='grey', alpha=0.25)

ax.plot(ns, ts, c="lime", label=r'OpenCL')
ax.plot(ns2, ts2, c="violet", label=r'Loop CPU')

# ax2 = ax.twiny()
# ax2.plot(highres_ns, tsa, c="red", label=r'Approx $y = 0.1x^{-1.8}$') # Approximation with POWER
# ax.plot(ns, tsa2, c="blue", label=(r'Approx $y = 0.7e^{-0.45x}$')) # Approximation with EXP

plt.legend()
# fig.tight_layout()

fig.savefig("Test Loop + OpenCl.png", dpi=450)
plt.show()
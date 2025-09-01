import numpy as np
import matplotlib.pyplot as plt

casmo = np.load("casmo_exposure_keff.npy")
casmo2 = np.load("casmo2_exposure_keff.npy")
scarabee = np.load("exposure_keff.npy")

plt.plot(scarabee[0,:], scarabee[1,:], label="Scarabee Style 1 MWd/kg")
plt.plot(casmo[0,:], casmo[1,:],       label="CASMO    Style 1 MWd/kg")
plt.plot(casmo2[0,:], casmo2[1,:],     label="CASMO    Style 2 MWd/kg")
plt.xlabel("Exposure [MWd/kg]")
plt.ylabel("keff")
plt.legend().set_draggable(True)
plt.tight_layout()
plt.show()

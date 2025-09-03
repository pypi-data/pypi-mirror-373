# =============================================================================
# 1. Import classes and modules
# =============================================================================

# =============================================================================
# #If local installation of dopes instead of using PyPI (https://pypi.org/project/dopes/)
# import sys
# important_path = 'D:\\Roisin\\Documents\\dopes'        
# if important_path not in sys.path:
#     sys.path.insert(0, important_path)
# =============================================================================

import dopes.data_analysis.polytec as pol
import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# 2. Open data map file
# =============================================================================

data_path="data/membrane_1kPa_area.txt"

step=10
data=np.genfromtxt(data_path)
x=data[::step,0]
y=data[::step,1]
z=data[::step,2] * 1e3

# =============================================================================
#  3. Plot 2D maps of the membrane deflection
# =============================================================================

# 2D map without median filtering to remove the outlier
fig, ax_map, ax_bar=pol.plot_map(x, y, z,levels=15,medfilt=False)
fig.set_dpi(200)

# 2D map with median filtering to remove the outlier
fig, ax_map, ax_bar=pol.plot_map(x, y, z,levels=15,medfilt=True,kernel_size=5 )
fig.set_dpi(200)

# Search for the maximum of the deflection

x_max,y_max,z_max=pol.find_max(x, y, z,kind="peaks")
ax_map.plot(x_max,y_max,marker="x",color="k")

# =============================================================================
# 4. Plot 1D lines of the membrane deflection
# =============================================================================

file_path="data/membrane_1kPa_lines.txt"
pol.plot_1D_line_from_file(file_path,unit_mult=(1e3,1e6))


# =============================================================================
# 5. Plot 1D lines of the membrane deflection for all pressures
# =============================================================================
fig,ax=plt.subplots(dpi=200)
ax.set_xlabel("d (mm)")
ax.set_ylabel("z (mm)")
for p in range(9):
    file_path="data/membrane_%dkPa_lines.txt"%p
    pol.plot_1D_line_from_file(file_path,unit_mult=(1e3,1e6),ax=ax,use_lines=[2],label="%d kPa"%p)
ax.legend(ncol=2)
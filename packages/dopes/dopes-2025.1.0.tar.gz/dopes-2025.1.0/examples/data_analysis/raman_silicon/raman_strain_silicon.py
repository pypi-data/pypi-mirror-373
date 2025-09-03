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

import dopes.data_analysis.raman as ram
import dopes.data_analysis.data_processing as proc
import dopes.data_analysis.file_handling as file_handling

import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# 2. Plot Raman spectrum from one data file
# =============================================================================


file_path="data/strained_silicon_1.txt"

peak_position, peak_height, peak_width=ram.find_peaks_from_file(file_path,height=500)
fig,ax=ram.plot_from_file(file_path,with_peaks=True,with_peaks_label=True,height=500,color="red")
fig.set_dpi(200)
ax.set_ylim((0,3000))
ax.set_xlim((500,540))
ax.set_xlabel("Energy (cm-1)")
ax.set_ylabel("Intensity (counts)")

# =============================================================================
# 2.bis Plot Raman spectrum from one data file with baseline correction
# =============================================================================


file_path="data/strained_silicon_1.txt"
file_path="data/strained_silicon_1.txt"

data=file_handling.read_file(file_path,comments="#",delimiter=None)
x=data[:,0]
y_raw=data[:,1]

y,baseline=proc.remove_baseline(x,y_raw,xmin_baseline=[350,540],xmax_baseline=[500,700])

fig,ax=ram.plot_with_peaks(x,y,height=500,color="red",with_peaks_label=True)
fig.set_dpi(200)
ax.set_ylim((0,3000))
ax.set_xlim((500,540))
ax.set_xlabel("Energy (cm-1)")
ax.set_ylabel("Intensity (counts)")

# =============================================================================
# 3. Plot Raman spectra from multiple data files
# =============================================================================

file_paths=["data/strained_silicon_%d.txt"%(i+1) for i in range(6)]
fig,ax_list=ram.plot_from_multiple_files(file_paths,with_peaks=True,with_peaks_label=True,sharey=True,ylabel="Intensity (counts)",height=500,color="red")
fig.set_dpi(200)
ax_list[0].set_xlim((500,540))
ax_list[0].set_ylim((0,3000))
ax_list[-1].set_xlabel("Energy (cm-1)")


# =============================================================================
# 4. Plot Raman spectra from one data file and fit with Lorentzian function
# =============================================================================

file_path="data/strained_silicon_1.txt"

data=file_handling.read_file(file_path,comments="#",delimiter=None)
x=data[:,0]
y_raw=data[:,1]

y,baseline=proc.remove_baseline(x,y_raw,xmin_baseline=[350,540],xmax_baseline=[500,700])
p_lorentzian,y_lorentzian=proc.fit_lorentzian(x,y,xmin=500,xmax=540)

x_interp=np.linspace(500,540,401)
y_lorentzian_interp=proc.lorentzian(x_interp,p_lorentzian["position"],p_lorentzian["amplitude"],p_lorentzian["width"])

fig,ax=plt.subplots()
fig.set_dpi(200)
ax.set_ylim((0,2500))
ax.set_xlim((500,540))
ax.set_xlabel("Energy (cm-1)")
ax.set_ylabel("Intensity (counts)")
ax.plot(x,y,marker=".",lw=0.5,label="measurement")
ax.plot(x_interp,y_lorentzian_interp,color="tab:red",ls="--",label="Lorentzian fit")
ax.legend()

plt.show()
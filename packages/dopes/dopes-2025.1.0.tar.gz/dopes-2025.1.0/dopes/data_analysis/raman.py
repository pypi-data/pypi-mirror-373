import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
import dopes.data_analysis.file_handling as file_handling

def phonon_deformation_silicon(strain_matrix,p,q,r,sort=False,w0=None):
    """ Function to calculate the Raman shift from an arbitrary strain tensor using Phonon Deformation Potential (PDP) theory
    
        args:
           \n\t- strain_matrix (3x3 matrix) : the strain tensor
           \n\t- p (scalar) : the first phonon deformation potential    
           \n\t- q (scalar) : the second phonon deformation potential.    
           \n\t- r (scalar) : the third phonon deformation potential  
           \n\t- sort (boolean) : if true, sort the phonon modes from lowest to highest energy
           \n\t- w0 (scalar) : reference energy at zero strain, 520.7 cm-1 for silicon
           
        return:
           \n\t- an array of three elements with the energy of the three phonon modes (LO, TO1, and TO2).
    """
    if w0==None:
        w0=520.7 # in cm-1
        
    p=p*w0**2
    q=q*w0**2
    r=r*w0**2
    exx=strain_matrix[0,0]
    eyy=strain_matrix[1,1]
    ezz=strain_matrix[2,2]
    eyz=strain_matrix[1,2]
    exz=strain_matrix[0,2]
    exy=strain_matrix[0,1]
    ezy=strain_matrix[2,1]
    ezx=strain_matrix[2,0]
    eyx=strain_matrix[1,0]
    P=np.array([[p*exx+q*(eyy+ezz),2*r*exy,2*r*exz],
                [2*r*eyx,p*eyy+q*(ezz+exx),2*r*eyz],
                [2*r*ezx,2*r*ezy,p*ezz+q*(eyy+exx)]])
    det=np.linalg.det(P)
    tr=np.trace(P)
    tr2=np.trace(P.dot(P))
    
    if sort : 
        lamb=np.sort(np.roots([1,-tr,-0.5*(tr2-tr**2),-det]))
        
    else :
        lamb=np.roots([1,-tr,-0.5*(tr2-tr**2),-det])
    return np.sqrt(lamb+w0**2)

def find_peaks(x,y,height=None, threshold=None, distance=None, width=None):
    """ Function to find peaks in the Raman spectrum. Be careful that the method is not a fit put a peak detection.
    
        args:
           \n\t- x (array) : an array 
           \n\t- y (array) : the signal with peaks with the same dimension as x
           \n\t- height (None, scalar or 2-element sequence) : required height of peaks. Either a number, None, an array matching x or a 2-element sequence of the former. The first element is always interpreted as the minimal and the second, if supplied, as the maximal required height.
           \n\t- threshold (None, scalar or 2-element sequence) : required threshold of peaks, the vertical distance to its neighboring samples. Either a number, None, an array matching x or a 2-element sequence of the former. The first element is always interpreted as the minimal and the second, if supplied, as the maximal required threshold.
           \n\t- distance (scalar) : Required minimal horizontal distance in samples between neighbouring peaks. The distance should be higher than the step between two adjacents points from x. Smaller peaks are removed first until the condition is fulfilled for all remaining peaks.
           \n\t- width (None, scalar or 2-element sequence) : required width of peaks in samples. Either a number, None, an array matching x or a 2-element sequence of the former. The first element is always interpreted as the minimal and the second, if supplied, as the maximal required width.
        
        return:
           \n\t- (positions, heights, widths) : an array of three elements with the positions, the heights and the widths of the peaks
    """
    peaks_properties={}
    dx=(np.max(x)-np.max(y))/len(x)
    
    if distance is not None:
        distance_index=int(np.round(distance/dx))
    else:
        distance_index=None
    
    peaks_index,prop=scipy.signal.find_peaks(y,height=height, threshold=threshold, distance=distance_index, width=width)
    if height is not None:
        peaks_properties["peak_heights"]=prop["peak_heights"]
    else:
        peaks_properties["peak_heights"]=y[peaks_index]
        
    if width is not None:
        peaks_properties["widths"]=prop["widths"]
    else:
        peaks_properties["widths"]=scipy.signal.peak_widths(y,peaks_index)[0]
    
    
    return x[peaks_index],peaks_properties["peak_heights"],peaks_properties["widths"]
    
def find_peaks_from_file(file_path,height=None, threshold=None, distance=None, width=None):
    """ Function to find peaks in the Raman spectrum. Be careful that the method is not a fit put a peak detection.
    
        args:
           \n\t- x (array) : an array 
           \n\t- y (array) : the signal with peaks with the same dimension as x
           \n\t- height (None, scalar or 2-element sequence) : required height of peaks. Either a number, None, an array matching x or a 2-element sequence of the former. The first element is always interpreted as the minimal and the second, if supplied, as the maximal required height.
           \n\t- threshold (None, scalar or 2-element sequence) : required threshold of peaks, the vertical distance to its neighboring samples. Either a number, None, an array matching x or a 2-element sequence of the former. The first element is always interpreted as the minimal and the second, if supplied, as the maximal required threshold.
           \n\t- distance (scalar) : Required minimal horizontal distance in samples between neighbouring peaks. The distance should be higher than the step between two adjacents points from x. Smaller peaks are removed first until the condition is fulfilled for all remaining peaks.
           \n\t- width (None, scalar or 2-element sequence) : required width of peaks in samples. Either a number, None, an array matching x or a 2-element sequence of the former. The first element is always interpreted as the minimal and the second, if supplied, as the maximal required width.
        
        return:
           \n\t- (positions, heights, widths) : an array of three elements with the positions, the heights and the widths of the peaks
    """
    data=file_handling.read_file(file_path,comments="#",delimiter=None)
    x=data[:,0]
    y=data[:,1]

    return find_peaks(x,y,height, threshold, distance, width)

def plot_with_peaks(x,y,ax=None,height=None, threshold=None, distance=None, width=None,with_peaks_label=False,**plot_kwargs):
    """ Function to plot the Raman spectrum with the peaks indicated.  Be careful that the method is not a fit put a peak detection.
    
        args:
           \n\t- x (array) : an array for the energy of the Raman spectrum
           \n\t- y (array) : the Raman signal with peaks with the same dimension as x
           \n\t- ax (Axes) : the axes of the subplot in which plotting the Raman signal and peaks
           \n\t- height (None, scalar or 2-element sequence) : required height of peaks. Either a number, None, an array matching x or a 2-element sequence of the former. The first element is always interpreted as the minimal and the second, if supplied, as the maximal required height.
           \n\t- threshold (None, scalar or 2-element sequence) : required threshold of peaks, the vertical distance to its neighboring samples. Either a number, None, an array matching x or a 2-element sequence of the former. The first element is always interpreted as the minimal and the second, if supplied, as the maximal required threshold.
           \n\t- distance (scalar) : Required minimal horizontal distance in samples between neighbouring peaks. The distance should be higher than the step between two adjacents points from x. Smaller peaks are removed first until the condition is fulfilled for all remaining peaks.
           \n\t- width (None, scalar or 2-element sequence) : required width of peaks in samples. Either a number, None, an array matching x or a 2-element sequence of the former. The first element is always interpreted as the minimal and the second, if supplied, as the maximal required width.
           \n\t- with_peaks_label (boolean) : if True, write the value of the peaks above each of them
           \n\t- **plot_kwargs : this method also takes any keyword argument for the Axes.plot() function such as linewidth, linestyle, marker, markersize, color, markeredgecolor, zorder, alpha, label, clip_on, ...
            
        return:
           \n\t- fig, ax : the Figure and Axes object created if None is specified for ax
    """
    
    if ax==None:
        fig=plt.figure()
        ax_data=fig.add_subplot()
    else:
        ax_data=ax
    
    ax_data.plot(x,y,**plot_kwargs)
    position, heights, width=find_peaks(x,y,height=height, threshold=threshold, distance=distance, width=width)
    
    ax_data.plot(position,heights,marker=".",ls="",color="k")
    for i in range(len(heights)):
        ax_data.plot([position[i],position[i]],[0,heights[i]],marker="",ls="--",color="k")
        if with_peaks_label:
            ax_data.text(position[i],1.1*heights[i],"%.2f"%position[i],ha="center",va="bottom",rotation="vertical")
    if ax==None:
        return fig, ax_data
    
def plot_from_file(file_path,ax=None,with_peaks=False,with_peaks_label=False,height=None, threshold=None, distance=None, width=None,**plot_kwargs):
    """ Function to plot the Raman spectrum with the peaks indicated
    
        args:
           \n\t- file_path (string) : the file to read
           \n\t- ax (Axes) : the axes of the subplot in which plotting the Raman signal and peaks
           \n\t- with_peaks (boolean) : if True, find the peaks in the spectrum and show them on the graph. Be careful that the method is not a fit put a peak detection.
           \n\t- with_peaks_label (boolean) : if True, write the value of the peaks above each of them
           \n\t- height (None, scalar or 2-element sequence) : required height of peaks. Either a number, None, an array matching x or a 2-element sequence of the former. The first element is always interpreted as the minimal and the second, if supplied, as the maximal required height.
           \n\t- threshold (None, scalar or 2-element sequence) : required threshold of peaks, the vertical distance to its neighboring samples. Either a number, None, an array matching x or a 2-element sequence of the former. The first element is always interpreted as the minimal and the second, if supplied, as the maximal required threshold.
           \n\t- distance (scalar) : Required minimal horizontal distance in samples between neighbouring peaks. The distance should be higher than the step between two adjacents points from x. Smaller peaks are removed first until the condition is fulfilled for all remaining peaks.
           \n\t- width (None, scalar or 2-element sequence) : required width of peaks in samples. Either a number, None, an array matching x or a 2-element sequence of the former. The first element is always interpreted as the minimal and the second, if supplied, as the maximal required width.
           \n\t- **plot_kwargs : this method also takes any keyword argument for the Axes.plot() function such as linewidth, linestyle, marker, markersize, color, markeredgecolor, zorder, alpha, label, clip_on, ...
            
        return:
           \n\t- fig, ax : the Figure and Axes object created if None is specified for ax
    """
    
    data=file_handling.read_file(file_path,comments="#",delimiter=None)
    x=data[:,0]
    y=data[:,1]
    
    if ax==None:
        fig=plt.figure()
        ax_data=fig.add_subplot()
    else:
        ax_data=ax
        
    if with_peaks:
        plot_with_peaks(x,y,ax=ax_data,height=height, threshold=threshold, distance=distance, width=width,with_peaks_label=with_peaks_label,**plot_kwargs)
    else:
        ax_data.plot(x,y,**plot_kwargs)
        
    if ax==None:
        return fig, ax_data
    
def plot_from_multiple_files(file_paths,with_peaks=False,with_peaks_label=False,height=None, threshold=None, distance=None, width=None,sharey=False,ylabel=None,**plot_kwargs):
    
    """ Function to plot the Raman spectrum with the peaks indicated
    
        args:
           \n\t- file_paths (list of string) : lis of the names for the files to read
           \n\t- ax (Axes) : the axes of the subplot in which plotting the Raman signal and peaks
           \n\t- with_peaks (boolean) : if True, find the peaks in the spectrum and show them on the graph. Be careful that the method is not a fit put a peak detection.
           \n\t- with_peaks_label (boolean) : if True, write the value of the peaks above each of them
           \n\t- height (None, scalar or 2-element sequence) : required height of peaks. Either a number, None, an array matching x or a 2-element sequence of the former. The first element is always interpreted as the minimal and the second, if supplied, as the maximal required height.
           \n\t- threshold (None, scalar or 2-element sequence) : required threshold of peaks, the vertical distance to its neighboring samples. Either a number, None, an array matching x or a 2-element sequence of the former. The first element is always interpreted as the minimal and the second, if supplied, as the maximal required threshold.
           \n\t- distance (scalar) : Required minimal horizontal distance in samples between neighbouring peaks. The distance should be higher than the step between two adjacents points from x. Smaller peaks are removed first until the condition is fulfilled for all remaining peaks.
           \n\t- width (None, scalar or 2-element sequence) : required width of peaks in samples. Either a number, None, an array matching x or a 2-element sequence of the former. The first element is always interpreted as the minimal and the second, if supplied, as the maximal required width.
           \n\t- **plot_kwargs : this method also takes any keyword argument for the Axes.plot() function such as linewidth, linestyle, marker, markersize, color, markeredgecolor, zorder, alpha, label, clip_on, ...
            
        return:
           \n\t- fig, ax : the Figure and a list with the axes object created
    """
    
    n_plot=len(file_paths)
    fig,ax=plt.subplots(n_plot,1,sharex=True,sharey=sharey,figsize=(5,n_plot*2))
    
    for i in range(n_plot):
        ax[-i-1].spines.right.set_visible(False)
        ax[-i-1].spines.top.set_visible(False)
        if ylabel is not None:
            ax[-i-1].set_ylabel(ylabel)
        # if i != 0:
        #     ax[-i-1].xticklabels.bottom.set_visible(False)
        plot_from_file(file_paths[i],ax=ax[-i-1],with_peaks=with_peaks,with_peaks_label=with_peaks_label,height=height, threshold=threshold, distance=distance, width=width,**plot_kwargs)
        
    return fig, ax
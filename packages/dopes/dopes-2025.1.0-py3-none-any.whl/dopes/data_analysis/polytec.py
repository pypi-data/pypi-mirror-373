import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

from scipy.interpolate import griddata
from scipy.signal import medfilt2d, find_peaks
import dopes.data_analysis.data_processing as proc


def find_max(x,y,z,kind="maximum",height=None,width=None):
    """ Function to find maximal values
    
        args:
           \n\t- x, y (array) : 1D array for the x and y position of the pixel 
           \n\t- z (array) : 1D array with the values at position (x,y) and with the same dimension as x and y
           \n\t- kind (string) : the method to determine the maximum. "maximum" only takes the max value of the z array while "peaks" is looking for the maximal peak. This last method is more robust with regards to outlier. The minimum height and width can be specified.
           \n\t- height (None, scalar or 2-element sequence) : required height of peaks. Either a number, None, an array matching x or a 2-element sequence of the former. The first element is always interpreted as the minimal and the second, if supplied, as the maximal required height.
           \n\t- width (None, scalar or 2-element sequence) : required width of peaks in samples. Either a number, None, an array matching x or a 2-element sequence of the former. The first element is always interpreted as the minimal and the second, if supplied, as the maximal required width.
        
        return:
           \n\t- x_max,y_max,z_max : three elements with the x, y position of the maximum value of the z array
    """
    if kind=="maximum":
        index=np.nanargmax(z)
        x_max=x[index]
        y_max=y[index]
        z_max=z[index]
        
    elif kind == "peaks":
        n_interp=int(np.sqrt(len(z)))
        X,Y,Z=medfilt_2D(x,y,z,n_interp)


        if height is None:
            height = np.nanmax(Z[:,int(n_interp/2)])*0.1
        if width is None:
            width = n_interp/np.nanmax(x)*0.1
        
        param_peaks=find_peaks(Z[:,int(n_interp/2)],height=height,width=width)
        peak_x=param_peaks[0][np.nanargmax(param_peaks[1]["peak_heights"])]

        param_peaks=find_peaks(Z[peak_x],height=height,width=width)
        peak_y=param_peaks[0][np.nanargmax(param_peaks[1]["peak_heights"])]
        peak_height=np.nanmax(param_peaks[1]["peak_heights"])
        
        x_max=X[peak_x,peak_y]
        y_max=Y[peak_x,peak_y]
        z_max=peak_height     

    
    return x_max,y_max,z_max

def unstructured_to_regular(x,y,z,n_interp=None):
    """ Function to convert unstructured 1D data (three vectors) in 2D grid
    
        args:
           \n\t- x, y (array) : 1D array for the x and y position of the pixel 
           \n\t- z (array) : 1D array with with the values at position (x,y), and with the same dimension as x and y
           \n\t- n_interp (int) : the number of points for the dimensions of the interpolation along x and y. if None, n_interp is set as the square root of the dimension of the z array
                
        return:
           \n\t- X,Y,Z : three meshgrids of the same dimension (n_interp x n_interp) with the x,y coordinates and the z values interpolated. The X and Y grid are linearly spaced from the minimal and maximal valeus of x and y, respectively.
            
    """
    if n_interp==None:
        n_interp=int(np.sqrt(len(z)))
        
    x_interp = np.linspace(min(x), max(x),n_interp)
    y_interp = np.linspace(min(y), max(y),n_interp)
    X, Y = np.meshgrid(x_interp, y_interp)  # 2D grid for interpolation
    Z=griddata(list(zip(x, y)), z, (X, Y), method='linear')

    return X,Y,Z

def medfilt_2D(x,y,z,kernel_size=9,n_interp=None):
    """ Function to convert unstructured 1D data (three vectors) in 2D grid for which the z values have been filtered with a 2D median filter to remove the outliers
    
        args:
           \n\t- x, y (array) : 1D array for the x and y position of the pixel 
           \n\t- z (array) : 1D array with with the values at position (x,y), and with the same dimension as x and y
           \n\t- kernel_size (int) : size of the median filter window.    
           \n\t- n_interp (int) : the number of points for the dimensions of the interpolation along x and y. if None, n_interp is set as the square root of the dimension of the z array
                
        return:
           \n\t- X,Y,Z : three meshgrids of the same dimension (n_interp x n_interp) with the x,y coordinates and the z values filtered. The X and Y grid are linearly spaced from the minimal and maximal valeus of x and y, respectively.
            
    """

    X, Y, Z_interp = unstructured_to_regular(x,y,z,n_interp)
    Z_med = medfilt2d(Z_interp,kernel_size)
    
    return X,Y,Z_med
    
def plot_map(x,y,z,ax=None,vmin=None,vmax=None,cmap="coolwarm",medfilt=True,kernel_size=9,n_interp=None, **contour_kwargs):
    """ Function to plot a 2D map from unstructured 1D data (three vectors)
    
        args:
           \n\t- x, y (array) : 1D array for the x and y position of the pixel 
           \n\t- z (array) : 1D array with with the values at position (x,y), and with the same dimension as x and y
           \n\t- ax (list of two Axes) : the axes of the subplot in which plotting the map and the color bar next to it
           \n\t- vmin, vmax (scalar) : define the data range that the colormap covers. By default, the colormap covers the complete value range of the supplied data. If vmin or vmax are not given, the default color scaling is based on levels.
           \n\t- cmap (str or Colormap) : the Colormap instance or registered colormap name used to map scalar data to colors.
           \n\t- medfilt (boolean) : if True apply a median filter on the data by interpolating it on a n_interp x n_interp grid
           \n\t- kernel_size (int) : size of the median filter window.    
           \n\t- n_interp (int) : the number of points for the dimensions of the interpolation along x and y. if None, n_interp is set as the square root of the dimension of the z array
           \n\t- contour_kwargs : this method also takes any keyword argument for the Axes.contourf() and axes.tricontourf()
           
        return:
            \n\t- fig, ax_map, ax_bar : the figure with the 2D map axe (ax_map) and the axe with the color bar (ax_bar)
            
    """
    if vmin==None:
        vmin=0

    if ax==None:
        fig,ax=plt.subplots(1,2,gridspec_kw={"wspace":0.1,"width_ratios":[5,0.2]})
    ax[0].set_xlabel("x (mm)")
    ax[0].set_ylabel("y (mm)")
  
    if medfilt:
        X,Y,Z=medfilt_2D(x,y,z,kernel_size,n_interp)
        if vmax==None:
            vmax=np.ceil(np.nanmax(Z)*1e3)/1e3
        ax[0].contourf(X, Y, Z, vmin=vmin, vmax=vmax,cmap=cmap,**contour_kwargs)

    else:
        if vmax==None:
            vmax=np.ceil(np.nanmax(z)*1e3)/1e3

        ax[0].tricontourf(x, y, z, vmin=vmin, vmax=vmax,cmap=cmap, **contour_kwargs)
        
    fig.colorbar(mpl.cm.ScalarMappable(norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax), cmap=cmap), 
                     orientation='vertical', label="Deflection (µm)",cax=ax[1])

    ax_map=ax[0]
    ax_bar=ax[1]
    
    return fig, ax_map, ax_bar

def plot_map_from_file(file_path,n_step=1,unit_mult=(1,1,1),ax=None,vmin=None,vmax=None,cmap="coolwarm",medfilt=True,kernel_size=9,n_interp=None, **contour_kwargs):
    """ Function to plot a 2D map from a file of unstructured 1D data (three vectors x,y and z)
    
        args:
           \n\t- file_path (string) : the file to read
           \n\t- n_step (int) : reduce the number of point to be plotted by taking one point each n_point index of the x, y ,z vectors
           \n\t- unit_mult (array) : array of three scalar to multiply the data of the x, y and z vector.
           \n\t- ax (list of two Axes) : the axes of the subplot in which plotting the map and the color bar next to it
           \n\t- vmin, vmax (scalar) : define the data range that the colormap covers. By default, the colormap covers the complete value range of the supplied data. If vmin or vmax are not given, the default color scaling is based on levels.
           \n\t- cmap (string or Colormap) : the Colormap instance or registered colormap name used to map scalar data to colors.
           \n\t- medfilt (boolean) : if True apply a median filter on the data by interpolating it on a n_interp x n_interp grid
           \n\t- kernel_size (int) : size of the median filter window.    
           \n\t- n_interp (int) : the number of points for the dimensions of the interpolation along x and y. if None, n_interp is set as the square root of the dimension of the z array
           \n\t- contour_kwargs : this method also takes any keyword argument for the Axes.contourf() and axes.tricontourf()
           
        return:
            \n\t- fig, ax_map, ax_bar : the figure with the 2D map axe (ax_map) and the axe with the color bar (ax_bar)
    """    
    n_step=10
    data=np.genfromtxt(file_path)
    x=data[::n_step,0] * unit_mult[0]
    y=data[::n_step,1] * unit_mult[1]
    z=data[::n_step,2] * unit_mult[2]


    if vmin==None:
        vmin=0

    if ax==None:
        fig,ax=plt.subplots(1,2,gridspec_kw={"wspace":0.1,"width_ratios":[5,0.2]})
        ax[0].set_xlabel("x (mm)")
        ax[0].set_ylabel("y (mm)")
      
    if medfilt:
        X,Y,Z=medfilt_2D(x,y,z,kernel_size,n_interp)
        if vmax==None:
            vmax=np.ceil(np.nanmax(Z)*1e3)/1e3
        ax[0].contourf(X, Y, Z, vmin=vmin, vmax=vmax,cmap=cmap,**contour_kwargs)

    else:
        if vmax==None:
            vmax=np.ceil(np.nanmax(z)*1e3)/1e3

        ax[0].tricontourf(x, y, z, vmin=vmin, vmax=vmax,cmap=cmap, **contour_kwargs)
        
    fig.colorbar(mpl.cm.ScalarMappable(norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax), cmap=cmap), 
                     orientation='vertical', label="Deflection (µm)",cax=ax[1])

    ax_map=ax[0]
    ax_bar=ax[1]
    
    return fig, ax_map, ax_bar
    
   
def plot_1D_line_from_file(file_path,unit_mult=(1,1),use_lines=None,ax=None,color_list=None,ls_list=None,marker_list=None,**plot_kwargs):
    """ Function to plot a line data from a file
    
        args:
           \n\t- file_path (string) : the file to read
           \n\t- unit_mult (array) : array of three scalar to multiply the data of the x, y and z vector.
           \n\t- use_lines (array) : list of lines to be plotted. Be careful that the number of column in the file is usually twice the number of lines (as each line has an x and z vector).
           \n\t- ax (list of two Axes) : the axes of the subplot in which plotting the map and the color bar next to it
           \n\t- color_list, ls_list, marker_list (array) : list of color, linestyle and marker to be used for the data lines found in the files. If the length of the list is smaller than the number of data lines, the last component is kept for the last data lines. 
           \n\t- plot_kwargs : this method also takes any keyword argument for the Axes.plot() function
           
        return:
            \n\t- fig, ax, data : the figure with its axe and the data array read from the file. If ax is provided, only data is returned
    """    
    if use_lines is not None:
        index=np.transpose(np.array([use_lines])) @ (2 * np.ones((1,2*len(use_lines))))+ np.array([[0,1]*len(use_lines)])
        use_col=[int(i) for i in index[0]]
    else:
        use_col=None
        
    data=np.genfromtxt(file_path,skip_header=2,delimiter="\t",usecols=use_col)
    n_lines=int(len(data[0])/2)
    
    if ax is None:
        fig,ax=plt.subplots(dpi=200)
        
        ax.set_xlabel("d (mm)")
        ax.set_ylabel("z (mm)")
    if use_lines is None:
        lines_to_plot=range(n_lines)
    else:
        lines_to_plot=range(len(use_lines))


    for i in lines_to_plot:
        d_lines=data[:,2*i]*unit_mult[0]
        z_lines=proc.moving_median(data[:,2*i+1],9)*unit_mult[1]
        if color_list is not None:
            plot_kwargs["color"]=color_list[np.min((i,len(color_list)-1))]
        if ls_list is not None:
            plot_kwargs["ls"]=ls_list[np.min((i,len(ls_list)-1))]     
            plot_kwargs.pop("linestyle",None)    
            
        if marker_list is not None:
            plot_kwargs["marker"]=marker_list[np.min((i,len(marker_list)-1))] 

        
        ax.plot(d_lines,z_lines,**plot_kwargs)

    if ax is None:        
        return fig,ax, data
    else:
        return data

    
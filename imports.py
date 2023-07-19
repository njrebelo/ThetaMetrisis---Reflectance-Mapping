import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import os
import time

"""
Created on July 4th 13:46:57 2023
This code will be used to plot maps of the ThetaMetric White Light Reflectance tool
@author: Nelson Rebelo  @ChalmersUniversity
"""

def find_in_array(array, value):
    """
    It will find the index of the matrice element with the closest value given as input

    Parameters
    ----------
    array : array of float
        Data array
    value : float
        calue to which you wish to find the index

    Returns
    -------
    idx : TYPE
        DESCRIPTION.

    """
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def get_files(dir_path):
    """
    For a given directoly will list the files into an array and the number of value

    Parameters
    ----------
    dir_path : String
        Directory path. Folder where all the data must be.

    Returns
    -------
    count : int.
    file_paths : List
        List with the directories path to the files inside the inout directory

    """
    # folder paths
    file_paths = []
    count = 0
    # Iterate directory
    for path in os.listdir(dir_path):
        # check if current path is a file
        if os.path.isfile(os.path.join(dir_path, path)):
            count += 1
            filepath = os.path.join(dir_path, path)
            file_paths.append(filepath) 
    return count,file_paths

def UploadCSVData(file_directory,num_data_points,min_wav,max_wav):
    """
    It will uplad all the data from the tool.
    
    Each spectrofram and the coordinates of each point must be put inside the same folder.

    Parameters
    ----------
    file_directory : string
        Folder path were all the data is located.
    min_wav : int
        Minimum wavelength you want to include.
    max_wav : int
        Maximum wavelength you want to include.

    Returns
    -------
    data : array
        reflectance spectrograms for each data point
    coordinates : array
        Coordinates of each data point
    wavelengths : list
        List with data points wavelength

    """
    count,file_paths = get_files(file_directory)
    
    wavelengths = np.loadtxt(file_directory+"\\0.csv",delimiter=",",skiprows=1,usecols=0)
    
    min_indx=find_in_array(wavelengths, min_wav)
    max_indx=find_in_array(wavelengths, max_wav)
    
    data = np.empty((max_indx,num_data_points))
    
    wavelengths=wavelengths[min_indx:max_indx:1]
    
    #Loop goes through the files to find the coordinates file, read, and exclude it
    for i in range(count):
        filename=file_paths[i]
        if "coordinates" in filename:
            coordinates = np.loadtxt(filename,delimiter=",",skiprows=1,usecols=(0,1,3))
            file_paths.remove(filename)
            count=count-1
            i=0
            break
    #Loop goes trhough the files in the folder to take data from each CVS and put it into one array
    for i in range(count):
        filename=file_paths[i]
        tag=int(filename[-10:].translate({ord(i): '' for i in 'Points.csv\\'}))
        data[:,tag] = np.loadtxt(filename,delimiter=",",skiprows=min_indx,usecols=(1),max_rows=max_indx)
    
    #Loop that removes data points with a too low R^2, 0.6    
    index=coordinates.shape[0]
    remove=[]
    for c in range(index):
        if coordinates[c,2]<0.6:
            remove.append(c)
    data=np.delete(data,remove,axis=1)
    coordinates=np.delete(coordinates,remove,axis=0)
    
    #Recenter de coordinates so that the center of the waffer is at (0,0)
    coordinates[:,0]=coordinates[:,0]-50
    coordinates[:,1]=coordinates[:,1]-50
            
    return data,coordinates,wavelengths


def FindCenter(data,wavelengths,smoothness):
    """
    

    Parameters
    ----------
    smoothness : Int
        Size of the kernel for the rolling average (it should not be more than 250)
    data : array
        Should come from UploadCSVData() 
    wavelengths : array
        Should come from UploadCSVData() 

    Returns
    -------
    wavelength_center : array
        Center of the stopband for each location

    """
    #Initiate array for data
    index=data.shape[1]
    wavelength_center=np.empty(index)
    
    #Parameters for rolling average
    kernel_size = smoothness
    kernel = np.ones(kernel_size) / kernel_size
    
    for i in range(index):
        #smooth data with a rolling average
        smooth_data = np.convolve(data[:,i], kernel, mode='same')
        #calculate the derivative of the raw data
        gradiant_sooth_data=np.gradient(smooth_data)
        #smooth the derivative with a rolling average
        gradiant_sooth = np.convolve(gradiant_sooth_data, kernel, mode='same')
        
        #Calculate the stopband center by calculating the middle point between the absolute maximum and absolute minimu of the derivative
        maxVal=gradiant_sooth.argmax()
        minVal=gradiant_sooth.argmin()
        center=round(maxVal+((minVal-maxVal)/2))#index
        wavelength=wavelengths[center]#What wavelength does this inx corresponde to

        #Save the result into an array
        wavelength_center[i]=wavelength
        
    return wavelength_center

def FindMaximum(data,wavelengths,smoothness):
    index=data.shape[1]

    wavelength_max=np.empty(index)

    kernel_size = smoothness
    kernel = np.ones(kernel_size) / kernel_size

    for i in range(index):
        smooth_data = np.convolve(data[:,i], kernel, mode='same')
        maxVal=smooth_data.argmax()
        
        wavelength=wavelengths[maxVal]
        
        wavelength_max[i]=wavelength
        
    return wavelength_max


def FindMaxReflectance(data,wavelengths,smoothness,wavelength):
    index=data.shape[1]

    reflectance=np.empty(index)

    wave_indx=find_in_array(wavelengths, wavelength)

    kernel_size = smoothness
    kernel = np.ones(kernel_size) / kernel_size

    for i in range(index):
        smooth_data = np.convolve(data[:,i], kernel, mode='same')
        reflectance[i] = smooth_data[wave_indx]
        
    refMax,refMin=reflectance.max(),reflectance.min()
    normalized_reflectance=(reflectance-refMin)/(refMax-refMin)
    
    return normalized_reflectance

def FilterMap(Zmap,coordinates,filterval):
    idx=Zmap.shape[0]
    
    remove=[]
    
    for i in range(idx):
        value=Zmap[i]
        if value<=filterval:
            remove.append(i)
    
    map_=np.delete(Zmap,remove)
    time.sleep(2)
    coordinates2=np.delete(coordinates,remove,axis=0)
        
    return map_,coordinates2

def plot_maps(coordinates,wavelength_center,detail,title):
    x=coordinates[:,0]
    y=coordinates[:,1]
    z=wavelength_center
    
    
    xi = np.linspace(x.min(), x.max(), 1000)
    yi = np.linspace(y.min(), y.max(), 1000)

    # Interpolate for plotting
    zi = griddata((x, y), z, (xi[None,:], yi[:,None]), method='linear')

    # I control the range of my colorbar by removing data 
    # outside of my range of interest
    zmin = np.amin(z)
    zmax = round(np.amax(z),3)
    zi[(zi<zmin) | (zi>zmax)] = None

    # Create the contour plot
    CS = plt.contourf(xi, yi, zi, detail, cmap=plt.cm.rainbow,vmax=zmax, vmin=zmin)
    #plt.xlim((-5,-3))
    #plt.ylim((-1,1))
    plt.xlabel("X position",size=10)
    plt.ylabel("Y position",size=10)
    
    if "Normalized" in title:
        plt.colorbar(label="Normalized Reflectance [a.u]")
    elif "Max":
        plt.colorbar(label="Wavelength [nm]")
    else:
        plt.colorbar(label="Center of the StopBand [nm]")
    
    plt.title(title)   
    plt.show()
    
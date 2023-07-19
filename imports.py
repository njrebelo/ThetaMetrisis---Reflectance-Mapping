import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import os
import time

"""
Created on July 4th 13:46:57 2023
This code will be used to plot maps of the 113
@author: rebelo
"""
def find_in_array(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def get_files(dir_path):
    # folder path
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

def UploadCSVData(file_directory,data_points):
    count,file_paths = get_files(file_directory)
    
    wavelengths = np.loadtxt(file_directory+"\\0.csv",delimiter=",",skiprows=250,usecols=0,max_rows=2300)
    length=wavelengths.shape[0]
    data = np.empty((length,data_points))
    
    for i in range(count):
        filename=file_paths[i]
        if "coordinates" in filename:
            coordinates = np.loadtxt(filename,delimiter=",",skiprows=1,usecols=(0,1,3))
            file_paths.remove(filename)
            count=count-1
            i=0
            break
    
    for i in range(count):
        filename=file_paths[i]
        tag=int(filename[-10:].translate({ord(i): '' for i in 'Points.csv\\'}))
        data[:,tag] = np.loadtxt(filename,delimiter=",",skiprows=250,usecols=(1),max_rows=2300)
        
    index=coordinates.shape[0]
    remove=[]
    for c in range(index):
        if coordinates[c,2]<0.6:
            remove.append(c)
    
    data=np.delete(data,remove,axis=1)
    coordinates=np.delete(coordinates,remove,axis=0)
    
    coordinates[:,0]=coordinates[:,0]-50
    coordinates[:,1]=coordinates[:,1]-50
            
    return data,coordinates,wavelengths


def FindCenter(data,wavelengths,smoothness):
    
    index=data.shape[1]
    index2=data.shape[0]
    
    wavelength_center=np.empty(index)
    
    kernel_size = smoothness
    kernel = np.ones(kernel_size) / kernel_size
    
    for i in range(index):
        smooth_data = np.convolve(data[:,i], kernel, mode='same')
        gradiant_sooth_data=np.gradient(smooth_data)
        gradiant_sooth2_raw = np.convolve(gradiant_sooth_data, kernel, mode='same')
        
        temp=gradiant_sooth2_raw
        maxVal=temp.argmax()
        minVal=temp.argmin()
        
        #Method 1
        #temp=temp[minVal:index2:1]
        #minVal=temp.argmax()
        
        #Method 2
        center=round(maxVal+((minVal-maxVal)/2))
        
        #Method3
        #temp=temp[maxVal:minVal:1]
        #center=find_in_array(temp, 0)
        
        wavelength=wavelengths[center]
        
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
    
    if detail==1:
        detail_val=30
    else:
        detail_val=10
        
    
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
    CS = plt.contourf(xi, yi, zi, detail_val, cmap=plt.cm.rainbow,
                      vmax=zmax, vmin=zmin)
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
    
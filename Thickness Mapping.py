from imports import *
#Upload the raw data and put it into matricies
file_directory="C:\\Users\\rebelo\\Desktop\\DBR Reflectance Uniformity\\Run\\30062023_150Points"
num_data_points=150#Number of dtaa points
data,coordinates,wavelengths=UploadCSVData(file_directory,num_data_points,300,700)
detail=50 #Numebr of levels in the heat map (recomended: 20-100)

#What is the center of the stop band for a DBR Structure
smoothness=50#minimum value is 40 - This value should be played with
filter_tolerance=300 #In nm
wavelength_center=FindCenter(data,wavelengths,smoothness)
plot_maps(coordinates,wavelength_center,detail,"Center of Stopband Wavelength [nm]")
filtered_wavelength_center,filtered_coordinates=FilterMap(wavelength_center,coordinates,filter_tolerance)
plot_maps(filtered_coordinates,filtered_wavelength_center,detail,"Filtered Center of Stopband Wavelength [nm]")

#What is the wavelength at which the reflectance is highest
smoothness=300#minimum value is 40 - This value should be played with
filter_tolerance=420 #In nm - points with a lower value will be removed
wavelength_max=FindMaximum(data,wavelengths,smoothness)
plot_maps(coordinates,wavelength_max,detail,"Max reflectance Wavelength [nm]")
filtered_wavelength_max,filtered_coordinates=FilterMap(wavelength_max,coordinates,filter_tolerance)
plot_maps(filtered_coordinates,filtered_wavelength_max,detail,"Filtered Max reflectance Wavelength [nm]")

#What is the reflectance for a given wacelength
filter_tolerance=0.1 #from 0 to 1
smoothness=40#minimum value is 40 - This value should be played with
wavelength=200#Target wavlength for the reflectance measurment
normalized_reflectance=FindMaxReflectance(data,wavelengths,smoothness,wavelength)
plot_maps(coordinates,normalized_reflectance,detail,f"Normalized Reflectance at {wavelength} nm")
filtered_normalized_reflectance,filtered_coordinates=FilterMap(normalized_reflectance,coordinates,filter_tolerance)
plot_maps(filtered_coordinates,filtered_normalized_reflectance,detail,f"Filtered Normalized Reflectance at {wavelength} nm")

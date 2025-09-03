import numpy as np
## Define diffraction-related parameters:
# x-ray energy in keV
E_keV = 50
# q range for fitting: (lower,upper) boundary in nm^-1
q_range = (10,60)
# path to crystal cif file
cifPath = '/Users/moritz/Documents/code/modelling_cajetan/scripts_cajetan/CIF-Files/ti64_alpha_modified.cif'
# approximate crystal size along (a,b,c)-axes in nm
crystalsize = (15,15,15)
# angular sampling
sampling = 'cubochoric' # or 'simple' (legacy)
# angular sampling resolution
dchi = 2*np.pi / 120



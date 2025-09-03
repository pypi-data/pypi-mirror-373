# Data path and names
path_in = 'path/to/your/experiment/overview_file.h5' # .h5 file with links to the data
h5_proj_pattern = 'mysample*.1' # projection names, * is a placeholder
# .h5 internal paths:
h5_data_path = 'measurement/eiger'
## required metadata:
h5_tilt_angle_path = 'instrument/positioners/tilt' # tilt angle / None if retrieved from name (convention: .._{tilt}_{rot}_diff...h5)
h5_rot_angle_path = 'instrument/positioners/rot' # rotation angle / None if retrieved from name (... use m for minus and p for point)
h5_ty_path = 'measurement/dty' # horizontal position
h5_tz_path = 'measurement/dtz' # vertical position
### required if in scanning mode:
h5_nfast_path = 'technique/dim0' # fast axis number of points
h5_nslow_path = 'technique/dim1' # slow axis number of points
## optional metadata:
h5_ion_path = 'measurement/ion' # ionization chamber/I_0 counter if present else None
h5_data_transmission_path = 'measurement/transmission_counter' # your path or None

# Parameters for pyFAI azimuthal integration
rad_range = [0.01, 37] # radial range
rad_unit = 'q_nm^-1' # radial parameter and unit ('q_nm^-1', ''2th_deg', etc)
azi_range = [-180, 180] # azimuthal range in degree
npt_rad = 100 # number of points radial direction
npt_azi = 120 # number of points azimuthal direction
npt_rad_1D = 2000 # number of points radial direction
int_method=('bbox','csr','opencl') # pyFAI integration methods, for GPU change 'cython' to 'opencl'
poni_path = 'path/to/your/poni_file.poni'
mask_path = 'path/to/your/mask.edf'
polarisation_factor= 0.95 # polarisation factor, usually 0.95 or 0.99
solidangle_correction = True
flatfield_correction = None #or /path/to/file
darkcurrent_correction = None #or /path/to/file

# Integration mode
mode = 2 # 1: 1D, 2: 2D, 3: both

# Parallelisation (only relevant for mode=parallel)
n_tasks = 8 # number of integrations performed in parallel
cores_per_task = 16 # size of the cluster that performs a single integration
# if opencl is used, cores_per_task is ignored
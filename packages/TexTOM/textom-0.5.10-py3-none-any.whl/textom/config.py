import numpy as np # don't delete this line
##################################################

# Define how many cores you want to use 
n_threads = 128 

# Choose if you want to use a GPU for alignment
use_gpu = False
# needs cudatoolkit: pip install cudatoolkit

# Choose your precision
# recommended np.float64 for double or np.float32 for single precision
data_type = np.float32

# turn on wise phrases at the start of TexTOM
fun_mode = False
import os
# Housekeeping, set num threads to 1 before importing numpy
os.environ["MKL_NUM_THREADS"] = "1" 
os.environ["NUMEXPR_NUM_THREADS"] = "1" 
os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np
import pickle

from src.model import model
from textom.src.data import data
import src.handle as hdl
import textom.src.symmetries as sym
from config import pickle_path
#################### general input ####################
# Load the model
mod = model( 'input.input_simsample' )

# the following should be compatible with the field of view in the input file:
size = np.array((20,20,20)) # No. of voxels in each direction
padding = 10 # No of empty voxels added around the sample
size = np.array((2,2,2)) # No. of voxels in each direction
padding = 1 # No of empty voxels added around the sample

# output file path from step1
coefficient_file = 'output/gaussian_n12_std40.txt'

poisson_noise = True
max_counts = 200

###############################################
size_pad = size + 2*padding
if padding:
    voxel_mask = np.zeros(size_pad)
    voxel_mask[ padding:-padding,padding:-padding,padding:-padding ] = 1
else:
    voxel_mask = np.ones(size_pad )
n_vox = voxel_mask.size
voxel_mask = np.where( voxel_mask.flatten() )[0]
with open('data/voxelmask_%s.txt' % mod.title ,'w') as fid:
    [fid.write('%d\n' % idx) for idx in voxel_mask]

################# sample layout #################
    
np.random.seed(2)
scaling = np.zeros(n_vox, np.float64) # scaling factor on each voxel
scaling[voxel_mask] = 0.5 + 0.5 * np.random.rand(voxel_mask.size)

mu_i = np.zeros( (n_vox,3), np.float64)
mu_i[voxel_mask] = np.take( mod.Gc,
 # for generating a sample with stripes with a random mean orientation 
 # in each stripe
        np.repeat( np.array([            
        np.random.randint(0,mod.Gc.shape[0],size[0]) for _ in range(size[1])
        ]), size[2], axis=0).flatten() 
    , axis=0)

###############################################

# symmetry generators for the point group:
gen = sym.generators(mod.symmetry)

# set to the HSH-order used for the gaussian
i0 = coefficient_file.find('_n')
i1 = coefficient_file.find('_', i0+1)
nmax = int( coefficient_file[i0+2 : i1] )
mod.set_orders(nmax)
C0 = np.genfromtxt(coefficient_file)

# make rotation matrices for mean orientation of each voxel
Rv = mod.get_Rs_stack( mu_i )
C = Rv @ C0
C = np.tile(scaling,(C.shape[1],1)).T*C
path = 'output/coefficients_%s.txt' % mod.title 
hdl.save_coefficients( C, mod, path )
print('Saved sHSH coefficients to file: %s' % path)

# calculate images from all beam directions
for g in range(mod.Beams.shape[0]):
    mod.projection(g, C)

# Add Poisson noise to the generated data
images = mod.images * max_counts / mod.images.max()
images[images<0] = 1
images = np.random.poisson(images).astype(np.float64)

# Save the data for further use
class data:
    def __init__(self, images):
        setattr( self, 'data', images)
        setattr( self, 'mask_detector', np.ones(images.shape[2], bool) )
dat = data( images )
path = os.path.join(pickle_path, 'data_%s.txt' % mod.title)
with open( path, 'wb' ) as fid:
    pickle.dump(dat, fid)
print('Saved simulated data to file: %s' % path)

# Write a file containing the mean orientations
a_pref, b_pref, c_pref = mod.abc_pref_sample( mu_i )
path = 'output/sim_%s.vtk' % mod.title
hdl.write_vtk_direct( mod, path, mod.mask_voxels,
                    scalars = [
                        ['scaling', scaling],
                    ],
                    vectors = [
                    ['mu', mu_i],
                    ['a_pref', a_pref],
                    ['b_pref', b_pref],
                    ['c_pref', c_pref],
                    ]
                )


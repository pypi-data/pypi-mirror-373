import os
import glob
import numpy as np
from time import time
import sys, shutil
# from ase.io import read # for reading .cif files
import importlib as imp # for reading input files
from numba import njit, prange
import h5py
from orix.sampling import get_sample_fundamental
import orix.quaternion.symmetry as osym 
from orix.quaternion import Orientation, Rotation
from scipy import ndimage
from ase.io import read # for reading .cif files

# domestic
from . import handle as hdl
from . import hsh
from . import rotation as rot
from . import symmetries as sym
from . import mask as msk
from .misc import meshgrid, integrate_c, erf, cp_addno, import_module_from_path
from . import model_crystal as cry
from ..config import data_type
# from . import model_difflets_odftt as dif

class model:
    """ A class to that contains the theoretical description of Texture tomography.

    Takes input from a designated input file, see input/input_template.py
    for how it has to be stuctured
    """

    def __init__(self, sample_dir, classic=True, single=False, q_det=False, chi_det=False, light=False, no_Isc=False):
        """Initializes the texture tomography model class

        Calculates arrays that do not need to be updated when fitting/plotting

        Parameters
        ----------
        startFileName : str
            path to the input file
        single : bool
            set to True if you just want to calculate a single image
            disables the whole tomography part
        
        Attributes created
        ------------
        see returned variables in input file
        """

        print("Initialize model")
        self.title = os.path.basename(sample_dir)
        self.path_analysis = os.path.join(sample_dir,'analysis')
        self.light = light
        self.no_Isc = no_Isc

        ################ Projectors
        if single: # initializes parameters if only a single image is produced
            self._init_single()
        else:
            if os.path.isfile(os.path.join(sample_dir,'analysis','projectors.h5')): # loads a tomo model if it exists
                t0 = time()
                with h5py.File( os.path.join(sample_dir,'analysis','projectors.h5'), 'r' ) as hf:
                    self.Omega = hf['Omega'][()].astype(data_type)
                    self.Kappa = hf['Kappa'][()].astype(data_type)
                    self.Gs = hf['Gs'][()].astype(data_type)
                    self.tomogram = hf['tomogram'][()].astype(data_type)
                    self.Ty = hf['Ty'][()].astype(data_type)
                    self.Tz = hf['Tz'][()].astype(data_type)
                    self.fov = hf['fov'][()]
                    self.x_p = hf['x_p'][()].astype(data_type)
                    self.p0 = hf['p0'][()]
                    self.nVox = hf['nVox'][()]
                    self.mask_voxels = hf['mask_voxels'][()]
                    # self.cutoff_low = hf['cutoff_low'][()]
                    if not light:
                        self.Beams = hf['Beams'][()].astype(data_type)
                        self.iBeams = hf['iBeams'][()]
                    if 'fov_single' in hf:
                        self.fov_single = hf['fov_single'][()]
                    
                print("\tLoaded projectors from analysis/projectors.h5 (%2.2f s)" % ( (time()-t0)) )
            
            else:
                if os.path.isfile(os.path.join(sample_dir,'analysis/alignment_result.h5')):
                    self.Kappa, self.Omega, self.shifty, self.shiftz, self.tomogram, self.sinogram = hdl.load_shifts_mumott(
                         os.path.join(sample_dir,'analysis/alignment_result.h5') )

                    print('\tImporting geometry')
                    geo = import_module_from_path('geometry', os.path.join(sample_dir,'analysis/geometry.py'))

                    # calculate beam intensities and save them
                    self._init_projectors(geo)

                    print('\tSaving results to sample path analysis/projectors.h5')
                    with h5py.File( os.path.join(sample_dir,'analysis','projectors.h5'), 'w' ) as hf:
                        hf.create_dataset('Omega', data=self.Omega)
                        hf.create_dataset('Kappa', data=self.Kappa) 
                        hf.create_dataset('Gs', data=self.Gs) 
                        hf.create_dataset('tomogram', data=self.tomogram, compression="lzf") 
                        hf.create_dataset('Ty', data=self.Ty) 
                        hf.create_dataset('Tz', data=self.Tz) 
                        hf.create_dataset('fov', data=self.fov) 
                        hf.create_dataset('x_p', data=self.x_p, compression="lzf") 
                        hf.create_dataset('p0', data=self.p0) 
                        hf.create_dataset('nVox', data=self.nVox) 
                        hf.create_dataset('mask_voxels', data=self.mask_voxels) 
                        # hf.create_dataset('cutoff_low', data=self.cutoff_low) 
                        hf.create_dataset('Beams', data=self.Beams, compression="lzf") 
                        hf.create_dataset('iBeams', data=self.iBeams, compression="lzf") 
                        hf.create_dataset('shifty', data=self.shifty) 
                        hf.create_dataset('shiftz', data=self.shiftz) 
                        if hasattr( self, 'fov_single' ):
                            hf.create_dataset('fov_single', data=self.fov_single) 
                    # hdl.save_pickle( self.tomo_pickle, self, 'tomo' )
                else:
                    print('Alignment not done, not calculating beam intensities\n\trun align_data() first')
        
        ################# Diffractlets
        self.classic = classic
        if classic:
            if os.path.isfile(os.path.join(sample_dir,'analysis','diffractlets.h5')): # loads a crystal if it exists
                t0 = time()
                with h5py.File( os.path.join(sample_dir,'analysis','diffractlets.h5'), 'r' ) as hf:
                    self.symmetry = hf['symmetry'][()].decode('utf-8')
                    self.Gc = hf['Gc'][()].astype(data_type)
                    self.dV = hf['dV'][()].astype(data_type)
                    self.V_fz = hf['V_fz'][()].astype(data_type)
                    self.detShape = hf['detShape'][()]
                    self.Chi_det = hf['Chi_det'][()].astype(data_type)
                    self.Qq_det = hf['Qq_det'][()].astype(data_type)
                    if not (light or no_Isc):
                        self.Isc = hf['Isc'][()].astype(data_type)
                        self.difflets = hf['difflets'][()].astype(data_type)
                    # self.q = hf['q'][()].astype(data_type)
                    self.lattice_vectors = hf['lattice_vectors'][()].astype(data_type)
                    self.E_keV = hf['Energy_keV'][()]
                    try:
                        self.sampling = hf['sampling'][()]
                    except:
                        self.sampling = 'simple'
                # self = hdl.load_pickle( self.diff_pickle, self )
                self.geo = import_module_from_path('geometry', os.path.join(sample_dir,'analysis/geometry.py'))
                print("\tLoaded single crystal images from analysis/diffractlets.h5 (%2.2f s)" % ( (time()-t0)) )
            else:
                crystal_path = os.path.join(sample_dir,'analysis','crystal.py')
                cr = import_module_from_path('crystal', crystal_path)
                # Import all variables from the imported_file module
                for var_name in dir(cr):
                    # Filter out special attributes and methods
                    if not var_name.startswith("__"):
                        # Set the attribute to self
                        setattr(self, var_name, getattr(cr, var_name))

                crystal_data = cry.parse_cif(os.path.join(sample_dir,self.cifPath))
                self.symmetry = sym.get_proper_point_group(crystal_data['space_group'])

                # this defines a grid of angles for crystallite rotation and related quantities
                self.Gc, self.dV, self.V_fz = rot.define_angles(self.dchi, self.sampling, self.symmetry)

                if np.any(q_det) and np.any(chi_det):
                    self.q_det = q_det
                    self.chi_det = chi_det * np.pi/180
                else:
                    # get detector coordinates from integrated data
                    int_data_file = glob.glob(os.path.join(sample_dir,'data_integrated','*h5'))[0]
                    with h5py.File(os.path.join(sample_dir,'data_integrated',int_data_file),'r') as hf:
                        self.q_det = hf['radial_units'][0]
                        self.chi_det = hf['azimuthal_units'][0] * np.pi/180
                    # adapt q to desired range
                    self.q_det = self.q_det[np.logical_and(
                        self.q_det > cr.q_range[0],
                        self.q_det < cr.q_range[1],
                    )]

                print('\tImporting geometry')
                self.geo = import_module_from_path('geometry', os.path.join(sample_dir,'analysis/geometry.py'))

                # calculate single crystal diffraction patterns and save them
                self._init_diffractlets()

                print('\tSaving results to sample path analysis/diffractlets.h5')
                with h5py.File( os.path.join(sample_dir,'analysis','diffractlets.h5'), 'w' ) as hf:
                    if not no_Isc:
                        hf.create_dataset('Isc', data=self.Isc)#, compression="lzf") 
                        hf.create_dataset('difflets', data=self.difflets) 
                    hf.create_dataset('cif_file', data=cr.cifPath)
                    hf.create_dataset('Energy_keV', data=cr.E_keV)
                    hf.create_dataset('Ang_resolution', data=self.dchi*180/np.pi)
                    hf.create_dataset('sampling',data=cr.sampling)
                    # hf.create_dataset('q_det', data=self.q_det)
                    hf.create_dataset('crystal_size', data=cr.crystalsize)
                    hf.create_dataset('symmetry', data=self.symmetry)
                    hf.create_dataset('Gc', data=self.Gc)
                    hf.create_dataset('dV', data=self.dV) 
                    hf.create_dataset('V_fz', data=self.V_fz) 
                    hf.create_dataset('detShape', data=self.detShape) 
                    hf.create_dataset('Chi_det', data=self.Chi_det) 
                    hf.create_dataset('Qq_det', data=self.Qq_det) 
                    hf.create_dataset('lattice_vectors', data=self.lattice_vectors)

            self.classic=True
            self.Gc[self.Gc[:,0]==0,0] = 1e-9 # maybe this helps against instabilities

        else:
            ############################ new mode ####################################################
            mode = 'hsh'
            difflets_path = os.path.join(sample_dir,'analysis',f'difflets_{mode}.h5')
            if os.path.isfile(difflets_path):
                with h5py.File(difflets_path, 'r') as hf:
                    self.difflets = hf['difflets'][()]
                    self.Qq_det = hf['q_values'][()]
                    self.Chi_det = hf['chi_values'][()]
                    self.symmetry = hf['symmetry'][()].decode('utf-8')

            else:
                # print('\tImporting geometry')
                geo = import_module_from_path('geometry', os.path.join(sample_dir,'analysis/geometry.py'))

                # get detector coordinates
                if np.any(q_det) and np.any(chi_det):
                    self.q_det = q_det
                    self.chi_det = chi_det * np.pi/180
                else:
                    # get detector coordinates from integrated data
                    int_data_file = glob.glob(os.path.join(sample_dir,'data_integrated','*h5'))[0]
                    with h5py.File(os.path.join(sample_dir,'data_integrated',int_data_file),'r') as hf:
                        self.q_det = hf['radial_units'][0]
                        self.chi_det = hf['azimuthal_units'][0] * np.pi/180
                    # adapt q to desired range
                    self.q_det = self.q_det[np.logical_and(
                        self.q_det > cr.q_range[0],
                        self.q_det < cr.q_range[1],
                    )]

                # print('calculating diffractlets')                
                crystal_path = os.path.join(sample_dir,'analysis','crystal.py')
                cr = import_module_from_path('crystal', crystal_path)
                sample_rotations = rot.QfromOTP(self.Gs)
                self.Qq_det, self.Chi_det, self.hkl, self.difflets, self.symmetry = cry.get_diffractlets(
                                cr, self.chi_det, geo, 
                                sample_rotations, max_order = 4,
                                cutoff_structure_factor=1e-2, mode=mode )
                # cry.plot_diffractlet(Qq_det, Chi_det, hkl, difflets[0], q_bins=np.linspace(*cr.q_range),
                #                      cmap='plasma', sym_cmap=False, logscale=True
                #                      )
                # cry.plot_diffractlet(Qq_det, Chi_det, hkl, difflets[1], q_bins=np.linspace(*cr.q_range),
                #                      cmap='plasma', sym_cmap=False, logscale=True
                #                      )
                with h5py.File(difflets_path,'w') as hf:
                    hf.create_dataset('difflets', data=self.difflets)
                    hf.create_dataset('cif_file', data=cr.cifPath)
                    hf.create_dataset('Energy_keV', data=cr.E_keV)
                    hf.create_dataset('q_values', data=self.Qq_det)
                    hf.create_dataset('chi_values', data=self.Chi_det)
                    hf.create_dataset('sample_rotations', data=self.Gs)
                    # hf.create_dataset('orders', data=self.ns)
                    hf.create_dataset('symmetry', data=self.symmetry)


            # mum_file = os.path.join(path,'analysis','data_mumott.h5')

            # crystal_path = os.path.join(path,'analysis','crystal.py')
            # cr = import_module_from_path('crystal', crystal_path)
            # # Import all variables from the imported_file module
            # for var_name in dir(cr):
            #     # Filter out special attributes and methods
            #     if not var_name.startswith("__"):
            #         # Set the attribute to self
            #         setattr(self, var_name, getattr(cr, var_name))

            # peak_regions_file = os.path.join(path,'analysis','peak_regions.txt')
            # peak_reg = np.genfromtxt(peak_regions_file)
            # peak_reg = peak_reg.reshape( (peak_reg.size//2, 2)  )
            # q_peaks = np.mean(peak_reg, axis=1)
            # h = 4.135667696e-18 # keV*s
            # c = 299792458 # m/s
            # lam = h*c*1e9 / self.E_keV # wavelength from energy 1.23984/E_keV
            # two_theta_values = 2*np.arcsin( q_peaks*lam /(4*np.pi))

            # hkl_file = os.path.join(path,'analysis','hkl_list.txt')
            # hkl_list = np.genfromtxt(hkl_file, delimiter=',')
            #         #    [(1, 1, 1),
            #         #     (2, 0, 0),
            #         #     (2, 2, 0),]
            # from ..ressources.odftt.crystallography import cubic, hexagonal
            # A, B = hexagonal() # cubic()
            # h_vectors = [B @ hkl for hkl in hkl_list]

            # self.symmetry = '622'
            # self.q = q_peaks
            # self.detShape = (len(h_vectors), cr.chi.shape[0])

            # self.difflets = dif.make_difflets(mum_file, cr.chi, two_theta_values, h_vectors, 
            #                     cr.grid_resolution, cr.kernel_sigma)
            
            # with h5py.File(difflets_path, 'r') as hf:
            #     self.difflets = hf['difflets']
            #     self.classic=False

    """
    Initialisation functions
    """                 
    def sample_SO3(self):
        """Defines the grid of angles for crystallite rotation

        Attributes created
        ------------
        Gc : 2D ndarray, float
            register of axis-angle rotations
            dim: 0: rotation index, 1: [omega, theta, phi]
        dV : 1D ndarray, float
            volume element for integrating over the odf
            dim: 0: rotation index
        V_fz : float
            volume of the fundamental zone
        """
        try:
            if self.sampling=='cubochoric':
                pg = getattr( osym, sym.get_SFnotation( self.symmetry ) )
                rot_orix = get_sample_fundamental(
                        self.dchi*180/np.pi, 
                        point_group= pg,
                        method=self.sampling
                )
                self.Gc = rot.OTPfromQ(rot_orix.data)

                # cubochoric is equal volume mapped
                # Sing and De Graef, 2016
                self.dV = 1/self.dchi**3 * np.ones( 
                    self.Gc.shape[0], data_type)
        except:
            self.sampling = 'simple'
        
        if self.sampling == 'simple':
            ## set up angles used to rotate the single crystal patterns
            ome = np.linspace( 
                self.dchi/2, np.pi-self.dchi/2, int(np.pi/self.dchi), endpoint=True)
            tta = np.linspace( 
                self.dchi/2, np.pi-self.dchi/2, int(np.pi/self.dchi), endpoint=True)
            phi = np.linspace( 0, 2*np.pi, int(2*np.pi/self.dchi), endpoint=False)
            TTA, PHI, OME = np.meshgrid(tta, phi, ome)
            Ome, Tta, Phi = OME.flatten(), TTA.flatten(), PHI.flatten()
            self.Gc = np.column_stack((Ome,Tta,Phi))

            ## apply the crystal symmetry conditions on Tta, Phi, Ome, so in the following 
            # only these are calculated by only choosing rotations in the fundamental zone 
            # of the proper point group
            fz = sym.zone(self.symmetry,self.Gc)
            Tta, Phi, Ome = Tta[fz], Phi[fz], Ome[fz] # these are the angles that effectively will be used
            self.Gc = self.Gc[fz] # cut away the redundand ones from the rotation array

            # volume element for integrating over the odf
            # see Mason/Patala, arXiv (2019), appendix C
            # omitted factor 1/2 here, since we use omega only from 0 to pi
            self.dV = np.sin(Ome/2)**2 * np.sin(Tta) * self.dchi**3 

        # import matplotlib.pyplot as plt
        # fig = plt.figure(figsize=(15, 10))
        # scatter_kwargs = dict(
        #     projection="rodrigues",
        #     figure=fig,
        #     wireframe_kwargs=dict(color="k", linewidth=1, alpha=0.1),
        #     s=5,
        # )
        # ori_plain = Orientation(Rotation([rot.QfromOTP( self.Gc)]), symmetry=pg).get_random_sample(10000)
        # ori_orix = Orientation(rot_orix, symmetry=pg).get_random_sample(10000)
        # ori_orix.scatter(position=231, c="C0", **scatter_kwargs)
        # ori_plain.scatter(position=232, c="C1", **scatter_kwargs)
        # # ori_quat2.scatter(position=233, c="C2", **scatter_kwargs)

        # ori_orix.scatter(position=234, c="C0", **scatter_kwargs)
        # ori_plain.scatter(position=235, c="C1", **scatter_kwargs)
        # # ori_quat2.scatter(position=236, c="C2", **scatter_kwargs)

        # titles = ["cubochoric", "plain"]#, "quaternion"]
        # for i, title in zip([0, 1], titles):
        #     fig.axes[i].view_init(elev=90, azim=0)
        #     fig.axes[i].set_title(titles[i])
        # for i in [2, 3]:
        #     fig.axes[i].view_init(elev=0, azim=0)

        # volume of the fundamental zone [rad^3]
        self.V_fz = self.dV.sum()

    def _init_diffractlets(self):
        """Calculates single crystal diffraction patterns and powder pattern

        Attributes created
        ------------
        Qq_det, Chi_det : 1D ndarray, float
            flattened meshgrids of detector point polar coordinates
            dim: 0: detector point index
        detShape : tuple, int
            number of detector points (n_q, n_chi)
        Natom : int
            number of atoms in the simulated crystal
        Isc : 2D ndarray, float
            flattened meshgrids of detector point polar coordinates
            dim: 0: rotation index, dim 1: detector point index
        difflets : 2D ndarray, float
            powder pattern/zero order diffractlet (others to be added)
            dim: 0: sHSH index, 1: detector point index
        """
        # ## calculate Ewald's sphere for each rotation given by the HSHs
        # # calculate the incoming wavevector
        # h = 4.135667696e-18 # keV*s
        # c = 299792458 # m/s
        # kXray = 2*np.pi * self.E_keV / (h*c*1e9) # wavevector in 1/nm

        # ####################### this should be imported from data!
        # # coordinates on detector
        # self.Qq_det, self.Chi_det, self.detShape = rot.qchi(self.q, self.chi)
        # # azimutal angle with respect to the beam for the points of Ewald's sphere 
        # #   (spherical coordinates with the azimuth at +x)
        # Tta_ew = np.pi - np.arctan( np.sqrt(kXray**2-self.Qq_det**2/4) *2/self.Qq_det ) 
        # # coordinates of Ewald's sphere in reciprocal space
        # QX_ew = self.Qq_det * np.cos(Tta_ew)
        # QY_ew = self.Qq_det * np.sin(Tta_ew) * np.sin(self.Chi_det)
        # QZ_ew = self.Qq_det * np.sin(Tta_ew )* np.cos(self.Chi_det)
        # Q_ew = np.column_stack([QX_ew,QY_ew,QZ_ew])
        
        # # import matplotlib.pyplot as plt
        # # fig = plt.figure()
        # # ax = fig.add_subplot(111, projection='3d')
        # # ax.scatter(QX_ew,QY_ew,QZ_ew,alpha=0.1)
        # # ax.scatter(QX_ew[0],QY_ew[0],QZ_ew[0], c='r')
        # # ax.scatter(QX_ew[10],QY_ew[10],QZ_ew[10], c='r')
        # # ax.set_xlabel('x')
        # # ax.set_ylabel('y')
        # # ax.set_zlabel('z')
        # #####################################################################
        # number of points on detector
        # Ndet = Tta_ew.shape[0]
        # coordinates on detector
        self.Qq_det, self.Chi_det, self.detShape = rot.qchi(self.q_det, self.chi_det)

        QX_ew,QY_ew,QZ_ew = self.get_reciprocal_space_coordinates()
        Q_ew = np.column_stack([QX_ew,QY_ew,QZ_ew])
        Ndet = Q_ew.shape[0]

        # make the real space crystal
        crystal_data = cry.parse_cif(self.cifPath)
        ## the following functions are currently not functional
        # pos = crystal_data['cartesian_positions']/10 # coordinates of all atoms in the unit cell converted to nm
        # chem = crystal_data['atom_list'] # chemical symbols of all atoms in the unit cell
        # self.lattice_vectors = crystal_data['lattice_vectors']/10
        ###
        self.symmetry = sym.get_proper_point_group(crystal_data['space_group'])

        unit = read(self.cifPath) # Read the CIF file via ase
        uc_pos = unit.positions/10 # coordinates of all atoms converted to nm
        uc_chem = np.array( unit.get_chemical_symbols() ) # chemical symbols of all atoms
        elements = np.unique(uc_chem) # all used elements
        Nel = elements.size # number of elements
        self.lattice_vectors = np.array( unit.get_cell() )/10 # converted to nm

        #lengths of lattice vectors in their "main" direction
        a=self.lattice_vectors[0][0]  
        b=self.lattice_vectors[1][1]
        c=self.lattice_vectors[2][2]
        
        crystal_dims = self.crystalsize # (20,20,50) #in nm    
        
        #crystalsize in powers of two along the lattice direction, close to the desired input
        crystalsize = 2**np.round(np.log2([crystal_dims[0]/a, crystal_dims[1]/b, crystal_dims[2]/c]))
        crystalsize = crystalsize.astype(int)

        print("\t Size of simulated crystal:", crystalsize,"\n \t Which equals:", crystalsize*np.array([a,b,c]),"nm")
        print('\t Number of lattice points: %u' % np.prod(crystalsize) ) 
        print("\t Unit cell size:", uc_pos.shape[0])
        # Get atomic form factor coefficients from lookup table parametrized trough a, b, c
        ff_path = hdl.get_file_path('textom',
        os.path.join('ressources','atomic_formfactors.txt'))
        ffcoeff = np.genfromtxt( ff_path, dtype="|U8", skip_header=2 )
        ffcoeff_used = np.array([ ffcoeff[ np.where( el == ffcoeff )[0][0], 1: ] for el in elements]).astype(data_type)
        a = ffcoeff_used[:,0:-1:2]
        b = ffcoeff_used[:,1:-1:2]
        c = ffcoeff_used[:,-1]

        FF_element = np.empty( (Nel, Ndet), np.float64 ) # atomic form factors for all used elements
        for k in range(Nel):
            A, Qf = np.meshgrid( a[k], self.q_det ) 
            B, _ = np.meshgrid( b[k], self.q_det )
            C = c[k]
            #Calculate form factor http://lampx.tugraz.at/~hadley/ss1/crystaldiffraction/atomicformfactors/formfactors.php
            F = ( A * np.exp( -B * (Qf/(4*np.pi))**2  ) ).sum(axis=1) + C
            _, FF = np.meshgrid( self.Chi_det.reshape(self.detShape)[0], F )
            FF_element[k,:] = FF.flatten()

        # rotate the crystal in all chosen orientations 
        uc_pos_rot = rot.stack_mrot( uc_pos.astype(data_type), self.Gc).astype(np.float64)
        lattice_vectors_rot = rot.stack_mrot( self.lattice_vectors.astype(data_type), self.Gc).astype(np.float64)

        #bool mask for the unit cell
        bool_pos_element = np.empty( (Nel, uc_chem.shape[0]), bool )
        for k in range(Nel):
            # determinate the positions of element k 
            bool_pos_element[k,:] = uc_chem == elements[k]

        if not self.no_Isc:
            # calculate structure factors
            print('\t recursively calculating single crystal diffraction patterns \n\t\t(long calculation time possible, do not close terminal)')
            t0 = time()
            self.Isc = single_crystal_images( Q_ew.astype(np.float64),
                            uc_pos_rot, bool_pos_element, FF_element, crystalsize, lattice_vectors_rot).astype(data_type)
            print('\t\t took %.2f seconds' % ((time()-t0)) )

            # Calculate powder pattern/zero order diffractlet
            # #t1 = time()
            # powder = ( (1/V_fz * dV) @ Isc ).reshape(detShape).sum(axis=1) # integrate over all rotations
            # Calculate powder pattern/zero order diffractlet
            difflet0_2D = ( self.dV @ self.Isc ).reshape(self.detShape) # integrate over all rotations
            for iq in range( self.detShape[0] ): 
                difflet0_2D[iq, :] = np.mean(difflet0_2D[iq, :]) # flatten it over the angles
            self.difflets = difflet0_2D.flatten().reshape([1,difflet0_2D.size])

    def _init_projectors(self, geo):
        """Calculates the beam intensity in each voxel for each configuration

        Attributes created
        ------------
        tomogram : 1D ndarray, float
            saves the tomogram loaded from the alignment by SASTT
            dim: 0: voxel index
        nVox : int
            number of voxels simulated
        Omega, Kappa : 1D ndarray, float
            sample rotation angles (Euler) for each unique rotation
            dim: 0: rotation index
        Gs : 2D ndarray, float
            sample rotation angles (axis-angle) for each unique rotation
            dim: 0: rotation index, 1: [omega, theta, phi]     
        Ty, Tz : 1D ndarray, float
            y- and z-distance from the central pixel for each translation
            dim: 0: translation index
        t0 : int
            translation index of the central pixel
        x_p : 2D ndarray, float
            array of coordinates of each voxel
            dim: 0: voxel index, 1: [x,y,z]
        p0 : int
            index of the central voxel (rotation center)
        mask_voxels : 1D ndarray, bool
            mask for including the voxel in the analysis or not
            dim: 0: voxel index
        cutoff_low : float
            chosen level below which voxels are masked
        Beams : 3D ndarray, float
            array of X-ray beam intensity in each voxel for each rotation
            and translation state
            dim: 0: rotation, 1: translation, 2: voxel sparse index
        iBeams : 3D ndarray, int
            array of indices for the sparse Beams array
            dim: 0: rotation, 1: translation, 2: voxel sparse index
        """
        # define sample size and field of view
        self.fov = np.array( self.tomogram.shape[1:3], np.int32)
        self.nVox = np.array( self.tomogram.shape[:3], np.int32)

        # sample rotation angles
        Nrot = self.Omega.shape[0] # number of sample rotations

        # # convert omega/kappa rotations in lab frame to axis/angle notation via quaternions
        Q_ome = np.column_stack(
                (np.cos(self.Omega/2),np.outer(np.sin(self.Omega/2), np.array(geo.inner_axis))))
        Q_kap = np.column_stack(
                (np.cos(self.Kappa/2),np.outer(np.sin(self.Kappa/2), np.array(geo.outer_axis))))
        # zer = np.zeros_like(self.Omega)
        # Q_ome = np.column_stack(
        #         (np.cos(self.Omega/2), zer, zer, np.sin(self.Omega/2) ) )
        # #                         , sin(inner_angle)*(0,0,1)
        # Q_kap = np.column_stack(
        #         (np.cos(self.Kappa/2), zer, np.sin(self.Kappa/2), zer ) )
        Q_srot = np.array([rot.quaternion_multiply(qk,qo) for qo,qk in zip(Q_ome,Q_kap)])
        self.Gs = rot.OTPfromQ(Q_srot)

        # Set up translations of the beam
        ny = self.fov[0]
        nz = self.fov[1]
        ty = np.arange(ny)-ny/2+1/2 # scan from left to right
        tz = np.arange(nz)-nz/2+1/2 # scan up to down
        TZ,TY = np.meshgrid(tz,ty)
        self.Ty,self.Tz = TY.flatten(), TZ.flatten()
        ntrans = self.Ty.shape[0]

        # voxel coordinates
        xy = np.arange(ny)-ny/2+1/2
        z = np.arange(nz)-nz/2+1/2
        YY,XX,ZZ = np.meshgrid(xy,xy,z)
        Xb = XX.flatten()
        Yb = YY.flatten()
        Zb = ZZ.flatten()
        self.x_p = np.column_stack([Xb,Yb,Zb]) # voxel coordinates for (omega, kappa) = (0,0)
        self.p0 = int(len(Xb)/2) # central voxel

        # mask the sample
        if not os.path.isfile(os.path.join(self.path_analysis,'voxelmask.txt')):
            print('Identify your sample by drawing a rectangle over it')
            # find the images at angles to check sample geometry
            to_try = np.array([[0,0],[0,np.pi/2]])
            rgl = []
            for b in to_try:
                A = np.column_stack((self.Kappa, self.Omega))
                shy, shz = self.shifty, self.shiftz
                # check which of the projections is closest to the angles defined in totry
                distances = np.linalg.norm(A - b, axis=1)
                g_match = np.argmin(distances)
                # plot the projection in textom scale
                Y,Z = np.meshgrid(ty+shy[g_match],tz+shz[g_match])
                rgl.append( msk.draw_rectangle_on_image( 
                    self.sinogram[:,:,g_match].T, xy=(Y,Z),
                    title=f'Projection No {g_match}, tilt = {A[g_match,0]*180/np.pi} \u00b0, rot = {A[g_match,1]*180/np.pi} \u00b0' 
                ))

            zmin = np.min( [rgl[0].start_point[1], rgl[0].end_point[1],
                            rgl[1].start_point[1], rgl[1].end_point[1],])
            zmax = np.max( [rgl[0].start_point[1], rgl[0].end_point[1],
                            rgl[1].start_point[1], rgl[1].end_point[1],])
            ymin = min( rgl[0].start_point[0], rgl[0].end_point[0] )
            ymax = max( rgl[0].start_point[0], rgl[0].end_point[0] )
            xmin = min( rgl[1].start_point[0], rgl[1].end_point[0] )
            xmax = max( rgl[1].start_point[0], rgl[1].end_point[0] )
            vmask_0 = np.logical_and.reduce((
                    Xb > xmin, Xb < xmax,
                    Yb > ymin, Yb < ymax,
                    Zb > zmin, Zb < zmax,
            ))

            happy = 'n'
            while happy != 'y':
                print('\tMasking empty voxels. Choose lower threshold in figure.')
                tomo_flat = self.tomogram.flatten()
                # # draw all data in a sausage and choose a threshold directly
                # self.cutoff_low = msk.select_threshold( tomo_flat[vmask_0] )
                # draw a horizontal cutoff in a histogram
                self.cutoff_low = msk.select_threshold_hist( tomo_flat[vmask_0] )

                # apply the cutoff and region exclusion to the mask
                vmask = np.logical_and.reduce((
                    tomo_flat > self.cutoff_low,
                    vmask_0))

                # erosion dilation of noise
                # structure_size = 2
                # structuring_element = ndimage.generate_binary_structure(3, 1)
                # structuring_element = ndimage.iterate_structure(
                #     structuring_element, structure_size)
                vmask = ndimage.binary_opening(vmask)#, structure=structuring_element)

                # print('\tMasking empty voxels. Choose regions to exclude in figure.')
                # sphere_mask = msk.sphere_exclusion(self.x_p[vmask])
                # vmask[vmask] = sphere_mask
                
                self.mask_voxels = np.where( vmask )[0]
                msk.check_tomogram(self.tomogram, self.mask_voxels)
                happy = input('\thappy? (y/n) ')
                
            # save voxel mask to file
            with open(os.path.join(self.path_analysis,'voxelmask.txt'), 'w') as fid:
                for iv in self.mask_voxels:
                    fid.write(f'{iv}\n')      
            print('\t\tSaved voxelmask to analysis/voxelmask.txt')  
        else:
            self.mask_voxels = np.genfromtxt(
                os.path.join(self.path_analysis,'voxelmask.txt'),
                np.int32 )

        print('\tCalculate beam intensities')
        t0 = time()
        # make sparse arrays for the beams
        beam_precision = 1e-2 # cut all values below this
        Dmax = np.ceil( np.sqrt(self.nVox[0]**2+self.nVox[1]**2+self.nVox[2]**2)/2 )*2 # diagonal of the voxel-cuboid
        lb_max_approx = int(Dmax*10) # this is an estimation for the max No of entries in the sparse direction
        lb_max = 0 # will be eventually stripped to this
        self.Beams  = np.zeros( (Nrot, ntrans, lb_max_approx), data_type)
        self.iBeams = np.full((Nrot, ntrans, lb_max_approx), 2**32-1, dtype=np.uint32)
        tau = np.linspace(-Dmax/2, Dmax/2, int(Dmax*2)) # parameter for the beam trajectory
        neighbors = np.transpose(np.indices((3,3,3)) - 1).reshape(-1, 3) # indices of a 3x3x3 cube
        pminmax = np.array([
            [np.min(self.x_p[:,0]), np.max(self.x_p[:,0])],
            [np.min(self.x_p[:,1]), np.max(self.x_p[:,1])],
            [np.min(self.x_p[:,2]), np.max(self.x_p[:,2])]
        ])
        points_filtered = self.x_p[self.mask_voxels]
        # print('')
        t0=time()
        for g in range(Nrot): # rotations
            # rotated beam direction vector B0 = R(omega,kappa)*(1,0,0)
            B0 = np.array([1,0,0]) @ rot.OTP_to_matrix(self.Gs[g,0],self.Gs[g,1],self.Gs[g,2])

            # make a vector of voxels that are actually touched by the beam
            BB0, TTau = meshgrid( B0, tau )
            Bpath0 = np.unique(np.round(BB0*TTau),axis=0) # the closest voxels touched by the untranslated beam

            Bpath0n = np.empty( (Bpath0.shape[0]*27,3), data_type ) # the voxels above plus their neighbors
            for k in range(Bpath0.shape[0]):
                Bpath0n[k*27:(k+1)*27,:] = neighbors + Bpath0[k]
            Bpath0n = np.unique(Bpath0n, axis=0) # drop duplicates
            
            # Calculate beam intensities for every voxel and translation
            Beams, iBeams = _beamtranslations(
                    lb_max_approx, geo.Dbeam/geo.Dstep,
                    self.x_p, pminmax, self.mask_voxels,
                    B0, Bpath0n,
                    self.Gs[g],
                    self.Ty+self.shifty[g], self.Tz+self.shiftz[g], 
                    beam_precision
                )
            # Beams, iBeams = beamtranslations_full(
            #         lb_max_approx, geo.Dbeam/geo.Dstep,
            #         points_filtered,
            #         B0,
            #         self.Gs[g],
            #         self.Ty+self.shifty[g], self.Tz+self.shiftz[g]
            #     )
            self.Beams[g,:,:] = Beams
            self.iBeams[g,:,:] = iBeams

            lb = max([np.searchsorted(ib,2**32-1) for ib in self.iBeams[g]])
            lb_max = max(lb,lb_max)
            
            t_it = (time()-t0)/(g+1)
            sys.stdout.write(f'\r\t\tProjection {(g+1):d} / {Nrot:d}, t/it: {t_it:.2f}, t left: {((Nrot-g-1)*t_it/60):.1f} min' )
            sys.stdout.flush()
        
        # strip away voxels without intensity
        self.Beams = self.Beams[:,:,:lb_max+1]
        self.iBeams = self.iBeams[:,:,:lb_max+1]

        print(f', finished ({(time()-t0)/60:.1f} min)' )

    def _init_single(self):
        """ Defines experiment-related parameters for simulating only single image """
        self.fov = np.array([1,1])
        self.nVox = np.array([1,1,1])
        self.Omega = np.array([0])
        self.Kappa = np.array([0])
        self.Gs = np.array([[0,0,0]])
        self.x_p = np.array([[0,0,0]])
        self.p0 = 0
        self.Ty = np.array([0])
        self.Tz = np.array([0])
        self.Beams = np.array([[[1,0]]])
        self.iBeams = np.array([[[0,2**32-1]]])
        self.mask_voxels = np.array([True])

    def _symmetrize( self ):
        """Calculates sHSHs from HSHs

        Attributes created
        ------------
        NsHSH : 1D ndarray, int
            Number of sHSHs per order
            dim 0: order index
        Sn : 1D ndarray, in
            'Slices' for selecting the sHSHs of each order in an array
            dim: 0: order index, dim 1: [start, end]
        sHSHs : 2D ndarray, float
            all used sHSHs
            dim: 0: rotation index, dim 1: sHSH index
        Xsn : dict containing 2D ndarrays, float
            HSH -> sHSH transformation matrix, access orders with Xsn['n']
        """
        # number of crystal rotations
        Nrot = self.Gc.shape[0] 
        # Number sHSHs for each n
        self.NsHSH  =  np.array( [sym.get_NsHSH(self.symmetry,n) for n in self.ns] ) 
        # make array with sHSH coefficients per voxel
        self.Sn = np.array(
            [ [ self.NsHSH[:k].sum(), self.NsHSH[:k+1].sum() ] 
             for k in range(self.NsHSH.shape[0]) ]) # 'slices' of coefficients as numbers for each n
        
        ## calculate all necessary HSHs: for each used n: l = {0,..,n}, m = {-l,..,l}
        allHSH = {}
        for n in self.ns:
            allHSH[str(n)] = np.empty([(n+1)**2,Nrot], np.complex128)
            k=0
            for l in range(n+1):
                for m in range(-l,l+1):
                    allHSH[str(n)][k,:] = hsh.Z(self.Gc[:,0],self.Gc[:,1],self.Gc[:,2],n,l,m)
                    k+=1

        # calculate symmetrized HSHs from linear combinations of HSHs
        self.sHSHs = np.empty( ( self.NsHSH.sum()-1, Nrot ), data_type )
        self.Xsn = {'0': np.array([[1.]], np.complex128)}
        l = 0
        for k, n in enumerate(self.ns[1:]):
            _, csym = sym.cSymmHSH(self.symmetry, n) # get sSHSs and orders
            self.Xsn[str(n)] = csym # HSH to sHSH coefficient rotation matrix
            for m in range(self.NsHSH[k+1]):
                self.sHSHs[ l ] = np.real(csym[m,:] @ allHSH[str(n)]).astype(data_type)
                l += 1              

    def _init_odf(self):
        """Calculates sHSHs from HSHs

        Attributes created
        ------------
        difflets : 2D ndarray, float
            diffractlets for null rotation
            dim: 0: sHSH index, 1: detector point index
        Rs : 3D ndarray, float
            sHSH rotation matrices for all sample rotations
            dim: 0: sample rotation index, dim 1,2: sHSH indices
        difflets_rot : 3D ndarray, float
            diffractlets for all sample rotations
            dim: 0: sample rotation, 1: sHSH indices, 2: detector points
        """
        t0=time()
        # calculate symmetrized hyperspherical harmonics
        self._symmetrize()

        d_len = self.sHSHs.shape[0] - self.difflets.shape[0] + 1
        if d_len > 0:
            # Calculate image resulting from each used sHSH
            dlets = np.empty( 
                ( d_len, self.detShape[0]*self.detShape[1] ), data_type )
            for l in range(d_len):
                dlets[ l, : ] = (self.sHSHs[l] * self.dV) @ self.Isc

            # ###### test for changing detector angle direction
            #     d_inter = dlets[ l, : ].reshape( self.detShape )
            #     d_inter = np.flip( d_inter, axis=1 )
            #     dlets[ l, : ] = d_inter.flatten()
            # ######

            self.difflets = np.concatenate((self.difflets,dlets), axis = 0)

            # calculate the rotation matrices
            # # map sample rotations to fundamental zone
            # q_gen = rot.QfromOTP(sym.generators(self.symmetry))
            # Q_group = rot.generate_group(q_gen)
            # Qs = rot.QfromOTP(self.Gs)
            # for sHSHs for each used n and all sample rotation angles
            self.Rs = self.get_Rs_stack(np.column_stack(
                (-self.Gs[:,0], self.Gs[:,1], self.Gs[:,2])))
            
            # # calculate rotated diffractlets
            # self.difflets_rot = _rotate_difflets_stack( self.Rs, self.difflets)
            print(f"\tCalculated diffractlets, {(time()-t0):.2f} s)" )

        elif d_len < 0: # if order is reduced
            self.difflets = self.difflets[:d_len]
            self.Rs = self.Rs[:,:d_len,:d_len]
            # self.difflets_rot = self.difflets_rot[:,:d_len]

        elif self.sHSHs.shape[0]==0:
            nrot = self.Beams.shape[0]
            self.Rs = np.ones((nrot,1,1), data_type)
            # self.difflets_rot = np.tile(self.difflets, (nrot,1,1))#.reshape()

    def _init_misc(self):
        """ Other initialisations 

        images: 3D ndarray, float
            modelled diffraction patterns
            dim 0: rotation, 1: translation, 2: detector points
        """
        self.ns = [0]
        # prelocate stuff
        self.images = np.empty(
            (self.Gs.shape[0],self.Ty.shape[0],self.Chi_det.shape[0]), 
            data_type) # detector images self.images[gl,t]

    """
    Methods
    """
    def get_orders(self, n_max = 20, info=True, exclude_ghosts=True ):
        ''' Gives the allowed orders up to n_max
        
        Parameters
        ----------
        n_max : int
            maximum HSH order used
        info : bool
            if True, the list of how many sHSHs exist at each order is printed
        
        Return values
        ------------
        n_allowed : ndarray, int
            orders where sHSHs exist for this point group
        '''
        if info:
            print(f'\tBuilt model for symmetry {self.symmetry}')
            print('\t\tn\tNo of symmetrized HSHs for order n')
        n_allowed = [0]
        for n in range(1,n_max+1):
            Nn = sym.get_NsHSH(self.symmetry,n)
            if exclude_ghosts and (not n%2) and (n%4): # condition for ghosts
                ghost = f' ({Nn} ghosts)'
                Nn = 0
            else:
                ghost = ''
            if info:
                print('\t\t%u\t %u%s' % (n, Nn, ghost) )
            if Nn > 0:
                n_allowed.append(n)
        return np.array(n_allowed)
            
    def set_orders( self, n_max, info=True, exclude_ghosts=True ):
        ''' Calculates a single sHSH rotation matrix
        
        Parameters
        ----------
        n_max : int
            maximum HSH order used
            
        Attributes created
        ------------
        ns : 1D ndarray, int
            list of used HSH orders
        '''
        # get allowed orders up to n_max
        self.ns = np.array(self.get_orders( n_max, info=False, exclude_ghosts=exclude_ghosts)) 
        if info:
            print('\tSet HSH orders to [%s]' % ', '.join(self.ns.astype(str)) )

        if self.classic:
            # calculate HSH and diffractlets
            self._init_odf()

    def get_Rs( self, g ):
        ''' Calculates a single sHSH rotation matrix
        
        Parameters
        ----------
        g : 1D ndarray
            desired rotation [ome, tta, phi]
        
        Return values
        ------------
        Rs: 2D ndarray, float
            sHSH rotation matrix for all orders
        '''
        Rs = np.zeros( (self.difflets.shape[0], self.difflets.shape[0]), data_type )
        for kn, n in enumerate(self.ns):
            Rs[ self.Sn[kn,0]:self.Sn[kn,1], self.Sn[kn,0]:self.Sn[kn,1] ] = Rs_n(
                g, n, self.Xsn[str(n)] )        
        return Rs
    
    def get_Rs_stack( self, G ):
        ''' Calculates sHSH rotation matrices for a list of rotations G
        
        Parameters
        ----------
        G : 2D ndarray, float
            dim 0: rotation index, 1: [ome, tta, phi]
        
        Return values
        ------------
        Rs: 2D ndarray, float
            list of sHSH rotation matrix for all orders
            dim 0: rotation index, 1,2: rotation matrix
        '''
        Rs_stack = np.zeros( 
            ( G.shape[0], self.difflets.shape[0], self.difflets.shape[0] ), data_type )
        Rs_stack[:,0,0] = 1
        for k, n in enumerate(self.ns[1:]):
            kn = k+1
            Rs_stack[ :, self.Sn[kn,0]:self.Sn[kn,1], self.Sn[kn,0]:self.Sn[kn,1] ] = Rs_n_stack(
                G, n, self.Xsn[str(n)] )
        return Rs_stack

    def odfFromC( self, c, K = None, clip = False, info = False ):
        """Computes an ODF from sHSHs

        Sums over pre-calculated symmetrized spherical harmonic functions
        and weights by the given coefficients. Also adds a isotropic part
        weighted by another input parameter

        Parameters
        ----------
        c : 1D ndarray, float
            set of sHSH coefficients
        K : float or None for not applying
            HSH damping factor to ensure positivity, usually between 1 and 2
        clip: bool
            if True, negative values get clipped and ODF renormalized
        info: bool
            if True prints information about the ODF
            
        Return values
        ------------
        odf : 1D ndarray, float
            array of probabilities for each orientation self.Gc
        """
        if K == 'auto':
            K, neg = 1., 1.
            c_in=c.copy()
            while neg>0.01:
                c_in = self.apply_kernel( c, K, info=False )
                odf = _odfFromC( self.sHSHs, c )
                neg = ( odf[odf<0] @ self.dV[odf<0] ) 
                K += 0.1
        elif isinstance(K,(int, float)): # apply the Mason kernel on coefficients
            c_in = self.apply_kernel( c, K )
        else:
            c_in = c.copy()
        
        # calculate ODF
        odf = _odfFromC( self.sHSHs, c_in )

        if clip:
            neg_percent = - odf[odf<0].sum() / np.abs(odf).sum()
            odf[odf<0] = 0 # clip negative values
            odf = odf / ( odf @ self.dV ) # renormalize

        if info:
            self.get_c_weights(c_in)
            print('Made ODF')
            print('\tMaximum: %.3e' % odf.max() )
            print('\tMinimum: %.3e' % odf.min() )


            # estimate mean value from distribution truncated at lowest order
            if c.size > 1:
                ic_max = self.Sn[1,1]
                i_mu = np.argmax(
                    _odfFromC( self.sHSHs[:ic_max-1], c[:ic_max]))
                mu = self.Gc[i_mu]
                std = self.std_sample(
                    np.array([c_in]), np.array([mu])
                )[0]
            print('\tMean orientation: ome %.2f, tta %.2f, phi %.2f' % (
                mu[0],mu[1],mu[2]))
            print('\tStandard deviation [%s]: %.2f' % (chr(176), std*180/np.pi))
            
            if np.any(odf<0):
                odf_pos = odf.copy()
                odf_pos[odf_pos<0]=0
                tmp = odf_pos @ self.dV - 1
                rel_neg = tmp / (1 + 2*tmp)
                print('\t%.2f percent of the distribution is negative' % (rel_neg*100) )

        return odf

    def apply_kernel( self, c, K, info=True ):
        """Applies the Mason kernel on the HSH coefficients

        J. K. Mason and O. K. Johnson, ?Convergence of the hyperspherical 
        harmonic expansion for crystallographic texture,? J Appl Crystallogr, 
        vol. 46, no. 6, pp. 1722?1728, Dec. 2013, doi: 10.1107/S0021889813022814.

        Parameters
        ----------
        c : 1D ndarray, float
            set of sHSH coefficients
        K : float
            HSH damping factor to ensure positivity, usually 1 to 2
            
        Return values
        ------------
        c : 1D ndarray, float
            set of modified sHSH coefficients
        """
        for k, Sn in enumerate(self.Sn):
            c[Sn[0]:Sn[1]] = ( 1- self.ns[k]/(self.ns[-1]+1) )**K * c[Sn[0]:Sn[1]]
        if info:
            print('\tApplied Kernel, K = %.2f' % K)
        return c
    
    def get_c_weights(self, c):
        """ Evaluate the contributions from each order to the ODF """
        print('Coefficient weights sum(c^2):')
        weights = []
        for k, Sn in enumerate(self.Sn):
            weights.append( (c[Sn[0]:Sn[1]]**2).sum() )
            print( '\tOrder %d: %.4f' % (self.ns[k], weights[k]))
        return np.array(weights)
    
    def g_ML_sample( self, C, truncate = False ):
        """ Calculates ODFs from a stack of sets of sHSH coefficients
        by choice truncated at the lowest expansion order
        and returns the orientation corresponding to the peak of the
        distribution
        
        Parameters
        ----------
        C : 2D ndarray, float
            set of sHSH coefficients for each voxel
            dim 0: voxel index, 1: sHSH index

        Return values
        ------------
        g_ML :  2D ndarray, float
            register of axis-angle rotations
            dim: 0: voxel index, 1: [omega, theta, phi]
        """
        # ic_max = self.Sn[1,1]
        # g_mean = _odf_max_stack(
        #     C[:,:ic_max], self.sHSHs[:ic_max], self.Gc, self.V_fz )
        if truncate:
            ic_max = self.Sn[1,1]
            C[:,ic_max:] = 0
        g_ML = _odf_max_stack(
            C, self.sHSHs, self.Gc, self.V_fz )
        return g_ML

    def std_sample( self, C, Mu ):
        """ Calculates the standard deviation of a ODFs given by their
        sets of coefficients C around their mean orientations Mu
        
        Parameters
        ----------
        C : 2D ndarray, float
            set of sHSH coefficients for each voxel
            dim 0: voxel index, 1: sHSH index
        Mu : 2D ndarray, float
            mean orientations of each unmasked voxel
            dim 0: voxel index, 1: [omega, theta, phi]

        Return values
        ------------
        Std : 1D ndarray, float
            angular standard deviation for each voxel
        """
        Mu[Mu==0] += 1e-6 # this is to avoid NaNs if zero (why?)
        Rs = self.get_Rs_stack( np.column_stack( 
            (-Mu[:,0], Mu[:,1], Mu[:,2]) ) )
        Std = _odf_std_fromZero_stack(
            C, Rs, self.V_fz, self.sHSHs, self.dV, self.Gc[:,0] )

        return Std

    def abc_pref_sample( self, g_pref ):
        """ Calculates the crystal axis orientations from OTP orientations

        Should be generalized to all crystal systems using the actual axes

        Parameters
        ----------
        g_pref : 2D ndarray, float
            dim: 0: voxel index, 1: [ome,tta,phi]

        returns: 
        ------------
        a_pref, b_pref, c_pref : 2D ndarray, float
            crystal axis unit vectors
            dim: 0: voxel index, 1: [x,y,z]
        """
        lattice_vectors_norm = self.lattice_vectors/np.linalg.norm(self.lattice_vectors,axis=1)
        a_pref, b_pref, c_pref = _abc_pref_sample( g_pref, lattice_vectors_norm.astype(data_type) )
        return a_pref, b_pref, c_pref

    def directions_from_orientations( self, Orientations, direction_0=(0,0,1) ):

        return _directions_from_orientations(Orientations, np.array(direction_0,data_type))

    def imageFromC(self, c):
        """ Computes a diffraction image from a set of sHSH coefficients

        Parameters
        ----------
        c : 1D ndarray, float
            set of sHSH coefficients
        
        Return values
        ------------
        image : ndarray, float
            array of scattering intensity for each point on the detector
        """
        image = _imageFromC( c, self.difflets )
        return image

    def imageFromOdf(self, odf):
        """Computes a diffraction image from an ODF

        Integrates pre-calculated single crystal diffraction patterns
        over an orientation distribution function. 

        Parameters
        ----------
        odf : ndarray, float
            array of probabilities for each orientation defined in self.crystalrotations
        
        Return values
        ------------
        image : ndarray, float
            array of scattering intensity for each point on the detector
            defined in self.crystalrotations
        """
        image = _imageFromOdf(self.dV,self.Isc,odf)
        return image
    
    def projection( self, g, C ):
        """Simulates diffraction images from a 2D scan over the sample

        For a certain sample rotation calculates sHSH coefficients in 
        each voxel, then integrates over the beam intensity for each
        translation, calculates the diffraction patterns and saves them
        into the model object.

        Parameters
        ----------
        g : int
            index of the sample rotation, defined in self.samplerotations
        C : 2D ndarray, float
            set of sHSH coefficients for each voxel
            dim: 0: voxel index, 1: sHSH index

        Attributes modified
        ------------
        images : 3D ndarray, float
            array of resulting scattering intensity for each point on the 
            detector, for each rotation and translation
            dim: 0: rotation, 1: translation, 2: detector points
        """
        print('\tcalculating images for projection %d' % g )
        t0 = time()
        images = _projection(
            g, C, 
            self.Beams, self.iBeams, self.difflets_rot,
            )
        print("\t\tfinished in %.3f s" % (time()-t0))
        return images
    
    def projection_old( self, g, C ):
        """Simulates diffraction images from a 2D scan over the sample

        For a certain sample rotation calculates sHSH coefficients in 
        each voxel, then integrates over the beam intensity for each
        translation, calculates the diffraction patterns and saves them
        into the model object.

        Parameters
        ----------
        g : int
            index of the sample rotation, defined in self.samplerotations
        C : 2D ndarray, float
            set of sHSH coefficients for each voxel
            dim: 0: voxel index, 1: sHSH index

        Attributes modified
        ------------
        images : 3D ndarray, float
            array of resulting scattering intensity for each point on the 
            detector, for each rotation and translation
            dim: 0: rotation, 1: translation, 2: detector points
        """
        print('\tcalculating images for projection %d' % g )
        t0 = time()
        difflets_rot = rotate_difflets_stack( [self.Rs[g]], self.difflets)
        # ^ can i not skip this like and just put self.Rs[g] below?? (only hsh..)
        images = _projection(
            g, C, 
            self.Beams, self.iBeams, difflets_rot,
            )
        print("\t\tfinished in %.3f s" % (time()-t0))
        return images

    def insert_sparse_tomogram( self, values ):
        """ Makes a 3D tomogram out of sparse data
        """
        try:
            tomogram = np.empty( (self.nVox.prod(),values.shape[1]), data_type )
            tomogram[:] = np.nan
            tomogram[self.mask_voxels] = values
            tomogram = tomogram.reshape((*self.nVox, values.shape[1]))
        except:
            tomogram = np.empty( self.nVox.prod(), data_type )
            tomogram[:] = np.nan
            tomogram[self.mask_voxels] = values
            tomogram = tomogram.reshape(self.nVox)
        return tomogram

    def get_reciprocal_space_coordinates(self):
        """Calculates the coordinates of the detector points based on
        polar coordinates q_det, chi_det and X-ray energy E_kev

        Returns
        -------
        ndarray
            3D reciprocal space coordinates and number of detector points
        """

        h = 4.135667696e-18 # keV*s
        c = 299792458 # m/s
        wavelength = h*c*1e9 / self.E_keV # nm

        Two_theta = 2 * np.arcsin(self.Qq_det * wavelength / (4*np.pi))
        QX,QY,QZ = np.empty_like(Two_theta), np.empty_like(Two_theta), np.empty_like(Two_theta)
        for k in range(QY.shape[0]):
            QX[k], QY[k], QZ[k] = reciprocal_lattice_point(Two_theta[k], self.Chi_det[k], wavelength,
                u_beam=self.geo.beam_direction,
                u0=self.geo.detector_direction_origin,
                u90=self.geo.detector_direction_positive_90,
            )

        # import matplotlib.pyplot as plt
        # fig = plt.figure(figsize=(8, 6))
        # ax = fig.add_subplot(121, projection='3d')
        # ax.scatter(QX, QY, QZ)
        # ax.set_xlabel('x')
        # ax.set_ylabel('y')
        # ax.set_zlabel('z')
        return QX, QY, QZ

@njit
def reciprocal_lattice_point(two_theta_rad, chi_rad, wavelength_nm, 
                             u_beam=(1,0,0), u0=(0,0,1), u90=(0,1,0)):
    """
    Calculate (qx, qy, qz) from angles and wavelength, defining the geometry by vectors.

    Parameters:
    - two_theta_rad: scattering angle (2?) in rad
    - chi_rad: azimuthal angle in rad
    - wavelength_nm: wavelength of incident beam in nm
    Optional:
    - u_beam: beam direction vector
    - u0: direction vector pointing towards the origin of chi
    - u90: direction vector pointing towards chi of +90 degree

    Returns:
    - (qx, qy, qz): reciprocal space coordinates (nm^-1)
    """
    # axes
    u_beam = np.array(u_beam, data_type)
    u0 = np.array(u0, data_type)
    u90 = np.array(u90, data_type)

    # Magnitude of wavevector
    k = 2 * np.pi / wavelength_nm

    # Incoming wavevector:
    k_in = k * u_beam

    # Outgoing wavevector (direction from spherical coordinates)
    k_out = k * (
        np.cos(two_theta_rad) * u_beam + 
        np.sin(two_theta_rad) * ( np.cos(chi_rad) * u0 + np.sin(chi_rad) * u90 )
        )

    q = k_out - k_in
    return q

"""
Class-external functions compiled in numba and called from wrappers inside the class
"""

#### Functions for Initialisation ####

@njit(parallel=True)
def _beamtranslations(
            beam_maxlength, dBeam,
            points, pminmax, mask_voxels,
            B0, Bpath0n,
            gs,
            Ty, Tz,
            beam_precision
        ):
    """ Calculation of beam intensities for one sample orientation

    Parameters
    ----------
    beam_maxlength : int
        approximate maximum number of voxels involved in a calculation
    dBeam : float
        beam FWHM relative to the voxel size
    p : 2D ndarray, float
        dim 0: voxel index, 1: [x,y,z]
    pminmax : 2D ndarray, float
        minimum and maximum voxel position for each dimension
    mask_voxels : 1D ndarray, bool
        dim 0: voxel index
    B0 : 1D ndarray, float
        beam direction vector at translation 0
    Bpath0n : 1D ndarray, int
        beam trajectory at translation 0 in voxel indices
    omega, kappa : float
        rotation angles for this projection
    Ty, Tz : 1D ndarray, float
        beam translations with a common index
    beam_precition : float
        relative treshold for beam intensity below which values will be cut
    
    Return values
    ------------    
    values, indices
        2 arrays, together forming a sparse array

    """
    ntrans = Ty.shape[0]
    Beams  = np.zeros( ( ntrans, beam_maxlength), data_type)
    iBeams = (2**32-1) * np.ones( ( ntrans, beam_maxlength), np.uint32)

    for t in prange(ntrans): # translations
        ty,tz = Ty[t], Tz[t]
        # rotated translation vector
        T = np.array([0,ty,tz],data_type) @ rot.OTP_to_matrix(gs[0],gs[1],gs[2])

        # translated beam direction vector (actually just a point on the beam)
        B = B0 + T

        # translated voxel indices supposedly touched by the beam
        Bpath = Bpath0n + T   
        # filter out voxels outside the sample
        insample = (
            (Bpath[:,0] >= pminmax[0,0] )&
            (Bpath[:,1] >= pminmax[1,0] )&
            (Bpath[:,2] >= pminmax[2,0] )&
            (Bpath[:,0] <= pminmax[0,1] )&
            (Bpath[:,1] <= pminmax[1,1] )&
            (Bpath[:,2] <= pminmax[2,1] )
        )
        Bpath = Bpath[insample]

        # voxel indices of the path points
        ib0 = (
            np.floor(Bpath[:,0]-pminmax[0,0])*(pminmax[1,1]-pminmax[1,0]+1)*(pminmax[2,1]-pminmax[2,0]+1) + \
            np.floor(Bpath[:,1]-pminmax[1,0])  *(pminmax[2,1]-pminmax[2,0]+1) + \
                np.ceil(Bpath[:,2]-pminmax[2,0]) 
            ).astype(np.uint32)                                                                        

        # filter out filled voxels by mask
        ib_msk = np.intersect1d(ib0,mask_voxels)

        # coordinates of voxels on the path
        p_path = points[ib_msk]

        # distance to beam normal to beam direction (https://mathworld.wolfram.com/Point-LineDistance3-Dimensional.html)
        w = np.empty( p_path.shape[0], data_type )
        for k in range(p_path.shape[0]):
            w[k] = np.linalg.norm(np.cross((p_path[k]-T),(p_path[k]-B)))/np.linalg.norm(B-T)

        # cumulative gaussian distribution in function of the distance from the beam
        sigma = dBeam/(2*np.sqrt(2*np.log(2))) # if dBeam is the FWHM
        beam = 1/2 * ( erf( (1/2+w)/(np.sqrt(2)*sigma) ) + erf( (1/2-w)/(np.sqrt(2)*sigma) ) )

        # cut away small values
        ib2 = (beam>=beam_precision)
        ib = ib_msk[ib2]
        nb = ib.shape[0] # effective number of touched voxels
        Beams[t,:nb] = beam[ib2]
        iBeams[t,:nb] = ib
    return Beams, iBeams

@njit(parallel=True)
def beamtranslations_full(
        beam_maxlength, dBeam,
        points,
        beam_direction,
        gs,
        Ty, Tz
    ):
    """ Calculation of beam intensities for one sample orientation
    -- inactive -- maybe this approach could speed up the calculation

    Parameters
    ----------
    beam_maxlength : int
        approximate maximum number of voxels involved in a calculation
    dBeam : float
        beam FWHM relative to the voxel size
    p : 2D ndarray, float
        dim 0: voxel index, 1: [x,y,z]
    mask_voxels : 1D ndarray, bool
        dim 0: voxel index
    B0 : 1D ndarray, float
        beam direction vector at translation 0
    gs : 1D ndarray
        sample orientation (ome,tta,phi)
    Ty, Tz : 1D ndarray, float
        beam translations with a common index
    beam_precition : float
        relative treshold for beam intensity below which values will be cut
    
    Return values
    ------------    
    values, indices
        2 arrays, together forming a sparse array

    """
    # get Gaussian standard deviation from the FWHM
    sigma = dBeam/(2*np.sqrt(2*np.log(2))) 

    # set up sparse arrays
    ntrans = Ty.shape[0]
    Beams  = np.zeros( ( ntrans, beam_maxlength), data_type)
    iBeams = (2**32-1) * np.ones( ( ntrans, beam_maxlength), np.uint32)

    for t in prange(ntrans): # translations
        # rotated translation vector (some point on the beam)
        T = np.array([0,Ty[t], Tz[t]],data_type) @ rot.OTP_to_matrix(gs[0],gs[1],gs[2])
        # get beam intensities for this configuration
        values, idcs = beamintensity(points, T, beam_direction, sigma )
        # save to sparse array
        nb = idcs.size
        Beams[t,:nb] = values
        iBeams[t,:nb] = idcs
    return Beams, iBeams

@njit
def beamintensity( points, beam_center, beam_direction, sigma, threshold=0.01 ):
    """Calculates a gaussian beam intensity for a given rotation and translation
    defined by the vectors beam_center (arbitrary point on the beam path) and 
    beam_direction. Values are unnormalized and cut at the value treshold.
    They are returned as sparse array, the second returned array are the indices
    which link the values to the points.

    Parameters
    ----------
    points : ndarray
        dim 0: voxel index, 1: [x,y,z]    beam_center : ndarray
    beam_direction : ndarray
        point in 3D
    sigma : float
        beam width (gaussian standard deviation)
    threshold : float, optional
        lowest value entering in the sparse array, by default 0.01

    Returns
    -------
    values, indices
        2 arrays, together forming a sparse array
    """
    beam_direction = beam_direction / np.linalg.norm(beam_direction)

    # Project each point onto the plane using the normal
    # Compute the vector from center to each point
    r = points - beam_center
    # Distance from each point to the plane
    dist_to_plane = np.dot(r, beam_direction)
    # Project onto the plane
    proj = points - np.outer(dist_to_plane, beam_direction)

    # Now compute local coordinates (u,v) in the plane to define the 2D Gaussian
    # We need two orthonormal vectors in the plane
    def orthonormal_basis(n):
        # Choose a vector not parallel to n
        if abs(n[0]) < 0.9:
            other = np.array([1, 0, 0])
        else:
            other = np.array([0, 1, 0])
        u = np.cross(n, other)
        u /= np.linalg.norm(u)
        v = np.cross(n, u)
        return u, v

    u_vec, v_vec = orthonormal_basis(beam_direction)
    # Compute coordinates in plane
    u_coords = np.dot(proj - beam_center, u_vec)
    v_coords = np.dot(proj - beam_center, v_vec)

    # Evaluate 2D Gaussian on the plane
    # gaussian = (1 / (2 * np.pi * sigma**2)) * np.exp(-(u_coords**2 + v_coords**2) / (2 * sigma**2))
    gaussian = np.exp(-(u_coords**2 + v_coords**2) / (2 * sigma**2))

    # cut away small values
    indices = np.where(gaussian > threshold)[0]
    # nb = ib.shape[0] # effective number of touched voxels
    # Beams[t,:nb] = beam[ib2]
    # iBeams[t,:nb] = ib
    return gaussian[indices], indices

@njit(parallel=True)
def single_crystal_images( Q, uc_pos_rot, bool_pos_element, F_el, crystalsize, lattice_vectors_rot):
    """ 
    Calculation of the scattering intensities of a single crystal

    parameters
    ----------
    Q: 2D ndarray, float
        momentum exchange vector
        dim0: reciprocal lattice points, 1: [qx,qy,qz]
    uc_pos_rot: 3D ndarray, float
        atom position in the unit cell for all crystal rotations
        dim0: rotation, 1: real space positions, 2: [x,y,z]
    bool_pos_el : 2D ndarray, string
        mask for uc_pos to find elements
        dim0: element dim1: mask for positions in uc
    F_el : 2D ndarray, float
        atomic form factor
        dim 0: elements, 1: reciprocal lattice points
    crystalsize: 1D ndarray len=3
        dim: size along the three crystal axes
    lattice_vectors_rot: 3D ndarray, float
        dim0: rotations, 1:three lattice directions, 2: lattice vector in current orientation
    Return values
    ------------
    Isc : 2D ndarray, float
        refraction intensities in Q-spaces for all orientations
        dim 0: orientations, 1: for wave vector
    """
    Ndet = Q.shape[0] # number of detector bins
    Nrot = uc_pos_rot.shape[0] # number of rotations 
    Isc = np.empty((Nrot,  Ndet), np.float64) # single crystal diffraction patterns
    for g in prange(Nrot): #for each orientation
        uc_pos = uc_pos_rot[g] # get the positions of the atoms in the unit cell
        #calculate structure factors of lattice and the unit cell
        SF_lat_complex = strufact_lattice(Q, lattice_vectors=lattice_vectors_rot[g], crystal_size=crystalsize.copy())
        SF_uc_complex = strufact_unit_cell(Q, F_el, uc_pos, bool_pos_element)
        
        S_complex=SF_uc_complex*SF_lat_complex #Multiply SF of lattice with SF of the unit cell
        #S_complex=SF_uc_complex #Multiply SF of lattice with SF of the unit cell
        #print(np.max(np.imag(SF_lat_complex)), "should be near 0")
        Isc[g,:] = np.real(S_complex*S_complex.conjugate()) # put together for the respective orientation
        #in theory   complex part should be 0 here (z*z.conjugate=|z|^2), so ignore warning

    return Isc

@njit
def strufact_lattice(Q, lattice_vectors, crystal_size):
    '''
    Q: 2D ndarray, float
        sampling points in reciprocal space
        dim 0: reciprocal lattice points, 1: [qx,qy,qz]
    lattice_vectors: 2D ndarray
        dim0: three lattice directions, 1: lattice vector in current orientation
        a:[x, y, z]
        b:[x, y, z]
        c:[x, y, z]
    crystal_size: 1D ndarray len=3
        dim: size along the three crystal axes
    
    Return value:
    --------------
    sf_complex: 1D ndarray, complex128
        structure factor of the lattice, function of Q
        dim0: complex structure factor
    '''
    #algorithm does the following:
    #1: find largest dimension of the crystal (equality->lowest dim)
    #2: store 1 lattice point p which is the n/2th one along this axis, which is the n/2th along the acquired dimension
    #3: calculate the structure factor of this "lattice": 1+exp(i*p*Q)
    #4: multiply this sf with the one of its "sublattice", which will be recursively called using this function
    #5: break the recursion when the shape of the crystal is 1,1,1 and calculate the sf of that last "cell" by hand - it's just e^0
    longest_axis_value=np.max(crystal_size) #the length of the longest axis
    longest_axis_number=np.where(crystal_size==longest_axis_value)[-1][0] #the axis in question (in the lowest dim)
    #We could try to save time by not picking out the longest axis but rather go from 0-2 and just keep dividing until the length=2
    ###It should be alright to leave it like this. If large errors occur, it may come from numerical issues that
    ##may arise with the deeper recursion.
    ##Change commented code with first part of if statement
    '''
        if np.all(crystal_size == 2):
        #calculate the remaining 8 (7) lattice positions: a, b,c a+b, a+c, b+c, a+b+c
        positions=np.zeros((7, 3), data_type)
        positions[:3]=lattice_vectors       
        positions[3]=lattice_vectors[0]+lattice_vectors[1]
        positions[4]=lattice_vectors[0]+lattice_vectors[2]
        positions[5]=lattice_vectors[1]+lattice_vectors[2]
        positions[6]=positions[3]+lattice_vectors[2] #a+b+c      

        SFL_complex=np.ones(Q.shape[0],np.complex128) #accounting for the lattice point at 0
        for r in positions:
            #qr = r[0]*Q[:,0] + r[1]*Q[:,1] + r[2]*Q[:,2] #calculate scalar product
            qr = np.dot(Q, r)
            SFL_complex += np.exp(qr*1j) 
        return SFL_complex
    '''
    if np.all(crystal_size == 1):
        SFL_complex=np.ones(Q.shape[0],np.complex128) #the remaining lattice point at 0,0,0
        return SFL_complex
    else:
        #determine second lattice point (first one being [0,0,0])
        p = ((longest_axis_value//2)*lattice_vectors[longest_axis_number]).astype(np.float64)
        #evaluate 1+exp(ipq)
        #qp=p[0]*Q[:,0] + p[1]*Q[:,1] + p[2]*Q[:,2] #scalar product
        qp=np.dot(Q,p)
        #dot product will only run parallely with both as same datatype 

        sf_complex=1+np.exp(qp*1j) 
        #multiply by SF of sublattice, that is repeated at 0 and p
        crystal_size[longest_axis_number] = longest_axis_value//2
        sf_complex=sf_complex*strufact_lattice(Q, lattice_vectors, crystal_size)
        return sf_complex 
    ##possibly add cases for one dimension being 1 or odd

@njit       
def strufact_unit_cell( Q, FF, unit_cell_pos, bool_pos_element):
    '''
    Q: 2D ndarray, float
        momentum exchange vectors
        dim 0: reciprocal lattice points, 1: [qx,qy,qz]
    FF : 2D ndarray, float
        atomic form factors for different elements
        dim0: different elements
        dim1: different Qs
    unit_cell_pos: 2D ndarray, float
        real space atomic positions
    bool_pos_el : 2D ndarray, string
        mask for uc_pos to find elements
        dim0: element dim1: mask for positions in uc

    Return values
    -------------
    SU_complex: 1D ndarray, complex128
        structure factor of the unit cell, function of Q
        dim0: complex structure factor
    '''
    SU_complex=np.zeros_like(Q[:,0], np.complex128)
    nEl=bool_pos_element.shape[0]
    
    for i in range(nEl): #for all elements 
        f=FF[i] #get atomic form factor (for all Qs)
        sComplex=np.zeros_like(SU_complex)
        for r in unit_cell_pos[bool_pos_element[i,:]]: #all atom positions of that element
            #qr = r[0]*Q[:,0] + r[1]*Q[:,1] + r[2]*Q[:,2] #calculate scalar product
            qr = np.dot(Q,r)
            sComplex += np.exp(qr*1j)
        SU_complex += f*sComplex
    return SU_complex

# @njit(parallel=True)
# def _single_crystal_images( Q, pos_rot, F_el, bool_pos_el ):
#     """ Calculation of the structure factor for one atom type

#     Parameters
#     ----------
#     Q: 2D ndarray, float
#         momentum exchange vector
#         dim 0: reciprocal lattice points, 1: [qx,qy,qz]
#     pos_rot : 3D ndarray, float
#         atom positions for all cyrstal rotations
#         dim: 0: rotation, 1: real space positions, 2: [x,y,z]
#     F_el : 2D ndarray, float
#         atomic form factor
#         dim 0: elements, 1: reciprocal lattice points
#     bool_pos_el : 2D ndarray, bool
#         mask for pos_rot for each element
#         dim 0: elements, 2: real space positions
    
#     Return values
#     ------------
#     image : 1D ndarray, float
#         simulated diffraction pattern
#     """
#     Ndet = Q.shape[0]
#     Nrot = pos_rot.shape[0]
#     Nel = F_el.shape[0]
#     Isc = np.empty((Nrot,  Ndet), data_type)

#     for g in prange(Nrot):
#         Sreal, Simag = np.zeros(Ndet, data_type), np.zeros(Ndet, data_type)
#         for k_el in range(Nel):
#             apos = pos_rot[ g, bool_pos_el[k_el] ]
#             sr, si = _strufact_singleEl( Q, apos, F_el[k_el] )
#             Sreal += sr
#             Simag += si
#         Isc[g,:] = ( Sreal**2 + Simag**2 )

#     return Isc
    
# @njit()
# def _strufact_singleEl( Q, atom_positions, F ):
#     """ Calculation of the structure factor for one atom type

#     Parameters
#     ----------
#     Q: 2D ndarray, float
#         momentum exchange vector
#         dim 0: reciprocal lattice points, 1: [qx,qy,qz]
#     atom_positions : 2D ndarray, float
#         dim: 0: real space positions, 1: [x,y,z]
#     F : 1D ndarray, float
#         atomic form factor, function of Q
    
#     Return values
#     ------------
#     image : 1D ndarray, float
#         simulated diffraction pattern
#     """
#     sreal, simag = np.zeros_like(Q[:,0]), np.zeros_like(Q[:,0])
#     for p in atom_positions:
#         qr = p[0]*Q[:,0] + p[1]*Q[:,1] + p[2]*Q[:,2]
#         sreal += np.cos(qr)
#         simag += np.sin(qr)

#     Sreal = F * sreal
#     Simag = F * simag
#     return Sreal, Simag
    
#### Functions for methods ####

@njit()
def _imageFromOdf( dV, Isc, odf ):
    """Computes a diffraction image from an ODF

    Integrates pre-calculated single crystal diffraction patterns
    over an orientation distribution function. 

    Parameters
    ----------
    dV: 1D ndarray, float
        volume element of the angular grid
    Isc : 2D ndarray, float
        single crystal detector images for each orientation
        dim: 0: rotations, 1: detector points
    odf : 1D ndarray, float
        probability for each orientation
    
    Return values
    ------------
    image : 1D ndarray, float
        simulated diffraction pattern
    """
    image = (odf * dV) @ Isc
    return image

@njit()
def _imageFromC( c, difflets ):
    """Computes a diffraction image from custom parameters
    Statically typed to enable jitting
    Weights pre-calculated sHSH diffraction patterns with coefficients
    to make a custom diffraction pattern

    Parameters
    ----------
    c : 1D ndarray, float
        set of sHSH coefficients
    difflets : 2D ndarray, float
        diffractlets to be summed
        dim 0: sHSH index, 1: detector point index
    
    Return values
    ------------
    image : 1D ndarray, float
        simulated diffraction pattern
    """
    image = c @ difflets # sum over sHSH-images without isotropic part
    return image

@njit()
def _odfFromC( sHSHs, c ):
    """ Computes a diffraction image from a set of sHSH coefficients

    Parameters
    ----------
    c : 1D ndarray, float
        set of sHSH coefficients
    
    Return values
    ------------
    odf : 1D ndarray, float
        probability for each orientation
    """
    # renormalize to c0 = 1    
    c1plus = c[1:]/c[0]

    ## produces an ODF from HSH-coefficients
    odf = 1 + c1plus @ sHSHs

    return odf.astype(data_type)

@njit(parallel=True)
def _odf_max_stack( C, sHSHs, Gc,  V_fz ):
    """ Computes ODFs for a stack of sets of sHSH coefficients
    and returns the orientation at the maximum of the ODF

    Parameters
    ----------
    C : 2D ndarray, float
        set of sHSH coefficients for each voxel
        dim: 0: voxel index, 1: sHSH index
    sHSHs : 2D ndarray, float   
        all used sHSHs
        dim: 0: rotation index, dim 1: sHSH index
    Gc : 2D ndarray, float
        register of axis-angle rotations
        dim: 0: rotation index, 1: [omega, theta, phi]
    V_fz : float
        volume of the fundamental zone
    mask_voxels : 1D ndarray, bool
        mask for including the voxel in the analysis or not
        dim: 0: voxel index
        
    Return values
    ------------
    g_max : 2D ndarray, float
        register of axis-angle rotations
        dim: 0: voxel index, 1: [omega, theta, phi]
    """
    Nvox = C.shape[0]
    g_max = np.empty((Nvox,3), data_type)
    for k in prange(Nvox):
        odf = _odfFromC( sHSHs, C[k] ) # calculate the odf
        # get preferred orientation at the maximum value
        ig = np.argmax(odf) # index of the maximum of the odf
        g_max[k] = Gc[ig]
    return g_max

@njit(parallel=True)
def _odf_std_fromZero_stack( c, Rs, V_fz, sHSHs, dV, ome):
    """Computes the standard deviation of the ODF with the 
    mean value centered at 0

    Parameters
    ----------
    c : 1D ndarray, float
        set of sHSH coefficients
    
    Return values
    ------------
    odf : 1D ndarray, float
        probability for each orientation
    """
    std = []
    for k in prange(c.shape[0]):
        odf = _odfFromC( sHSHs, Rs[k] @ c[k] ) # calculate the odf
        odf[odf < 0] = 0 # clip negative values
        odf = odf / ( odf @ dV ) # renormalize
        std.append( np.sqrt( ( odf * ome**2 ) @ dV ) )
    return np.array(std)

@njit(parallel=True)
def _directions_from_orientations( orientations, direction_0 ):
    """ Calculates the crystal axis orientations from OTP orientations

    Should be generalized to all crystal systems using the actual axes

    Parameters
    ----------
    g_pref : 2D ndarray, float
        dim: 0: voxel index, 1: [ome,tta,phi]

    returns: 
    ------------
    a_pref, b_pref, c_pref : 2D ndarray, float
        crystal axis unit vectors
        dim: 0: voxel index, 1: [x,y,z]
    """
    Nvox = orientations.shape[0]
    directions = np.empty((Nvox,3), data_type)

    for k in prange(Nvox):
        # get preferred orientation for all axes
        R_pref  = rot.OTP_to_matrix( orientations[k,0], orientations[k,1], orientations[k,2])
        directions[k] = direction_0 @ R_pref 
    return directions

@njit(parallel=True)
def _abc_pref_sample( g_pref, lattice_vectors ):
    """ Calculates the crystal axis directions from OTP orientations

    Parameters
    ----------
    g_pref : 2D ndarray, float
        dim: 0: voxel index, 1: [ome,tta,phi]

    returns: 
    ------------
    a_pref, b_pref, c_pref : 2D ndarray, float
        crystal axis unit vectors
        dim: 0: voxel index, 1: [x,y,z]
    """
    Nvox = g_pref.shape[0]
    a_pref = np.empty((Nvox,3), data_type)
    b_pref = np.empty((Nvox,3), data_type)
    c_pref = np.empty((Nvox,3), data_type)

    for k in prange(Nvox):
        # get preferred orientation for all axes
        R_pref  = rot.OTP_to_matrix( g_pref[k,0], g_pref[k,1], g_pref[k,2])
        a_pref[k] = lattice_vectors[0] @ R_pref 
        b_pref[k] = lattice_vectors[1] @ R_pref 
        c_pref[k] = lattice_vectors[2] @ R_pref 
    return a_pref, b_pref, c_pref

@njit(parallel=True)
def _projection(
        g, images,
        C, # parameters
        Beams, iBeams, difflets_rot, # pre-calculated quantities
        ):
    """Simulates diffraction images from a 2D scan over the sample

    For a certain sample rotation calculates sHSH coefficients in 
    each voxel, then integrates over the beam intensity for each
    translation and makes diffraction patterns from diffractlets

    Parameters
    ----------
    g : int
        rotation index
    images : 3D ndarray, float
        simulated diffraction patterns
        dim: 0: rotation, 1: translation, 2: detector points
    C : 2D ndarray, float
        set of sHSH coefficients for each voxel
        dim: 0: voxel index, 1: sHSH index
    Beams : 3D ndarray, float
        sparse-array containing beam intensity for all configurations
        dim: 0: rotation, 1: translation, 2: voxel (sparse)
    iBeams : 3D ndarray, int
        array of indices for the sparse Beams array
        dim: 0: rotation, 1: translation, 2: voxel index
    difflets_rot : 3D ndarray, float
        diffractlets for rotation g
        dim: 0: sHSH indices, 1: detector points

    returns: 
    ------------
    images : 3D ndarray, float
        modified simulated diffraction patterns
        dim: 0: rotation, 1: translation, 2: detector points
    """
    images = np.array((Beams.shape[1], difflets_rot.shape[1]), data_type)
    for t in prange( Beams.shape[1] ): # scan over the sample
        iend = np.searchsorted(iBeams[g,t,:],2**32-1) # for sparsearray
        # get projected coefficients for the corresponding beam rotation/translation
        c_proj = integrate_c( Beams[g,t,:iend], iBeams[g,t,:iend], C)
        # calculate the image
        images[t,:] = c_proj @ difflets_rot 
    return images

@njit()
def rotate_difflets_stack( Rs_stack, difflets ):
    ''' calculates the symmetrized HSH rotation matrices and the corresponding
    diffraction images for all sHSHs of order n and all rotations Gs
    '''
    difflets_stack = np.zeros( (Rs_stack.shape[0], difflets.shape[0], difflets.shape[1]), np.float64 )
    for g, Rs_g in enumerate(Rs_stack):
        difflets_stack[g] = Rs_g @ difflets
    
    return difflets_stack

@njit(parallel=True)
def Rs_n_stack( Gs, n, Xsn ):
    ''' calculates sHSH rotation matrices for all rotation Gs and order n
    '''
    Rs_stack = np.zeros( (Gs.shape[0], Xsn.shape[0], Xsn.shape[0]), np.float64 )
    for g in prange(Gs.shape[0]):
        Rs_stack[g] = Rs_n( Gs[g], n, Xsn )
    
    return Rs_stack

@njit()
def Rs_n( g, n, Xsn ):
    ''' calculates a single sHSH rotation matrix for a rotation g and order n
    '''
    R = hsh.R( n, g, np.array([0.,0.,0.]) ) # this is the HSH rotation matrix
    sR = np.real( np.conj( Xsn ) @ R @ Xsn.T ) # here it's converted to sHSH
    return sR
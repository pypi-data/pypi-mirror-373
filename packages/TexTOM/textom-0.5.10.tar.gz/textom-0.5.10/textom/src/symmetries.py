import numpy as np
import sys
import os

from . import handle as hdl
from ..config import data_type

""" Library that connects point group symmetries to rotations
    and hyperspherical harmonics. partially depends on the 
    matlab files written by J.Mason in the sub-folder """

def zone(proper_point_group, g):
    """Computes the fundamental zone in Rodrigues space for given sample symmetries

    This function constructs a bool-array that can constrict the
    used rotations to the unique ones with respect to symmetries
    in the sample and containing crystals. The corresponding region
    in the rotation space (fundamental zone) is found by converting
    to Rodrigues parametrization and by applying the inequalities
    corresponding to the symmetry, as explained in:
    Heinz, A., and P. Neumann. Acta Crystallographica Section A 
        Foundations of Crystallography 47, no. 6 (November 1, 1991): 
        780–89. https://doi.org/10.1107/S0108767391006864.

    Parameters
    ----------
    proper_point_group : str
        name of the set of rotation symmetries, taken from a provided table
        # add numbering?
    g : 2D ndarray, float
        array of rotations given by angles: [omega, theta, phi]
        where omega is the rotation angle, theta the polar and phi
        the azimutal angle of the rotation axis
        dimensions: 0: rotation index, 1: ome,tta,phi

    Return values
    ------------
    fz : ndarray, bool
        array containing True if the corresponding rotation lies
        in the fundamental zone, False if not
    """
    # transform to Rodrigues vector components
    R1 = np.tan(g[:,0]/2) * np.sin(g[:,1]) * np.cos(g[:,2])
    R2 = np.tan(g[:,0]/2) * np.sin(g[:,1]) * np.sin(g[:,2])
    R3 = np.tan(g[:,0]/2) * np.cos(g[:,1])
    
    match proper_point_group:
        case ('1' | 'C1'): # 1, m // C1
            fz = np.full((g.shape[0]), True)

        case ('2' | 'C2'): # 2, 2/m, mm2, -4 // C2
            fz = np.logical_and.reduce((
                np.abs(R2) <= 1,
            ))
 
        case ('222' | 'D2'): # 222, mmm, -42m // D2
            fz = np.logical_and.reduce((
                np.abs(R1) <= 1,
                np.abs(R2) <= 1,
                np.abs(R3) <= 1,
            ))

        case ('4' | 'C4'): # 4, 4/m // C4
            fz = np.logical_and.reduce((
                np.abs(R1) <= 1,
                np.abs(R2) <= 1,
                +R1+R2 <= np.sqrt(2),
                -R1+R2 <= np.sqrt(2),
                -R1-R2 <= np.sqrt(2),
                +R1-R2 <= np.sqrt(2),
            ))

        case ('422' | 'D4'): # 422, 4/mmm // D4
            fz = np.logical_and.reduce((
                np.abs(R1) <= 1,
                np.abs(R2) <= 1,
                np.abs(R3) <= 1,
                R3 <= np.sqrt(2)-1,
                -R3 <= np.sqrt(2)-1,
                +R1+R2 <= np.sqrt(2),
                -R1+R2 <= np.sqrt(2),
                -R1-R2 <= np.sqrt(2),
                +R1-R2 <= np.sqrt(2),
            ))

        # tan(120deg/2) = sqrt(3)
        case ('3' | 'C3'): # 3, 3m1, 31m, -3, -6 // C3
            a = -1/2 # cos(120)
            b = np.sqrt(3)/2 # sin(120)
            fz = np.logical_and.reduce((       
                +a*R1 +b*R2 <= 1,
                -a*R1 +b*R2 <= 1,
                +a*R1 -b*R2 <= 1,
                -a*R1 -b*R2 <= 1,                
                +b*R1 +a*R2 <= 1,
                -b*R1 +a*R2 <= 1,
                +b*R1 -a*R2 <= 1,
                -b*R1 -a*R2 <= 1,        
            ))

        case ('32' | 'D3'): # 321, 312, -31m, -3m1, -6m2 // D3
            a = -1/2 # cos(120)
            b = np.sqrt(3)/2 # sin(120)
            fz = np.logical_and.reduce((      
                np.abs(R3) <= 1, # 180 deg rotation
                +a*R1 +b*R2 <= 1,
                -a*R1 +b*R2 <= 1,
                +a*R1 -b*R2 <= 1,
                -a*R1 -b*R2 <= 1,                
                +b*R1 +a*R2 <= 1,
                -b*R1 +a*R2 <= 1,
                +b*R1 -a*R2 <= 1,
                -b*R1 -a*R2 <= 1,      
            ))

        case ('6' | 'C6'): # 6, 6/m, 6mm // C6
            a = 1/2 # cos(60)
            b = np.sqrt(3)/2 # sin(60)
            fz = np.logical_and.reduce((
                np.abs(R1) <= 1, # 180 deg rotation
                np.abs(R2) <= 1, # 180 deg rotation
                +a*R1 +b*R2 <= 1,
                -a*R1 +b*R2 <= 1,
                +a*R1 -b*R2 <= 1,
                -a*R1 -b*R2 <= 1,                
                +b*R1 +a*R2 <= 1,
                -b*R1 +a*R2 <= 1,
                +b*R1 -a*R2 <= 1,
                -b*R1 -a*R2 <= 1,          
            ))

        case ('622' | 'D6'): # 622, 6/mmm // D6
            a = 1/2
            b = np.sqrt(3)/2
            fz = np.logical_and.reduce((
                np.abs(R1) <= 1, # 180 deg rotation
                np.abs(R2) <= 1, # 180 deg rotation
                np.abs(R3) <= 1, # 180 deg rotation
                +a*R1 +b*R2 <= 1,
                -a*R1 +b*R2 <= 1,
                +a*R1 -b*R2 <= 1,
                -a*R1 -b*R2 <= 1,                
                +b*R1 +a*R2 <= 1,
                -b*R1 +a*R2 <= 1,
                +b*R1 -a*R2 <= 1,
                -b*R1 -a*R2 <= 1,
                +a +b*R3 <= 1,
                -a +b*R3 <= 1,
                +a -b*R3 <= 1,
                -a -b*R3 <= 1,
                +b +a*R3 <= 1,
                -b +a*R3 <= 1,
                +b -a*R3 <= 1,
                -b -a*R3 <= 1,               
            ))

        case ('23' | 'T'): # 23, -43m,  m-3 // T
            fz = np.logical_and.reduce((
                # missing ############## ?
                R1 <= np.sqrt(2)-1,
                -R1 <= np.sqrt(2)-1,
                R2 <= np.sqrt(2)-1,
                -R2 <= np.sqrt(2)-1,
                R3 <= np.sqrt(2)-1,
                -R3 <= np.sqrt(2)-1,
            ))

        case ('432' | 'O'): # 432, m-3m // O
            fz = np.logical_and.reduce((
                R1 <= np.sqrt(2)-1,
                -R1 <= np.sqrt(2)-1,
                R2 <= np.sqrt(2)-1,
                -R2 <= np.sqrt(2)-1,
                R3 <= np.sqrt(2)-1,
                -R3 <= np.sqrt(2)-1,
                +R1+R2+R3 <= 1,
                -R1+R2+R3 <= 1,
                -R1-R2+R3 <= 1,
                -R1-R2-R3 <= 1,
                +R1-R2+R3 <= 1,
                +R1-R2-R3 <= 1,
                +R1+R2-R3 <= 1,
            ))
            
        case _:
            print('Point group not recognized')
            sys.exit(1)
    return fz

def generators( proper_point_group ):
    """ Provides the symmetry generators for the given point group
    by 3 angles for axis-angle parametrization [omega, theta, phi]

    Parameters
    ----------
    proper_point_group : str
        name of the crystal symmetry, taken from a provided table

    Return values
    ------------
    gen : 2D ndarray, float
        2 symmetry generators in OTP representation
        [[ome1,tta1,phi1], [ome2,tta2,phi2]]
    """
    g1 = [2*np.pi, 0, 0]; # no rotation, any mirror, glide or rotation-inversion

    g2z = [np.pi, 0., 0.]; # 2nd order rotation around [001]: 2, 2/m
    g2p = [np.pi, np.pi/2, 0.]; # 2nd order rotation around [100]: _2, _2/m
    g2d = [np.pi, np.pi/2, np.pi/4]; # 2nd order rotation around [110]

    g3z = [2*np.pi/3, 0., 0.]; # 3rd order rotation around [001]: 3, 3/m
    g3d = [2*np.pi/3, np.arctan(np.sqrt(2)), np.pi/4]; # 3rd order rotation around [111]: _3

    g4z = [np.pi/2, 0., 0.]; # 4th order rotation around [001]: 4, 4/m
    g4p = [np.pi/2, np.pi/2, 0.]; # 4th order rotation around [100]: 4, 4/m

    g6z = [np.pi/3, 0., 0.]; # 3rd order rotation around [001]: 6, 6/m

    match proper_point_group:
        case ('1' | 'C1'): # 1, m // C1
            gen = np.array((g1,g1),data_type)
        case ('2' | 'C2'): # 2, 2/m, mm2, -4 // C2
            gen = np.array((g2z,g1),data_type)
        case ('222' | 'D2'): # 222, mmm, -42m // D2
            gen = np.array((g2z,g2p),data_type)
        case ('4' | 'C4'): # 4, 4/m // C4
            gen = np.array((g4z,g1),data_type)
        case ('422' | 'D4'): # 422, 4/mmm // D4
            gen = np.array((g4z,g2p),data_type)
        case ('3' | 'C3'): # 3, 3m1, 31m, -3, -6 // C3
            gen = np.array((g3z,g1),data_type)
        case ('32' | 'D3'): # 321, 312, -31m, -3m1, -6m2 // D3
            gen = np.array((g3z,g2p),data_type)
        case ('6' | 'C6'): # 6, 6/m, 6mm // C6
            gen = np.array((g6z,g1),data_type)
        case ('622' | 'D6'): # 622, 6/mmm // D6
            gen = np.array((g6z,g2p),data_type)
        case ('23' | 'T'): # 23, -43m,  m-3 // T
            gen = np.array((g2z,g3d),data_type)
        case ('432' | 'O'): # 432, m-3m // O
            gen = np.array((g4z,g3d),data_type)
        case _:
            print('Point group not recognized')
            sys.exit(1)
    return gen

def cSymmHSH(point_group, n):
    """Loads a matrix to transform HSHs to sHSHs

    loads sets of coefficients that make the hyperspherical 
    harmonic expansion invariant a certain crystal symmetry. 
    These can  be interpreted as defining a compact basis
    for an orientation distribution obeying the required symmetry, 
    namely, the symmetrized hyperspherical harmonics (sHSHs).

    This function loads from files created separately by Matlab
    functions in ressources/symmetrizedHSH

    Parameters
    ----------
    proper_point_group : str
        name of the crystal symmetry, taken from a provided table
    n : int
        order of the HSHs

    Return values
    ------------
    nlm : ndarray, int
        HSH indices corresponding to the coefficients
    c : 2D ndarray, complex
        matrix of HSH coefficients for all sHSHs for given n and lattice
        dimensions: 0: HSH orders, 1: sHSHs
    """
    path_csym = hdl.get_file_path('textom',
            os.path.join('ressources','symmetrizedHSH','output',
                         point_group + '_n' + str(n)))
    # filename = 'ressources/symmetrizedHSH/output/' + point_group + '_n' + str(n)
    if os.path.isfile(path_csym):
        data = np.genfromtxt(
            path_csym,
            dtype=np.complex128,
            skip_header=1,
            skip_footer=0,
        )
        
        nlm = data[:,:3].real.astype(int)
        c = data[:,3:].T
        return nlm, c
    
    else:
        print('Symmetrized HSH base file does not exist. Check for typos or generate it via matlab files')
        sys.exit(1)

def get_NsHSH(point_group, n):
    """ Returns how many sHSHs exist for the respective point group and order

    Parameters
    ----------
    point_group : str
        name of the crystal symmetry, taken from a provided table
    n : int
        order of the HSHs
    """
    if np.mod(n,2):
        return 0
    elif n==0:
        return 1
    else:
        path_overview = hdl.get_file_path('textom',
            os.path.join('ressources','symmetrizedHSH','output','overview.txt'))
        with open(path_overview, "r") as file:
                NsHSH_all = eval( file.read() )[point_group]
        return NsHSH_all[int(n/2-1)]

def get_SFnotation( point_group ):
    """Transforms proper point group from Hermann-Mauguin notation to Schonflies
    """
    convdict = {
        '1': 'C1',
        '2': 'C2',
        '222': 'D2',
        '4': 'C4',
        '422': 'D4',
        '3': 'C3',
        '32': 'D3',
        '6': 'C6',
        '622': 'D6',
        '23': 'T',
        '432': 'O',
    }
    return convdict[point_group]

def get_proper_point_group(space_group_number):
    """
    Determine the proper point group from the space group IT number, accounting for equivalent symmetries.

    Parameters:
        space_group_number (int): The IT number of the space group.

    Returns:
        str: The proper point group symbol, or "Unknown" for invalid inputs.
    """
    # consider also:
    # from orix.quaternion.symmetry import get_point_group

    # Define ranges of space groups and their proper point groups (reduced symmetry)
    proper_point_groups = {
        "Triclinic": {range(1, 3): "1"},  # Space groups 1-2
        "Monoclinic": {range(3, 16): "2"},  # Space groups 3-15
        "Orthorhombic": {range(16, 75): "222"},  # Space groups 16-74
        "Tetragonal": {
            range(75, 89): "4",  # Space groups 75-88
            range(89, 143): "422",  # Space groups 89-142
        },
        "Trigonal": {
            range(143, 149): "3",  # Space groups 143-148
            range(149, 168): "32",  # Space groups 149-167
        },
        "Hexagonal": {
            range(168, 177): "6",  # Space groups 168-176
            range(177, 195): "622",  # Space groups 177-194
        },
        "Cubic": {
            range(195, 209): "23",  # Space groups 195-206
            range(209, 231): "432",  # Space groups 207-230
        },
    }

    # Iterate through the dictionary to find the matching range and return the proper point group
    for system, groups in proper_point_groups.items():
        for spg_range, proper_pg in groups.items():
            if space_group_number in spg_range:
                return proper_pg

    return "Unknown"  # For invalid space group numbers
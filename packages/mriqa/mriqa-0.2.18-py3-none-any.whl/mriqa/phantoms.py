# -*- coding: utf-8 -*-
"""phantoms.py: phantom descriptions and segmentations."""

from itertools import product

import numpy as np
from scipy.interpolate import interp1d

from skimage.transform import hough_circle, hough_circle_peaks
from skimage.measure import label, regionprops
from skimage.morphology import disk, binary_erosion, binary_dilation

from skimage.filters import threshold_otsu
from skimage.feature import canny


# Standard DOH Uniformity and SNR phantom
TO1 = {
    'Name': 'TO1',
    'Diameter': 188,  # mm
    'PD': 1.0,
    'T1': 500.0,
    'T2': 500.0,
    'Features': {
        'Holes': [
            (( 82, -10), (6, 6)),
            (( 10,  82), (6, 6)),
            ((-82,  10), (6, 6)),
            ((-10, -82), (6, 6))
        ]
    }
}

# Standard DOH phantom for slice thickness and distortion
# There are plates and wedges for slice thickness, and a box for distortion.
# The standard orientation is with plates going AP in an axial acquisition.
TO2 = {
    'Name': 'TO2',
    'Diameter': 188,  # mm
    'PD': 1.0,
    'T1': 500.0,
    'T2': 500.0,
    'Features': {
        'Holes': [
            (( 82, -10), (6, 6)),
            (( 10,  82), (6, 6)),
            ((-82,  10), (6, 6)),
            ((-10, -82), (6, 6))
        ],
        'Wedges': [
            ((-21, -35), (16, 70)),
            ((-47, -35), (16, 70))
        ],
        'Plates': [
            (( 5, -50), (10, 100)),
            ((30, -50), (10, 100))
        ],
        'Boxes': [
            ((-66, -66), (132, 132))
        ]
    },
    'FeatureSizes': {
        'Boxes': [
            12.5
        ]
    },
    'FeatureAngles': {
        'Plates': 11.7,  # degrees
        'Wedges': 11.7
    },
    'FeatureAxes': {
        'Plates': 0,
        'Wedges': 0
    }
}

# Local variant of TO2 with just single pair of plates (different angle)
# The standard orientation is with plates going LR an anaxial acquisistion.
TO2B = {
    'Name': 'TO2B',
    'Diameter': 188,  # mm
    'PD': 1.0,
    'T1': 500.0,
    'T2': 500.0,
    'Features': {
        'Holes': [
            (( 82, -10), (6, 6)),
            (( 10,  82), (6, 6)),
            ((-82,  10), (6, 6)),
            ((-10, -82), (6, 6))
        ],
        'Wedges': [],
        'Plates': [
            ((-25,  20), (50, 20)),
            ((-25, -40), (50, 20))
        ],
        'Boxes': [
            ((-67, -67), (134, 134))
        ]
    },
    'FeatureSizes': {
        'Boxes': [
            10.0
        ]
    },
    'FeatureAngles': {
        'Plates': 27  # degrees (guess)
    },
    'FeatureAxes': {
        'Plates': 1
    }
}


# Standard DOH phantom for slice position and slice warp.
# TODO: There is an array of crossing objects to define.
TO3 = {
    'Name': 'TO3',
    'Diameter': 188,  # mm
    'PD': 1.0,
    'T1': 500.0,
    'T2': 500.0,
    'Features': {
        'Holes': [
            (( 82, -10), (6, 6)),
            (( 10,  82), (6, 6)),
            ((-82,  10), (6, 6)),
            ((-10, -82), (6, 6))
        ]
    }
}

# Standard DOH phantom for resolution. The phantom has a set of
# bars that are assummed to run AP in axial images.
# In addition, there are two square mtf blocks.
TO4 = {
    'Name': 'TO4',
    'Diameter': 188,  # mm
    'PD': 1.0,
    'T1': 500.0,
    'T2': 500.0,
    'Features': {
        'Holes': [
            (( 48, -62), (6, 6)),
            ((-65, -54), (6, 6)),
            ((-56,  63), (6, 6)),
            (( 52,  63), (6, 6))
        ],
        'Blocks': [
            ((-60, -67), (55, 55)),
            ((-59,  15), (50, 50))
        ],
        'Bars': [
            ((-79, -12), ( 7,  24)),  # 0.3 mm
            (( 42,  19), (10,  26)),  # 0.5 mm
            ((  0, -62), (16, 126)),  # 1.0 mm
            (( 46, -48), (18,  52)),  # 1.5 mm
            (( 20, -62), (20, 126))   # 2.0 mm
        ]
    },
    'FeatureSizes': {
        'Bars': [0.3, 0.5, 1.0, 1.5, 2.0]
    }
}

# A local variant of TO4, which different bars positioning and sizes
TO4B = {
    'Name': 'TO4B',
    'Diameter': 188,  # mm
    'PD': 1.0,
    'T1': 500.0,
    'T2': 500.0,
    'Features': {
        'Holes': [
        ],
        'Blocks': [
            ((-70, 35), (80, 30))
        ],
        'Bars': [
            (( 37,  38), (26,   6)),  # 0.3 mm
            (( 37, -58), (27,   8)),  # 0.5 mm
            ((-65, -22), (128, 16)),  # 1.0 mm
            ((-48,   7), (52,  17)),  # 1.5 mm
            ((-65, -46), (128, 20)),  # 2.0 mm
            ((-49, -74), (52,  26)),  # 2.5 mm
            ((  3,  -4), (50,  28)),  # 3.0 mm

        ]
    },
    'FeatureSizes': {
        'Bars': [0.3, 0.5, 1.0, 1.5, 2.0, 2.5, 3]  # mm
    }
}

# A local variant of TO4, which different bars positioning and sizes
TO4C = {
    'Name': 'TO4C',
    'Diameter': 190,  # mm
    'PD': 1.0,
    'T1': 500.0,
    'T2': 500.0,
    'Features': {
        'Holes': [
        ],
        'Blocks': [
            ((-68, 26), (66, 28))
        ],
        'Bars': [
            ((-86,  -2), (22,   6)),  # 0.5 mm
            ((-85, -17), (172, 11)),  # 1.0 mm
            ((-38,  -2), (33,  14)),  # 1.5 mm
            ((-83, -40), (162, 20)),  # 2.0 mm
            ((-65, -65), (24,  23)),  # 2.5 mm
            ((-32, -70), (29,  28)),  # 3.0 mm
            (( -2, -84), (44,  43)),  # 5.0 mm
        ]
    },
    'FeatureSizes': {
        'Bars': [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 5.0]  # mm
    }
}


# Bespoke spherical phantom filled with silicone oil
OILSPHERE = {
    'Name': 'OILSPHERE',
    'Diameter': 155.0,  # mm
    'PD': 0.71,  # from doi://10.1002/mp.13429
    'T1': float('nan'),
    'T2': float('nan'),
    'Features': {}
}


# Small spherical phantom for ghosting
GE10CMSPHERE = {
    'Name': 'GE10CMSPHERE',
    'Diameter': 100.0,  # mm
    'PD': 1.0,
    'T1': float('nan'),
    'T2': float('nan'),
    'Features': {}
}


# Siemens long bottle used in head coil
SIEMENSLONGBOTTLE = {
    'Name': 'SIEMENSLONGBOTTLE',
    'Diameter': 133.0,  # mm
    'PD': 1.0,
    'T1': 100.0,
    'T2': 100.0,
    'Features': {}
}

# Siemens shorter, wider bottle on older scanners
SIEMENSSHORTBOTTLE = {
    'Name': 'SIEMENSSHORTBOTTLE',
    'Diameter': 160.0,  # mm
    'PD': 1.0,
    'T1': 100.0,
    'T2': 100.0,
    'Features': {}
}

# Siemens 2L sphere, with 1.25g/L Nickel Sulphate
SIEMENSD165 = {
    'Name': 'SIEMENSD165',
    'Diameter': 165.0,  # mm
    'PD': 1.0,
    'T1': 100.0,
    'T2': 100.0,
    'Features': {}
}

# Phantom used in quarterly QA on GE DIscovery
GED155 = {
    'Name': 'GED155',
    'Diameter': 154.5,  # mm
    'PD': 1.0,
    'T1': 100.0,
    'T2': 100.0,
    'Features': {}
}

# ACR NEMA Phantom, Basic Definition
ACR40 = {
    'Name': 'ACR40',
    'Diameter': 190,  # mm
    'PD': 1.0,
    'T1': 500.0,
    'T2': 500.0,
    'Features': {}
}

# ACR NEMA Phantom, Slice Profile Section
ACRSP = {
    'Name': 'ACRSP',
    'Diameter': 190,  # mm
    'PD': 1.0,
    'T1': 500.0,  # TODO: estimate from 10mM Ni2+
    'T2': 500.0,
    'Features': {
        'Plates': [
            ((-50, -7), (100, 4)),
            ((-50, -1), (100, 4))
        ]
    },
    'FeatureAngles': {
        'Plates': 5.71  # from Phantom Guidance
    },
    'FeatureAxes': {
        'Plates': 1  # horizontal
    }
}

PHILIPS3LBOTTLE = {
    'Name': 'PHILIPS3LBOTTLE',
    'Diameter': 157.0,  # mm
    'PD': 1.0,
    'T1': float('nan'),
    'T2': float('nan'),
    'Features': {}
}

PHILIPS2LBOTTLE = {
    'Name': 'PHILIPS2LBOTTLE',
    'Diameter': 133.0,  # mm
    'PD': 1.0,
    'T1': float('nan'),
    'T2': float('nan'),
    'Features': {}
}

PHILIPS1L5BOTTLE = {
    'Name': 'PHILIPS1L5BOTTLE',
    'Diameter': 117.0,  # mm
    'PD': 1.0,
    'T1': float('nan'),
    'T2': float('nan'),
    'Features': {}
}

# Philips PIQT Phantom, Basic Definition
PIQT = {
    'Name': 'PIQT',
    'Diameter': 190,  # mm
    'PD': 1.0,
    'T1': 500.0,
    'T2': 500.0,
}

# Philips PIQT Phantom, Slice Profile Section
PIQTSP = {
    'Name': 'PIQTSP',
    'Diameter': 190,  # mm
    'PD': 1.0,
    'T1': 500.0,
    'T2': 500.0,
    'Features': {
        'Plates': [
            ((-40, -55), (80, 20)),
            ((-40, -18), (80, 20))
        ],
        'Wedges': [
            ((-40, 20), (80, 20))
        ]
    },
    'FeatureAngles': {
        'Plates': 11.7,  # TODO: need to check this
        'Wedges': 11.7
    },
    'FeatureAxes': {
        'Plates': 1,  # horizontal
        'Wedges': 1
    }
}

# Philips PIQT Phantom, Uniform SNR section (no features)
PIQTSNR = {
    'Diameter': 190,
    'PD': 1.0,
    'T1': 500.0,
    'T2': 500.0
}

# Philips PIQT Phantom, Resolution section (square MTF block)
PIQTMTF = {
    'Diameter': 190,
    'PD': 1.0,
    'T1': 500.0,
    'T2': 500.0,
    'Features': {
        'Blocks': [
            ((-45, -95), (90, 90))
        ]
    }
}


# Philips PIQT Phantom, Distortion Grid Section
def _make_piqtdist(n=7, spacing_mm=25):
    """Generate description of 'spots' in PIQT phantom."""
    # Lower and upper range of indices about zero
    l, u = -(n//2), n//2

    # One point missing in each corner
    excluded_points = list(product([l, u], [l, u]))
    points = [
        point
        for point in product(range(l, u+1), range(l, u+1))
        if point not in excluded_points
    ]
    points_mm = [(x*spacing_mm, y*spacing_mm) for (x, y) in points]

    # One row and column less
    central_points = list(
        product(range(l+1, u), range(l+1, u))
    )
    central_points_mm = [
        (x*spacing_mm, y*spacing_mm) for (x, y) in central_points
    ]

    return {
        'Name': 'PIQTDIST',
        'Diameter': 190,
        'PD': 1.0,
        'T1': 500.0,
        'T2': 500.0,
        'Features': {
            'GridPoints': points_mm,
            'InnerPoints': central_points_mm
        },
        'FeatureSizes': {
            'GridPoints': spacing_mm,
            'InnerPoints': spacing_mm
        }
    }


PIQTDIST = _make_piqtdist()


# ACR NEMA Phantom, Distortion Grid Section
def _make_acrdist(n=11, spacing_mm=15):
    """Generate description of 'crosses' in ACR phantom distortion grid."""
    # Lower and upper range of indices about zero
    l, u = -(n//2), n//2

    # Three points missing in each corner
    excluded_points = [
        (l, l), (l, u), (u, l), (u, u),
        (l, l+1), (l, u-1), (l+1, l), (l+1, u),
        (u, l+1), (u, u-1), (u-1, l), (u-1, u)
    ]
    points = [
        point
        for point in product(range(l, u+1), range(l, u+1))
        if point not in excluded_points
    ]
    points_mm = [
        (x*spacing_mm, y*spacing_mm) for (x, y) in points
    ]

    # Two rows and columns less
    central_points = list(
        product(range(l+2, u-1), range(l+2, u-1))
    )
    central_points_mm = [
        (x*spacing_mm, y*spacing_mm) for (x, y) in central_points
    ]

    return {
        'Name': 'ACRDIST',
        'Diameter': 190,
        'PD': 1.0,
        'T1': 500.0,
        'T2': 500.0,
        'Features': {
            'GridPoints': points_mm,
            'InnerPoints': central_points_mm
        },
        'FeatureSizes': {
            'GridPoints': spacing_mm,
            'InnerPoints': spacing_mm
        }
    }


ACRDIST = _make_acrdist()

# ACR NEMA Small Phantom, Basic Definition
ACRSMALL40 = {
    'Name': 'ACRSMALL40',
    'Diameter': 100,  # mm
    'PD': 1.0,
    'T1': 500.0,
    'T2': 500.0,
    'Features': {}
}

# ACR NEMA Small Phantom, Slice Profile Section
ACRSMALLSP = {
    'Name': 'ACRSMALLSP',
    'Diameter': 100,  # mm
    'PD': 1.0,
    'T1': 500.0,  # TODO: estimate from 10mM Ni2+
    'T2': 500.0,
    'Features': {
        'Plates': [
            ((-40, 0), (80, 3)),
            ((-40, -4), (80, 3))
        ]
    },
    'FeatureAngles': {
        'Plates': 5.71  # from Phantom Guidance
    },
    'FeatureAxes': {
        'Plates': 1  # horizontal
    }
}

# ACR NEMA Phantom, High Contrast Resolution Spots Definitions
ACRRES = {
    'Name': 'ACRRES',
    'Diameter': 190,  # mm
    'PD': 1.0,
    'T1': 500.0, # TODO: estimate from 10mM Ni2+ 
    'T2': 500.0,
    'Features': {
        'Spots': [
            ((-25, 25), (20, 25)),
            ((-2, 25), (20, 25)),
            ((21, 25), (20, 25))
        ],       
    }
}


# ACR NEMA Small Phantom, High Contrast Resolution Spots Definitions
ACRSMALLRES = {
    'Name': 'ACRSMALLRES',
    'Diameter': 100,  # mm
    'PD': 1.0,
    'T1': 500.0, # TODO: estimate from 10mM Ni2+ 
    'T2': 500.0,
    'Features': {
        'Spots': [ # x, y, dx, dy
            ((-30, -23), (18, 16)),
            ((-10, -23), (18, 16)),
            (( 11, -23), (18, 16))
        ],       
    }
}

# ACR NEMA Phantom, Low Contrast Spots Definitions
ACRCONTRAST = {
    'Name': 'ACRCONTRAST',
    'Diameter': 190,  # mm
    'PD': 1.0,
    'T1': 500.0, # TODO: estimate from 10mM Ni2+ 
    'T2': 500.0,
    'Features': {
        'Circle': [
            (128, 128+6), 44
        ],
        'Spots': [
            ((-25, 25), (20, 25)),
            ((-2, 25), (20, 25)),
            ((21, 25), (20, 25))
        ],       
        'blobs': [
            # x, y, diameter
            ((-25, 25), ),
            ((-2, 25), (20, 25)),
            ((21, 25), (20, 25))
        ],       

    }
}


# ACR NEMA Phantom v2, New Model Distortion Grid Section
def _make_acrdistnew(n=3, spacing_mm=60):
    """Generate description of 'dots' in ACR phantom distortion grid."""
    # Lower and upper range of indices about zero
    l, u = -(n//2), n//2

    points = [
        point
        for point in product(range(l, u+1), range(l, u+1))
    ]
    points_mm = [
        (x*spacing_mm, y*spacing_mm) for (x, y) in points
    ]

    return {
        'Name': 'ACRDISTNEW',
        'Diameter': 190,
        'PD': 1.0,
        'T1': 500.0,
        'T2': 500.0,
        'Features': {
            'GridPoints': points_mm,
            'InnerPoints': points_mm,
        },
        'FeatureSizes': {
            'GridPoints': spacing_mm,
            'InnerPoints': spacing_mm,
        }
    }


ACRDISTNEW = _make_acrdistnew()


# ACR NEMA Small Phantom, Distortion Grid Section
def _make_acrsmalldist():
    """Generate description of 'crosses' in small ACR phantom."""
    spacing_mm=15
    n = 7  
    name = 'ACRSMALLDIST'
    diameter = 100

    # Lower and upper range of indices about zero
    l, u = -(n//2), n//2

    # Three points missing in each corner and one fictitious line so the grid is a square. 

    excluded_points = [
        (l, l), (l + 1, l), (u - 1, l), (u, l),
        (l, l + 1), (u, l + 1),
        (l, u - 2), (u, u - 2),
        (l, u - 1), (l + 1, u - 1), (u - 1, u - 1), (u, u - 1),
        (l, u), (l + 1, u), (l + 2, u), (0, u), (u-2, u), (u-1, u), (u, u), 
    ]
        
    
    points = [
        point
        for point in product(range(l, u+1), range(l, u+1))
        if point not in excluded_points
    ]
    points_mm = [
        (x*spacing_mm, (y+0.5)*spacing_mm) for (x, y) in points
    ]

    # Two rows and columns less
    central_points = list(
        product(range(l+2, u-1), range(l+2, u-1))
    )
    central_points_mm = [
        (x*spacing_mm, (y+0.5)*spacing_mm) for (x, y) in central_points
    ]

    return {
        'Name': name,
        'Diameter': diameter,
        'PD': 1.0,
        'T1': 500.0,
        'T2': 500.0,
        'Features': {
            'GridPoints': points_mm,
            'InnerPoints': central_points_mm
        },
        'FeatureSizes': {
            'GridPoints': spacing_mm,
            'InnerPoints': spacing_mm
        }
    }

ACRSMALLDIST = _make_acrsmalldist()

# NIST Diffusion Phantom: 13 tubes with different pvp concentrations; 3 small locating tubes
_nist_dwi_tube_radius_mm = 15  # mm
_nist_dwi_lug_radius_mm = 5  # mm
_nist_dwi_centre_offset_mm = np.array([-2, -2])
_nist_dwi_tube_locations_mm = np.array([
   (0, 0),
   (30, 18),
   (30, 52),
   (-30, 52),
   (0, 35),
   (-61, 0),
   (-30, 18),
   (-30, -52),
   (-30, -18),
   (0, -35),
   (30, -52),
   (30, -18),
   (61, 0)
]) + _nist_dwi_centre_offset_mm
# These %w/w concs of PVP must be in the *same order* as the tubes in _nist_dwi_tube_locations_mm
_nist_dwi_concentrations = [0, 0, 0, 10, 10, 20, 20, 30, 30, 40, 40, 50, 50]

# We guarantee this is in increasing order of the angles subtended 30, 60, 90
# which is the order of angles going from upper right in a clockwise direction
_nist_dwi_lug_locations_mm = np.array([
    (53, -30), (-53, 30), (-53, -30)
]) + _nist_dwi_centre_offset_mm

NISTDWI = {
    'Name': 'NISTDWI',
    'Features': {
        'Tubes': _nist_dwi_tube_locations_mm,
        'Lugs': _nist_dwi_lug_locations_mm
    },
    'FeatureSizes': {
        'Tubes': _nist_dwi_tube_radius_mm,
        'Lugs': _nist_dwi_lug_radius_mm
    },
    'FeatureProperties': {
        'Concentrations': _nist_dwi_concentrations
    }
}


def nist_adc_k30(conc, temp):
    """
    Empirical relation for adc of K30 PVP

    From https://doi.org/10.1371/journal.pone.0179276

    Concentration is % (w/w)
    Temperature is degrees C

    Coefficients are c_1 (per K) and c_2 (per K per %point) 
    """
    coeffs = {
         0: (2055, 0.02617),
        10: (1594, 0.02531),
        20: (1197, 0.02749),
        30: ( 839, 0.02952),
        40: ( 546, 0.03247),
        50: ( 333, 0.03303)
    }
    temp_0 = 20.0

    c_1 = interp1d(list(coeffs.keys()), [c[0] for c in coeffs.values()])
    c_2 = interp1d(list(coeffs.keys()), [c[1] for c in coeffs.values()])

    return c_1(conc) * np.exp(c_2(conc) * (temp - temp_0))


def _best_hough_circle(edges, radii):
    """
    Locate best circle in edge map image using hough circle transform.

    The calls to hough_circle are broken into chunks to avoid
    excessive memory use. Coordinates are in pixels.

    Parameters
    ----------
    image : numpy 2D float array in range [0, 1]
            binary edge image
    radii: list or array
            a sequence of radii to consider in units of pixels

    Returns
    -------
    centre_x : float
            x coordinate of centre of best circle
    centre_y : float
            y coordinate of centre of best circle
    radius: float
            radius of best circle

    """
    # Break the list of radii into chunks of size N to reduce memory footprint
    N = 10
    radii_chunks = [radii[i:i + N] for i in range(0, len(radii), N)]

    matches = []
    for radii_chunk in radii_chunks:
        hough_maps = hough_circle(edges, radii_chunk)
        matches += list(zip(
            *hough_circle_peaks(hough_maps, radii_chunk, num_peaks=2, normalize=True)
        ))

    # Then sort all of them to get the highest peak
    _, centre_x, centre_y, radius = sorted(matches)[-1]
    return centre_x, centre_y, radius


def find_phantom(image, expected_radius=None):
    """
    Locate circular phantom in image.

    Find the best match circle for the outer edge of the phantom.

    Parameters
    ----------
    image : numpy 2D float array in range [0, 1]
            greyscale image of phantom
    expected_radius: numeric
            the expected radius of the phantom in units of pixels

    Returns
    -------
    centre_x : float
            x coordinate of centre
    centre_y : float
            y coordinate of centre
    radius: float
            the fitted radius of the phantom in units of pixels

    """
    image = np.asarray(image, dtype='float')

    assert len(image.shape) == 2
    assert np.amax(image) != np.amin(image)

    # Normalize image
    image = (image - np.amin(image)) / (np.amax(image) - np.amin(image))
    edges = canny(image, sigma=2)

    # If no expected radius given the estimate from area of threshholded image
    if expected_radius is None:
        mask = phantom_mask_2d(image)
        # Using 'filled_area' is to cope with any holes in the phantom
        area = sorted(p.filled_area for p in regionprops(label(mask)))[-1]
        expected_radius = np.sqrt(area / np.pi)

    # Search within +/- 10% of the expected radius
    rmin = int(round(expected_radius * 0.90))
    rmax = int(round(expected_radius * 1.10))

    return _best_hough_circle(edges, np.arange(rmin, rmax, 1))


def phantom_mask_2d(image, mode=None):
    """
    Generate an (eroded/dilated) mask of the phantom.

    This uses an Otsu Threshold.

    Parameters
    ----------
    image: Numpy rank-2 image array (ny,nx)
    mode: Erode or Dilate mask

    Returns
    -------
    Numpy 8 bit mask array of same dimensions

    """
    # Scale to 8 bit image, smooth and threshold
    image = np.asarray(image * (255.0/np.max(image)), 'uint8')
    mask = image >= 0.75 * threshold_otsu(image)

    # Connect and keep largest region
    labels = label(mask)
    regions = regionprops(labels)
    mask = labels == sorted(regions, key=lambda x: x.area)[-1].label

    # Morphological adjustments
    if mode is None:
        return mask

    if mode.lower() == 'erode':
        mask = binary_erosion(mask, disk(3))
    elif mode.lower() == 'dilate':
        mask = binary_dilation(mask, disk(3)) 
    return mask


def noise_background_mask_2d(image, phase_encoding='ROW', margin=10, fix_siemens_bug=True, fix_philips_bug=False, fix_ge_bug=False):
    """
    Generate mask of suitable background region for estimation of noise stats.

    Parameters
    ----------
    image: array
        rank-2 image array (ny, nx)
    phase_encoding: str
        phase encoding direction ROW | COL
    margin: int
        size of structuring element used in growing phantom mask
    fix_siemens_bug: bool
        remove first row and column to work around Siemens recon artefact
    fix_philips_bug: bool
        remove two rows at top and bottom to work around Philips recon artefact
    fix_ge_bug: bool
        remove two rows at all edges to work around GE recon artefact
    Returns
    -------
    Numpy 8 bit mask array of same dimensions as input image

    """
    background_mask = ~phantom_mask_2d(image, mode='Dilate')

    # Further erode mask to exclude ringing at edges of phantom.
    # Do as a dilation of the complement to avoid eroding the image borders.
    background_mask = ~binary_dilation(~background_mask, disk(margin))

    # Remove the area of likely phase encoding artefacts.
    # Divide image up into quadrants along the diagonals
    x, y = np.indices(background_mask.shape)
    nx, ny = len(x), len(y)
    ul = x / nx + y / ny < 1.0
    ur = x / nx - y / ny < 0
    lr = x / nx + y / ny >= 1.0
    ll = x / nx - y / ny >= 0

    # and keep just the bits clear of the phase encoding artefacts.
    if phase_encoding.upper().startswith('R'):
        # pe is along ROWs: keep top and bottom, remove sides
        background_mask &= ul & ur | ll & lr
    elif phase_encoding.upper().startswith('C'):
        # pe is along COLs: keep sides, remove top and bottom
        background_mask &= ul & ll | ur & lr
    else:
        raise ValueError(
            'Unrecognised phase encoding direction %s' % phase_encoding
        )

    # Remove the first row and column as these are artefactually set to zero
    # in Siemens images and this disturbs the noise statistics.
    if fix_siemens_bug:
        background_mask[:, 0] = 0
        background_mask[0, :] = 0

    # Remove the top and bottom two rows from philips artefactually fixed
    if fix_philips_bug:
        background_mask[:2, :] = 0
        background_mask[-2:, :] = 0

    # Remove all edges from ge (caused by distortion correction?)
    if fix_ge_bug:
        background_mask[:5, :] = 0
        background_mask[-5:, :] = 0
        background_mask[:, :5] = 0
        background_mask[:, -5:] = 0

    return background_mask


def circular_mask(image, radius, centre_x, centre_y):
    """
    Construct a disc shaped mask in an image.

    Mask is True on the *interior* of circle.

    Parameters
    ----------
    image: numpy array
        image that mask will be used with; just for shape
    radius: float
        radius of disc in pixels
    centre_x: float
        centre of disc in pixels (x)
    centre_y: float
        centre of disc in pixels (y)

    Returns
    -------
    numpy boolean array, the same shape as image

    """
    ny, nx = image.shape
    Y, X = np.ogrid[:ny, :nx]
    X, Y = X - centre_x, Y - centre_y
    return X**2 + Y**2 <= radius**2


def rectangular_mask(image, xa, xb, ya, yb):
    """
    Construct a rectangular mask in an image.

    Mask is True on *interior* of the rectangle.

    Parameters
    ----------
    image: numpy array
        image that mask will be used with; just for shape
    xa, xb: float
        extent of rectangle in x (inclusive of end points)
    ya, yb: float
        extent of rectangle in y (inclusive of end points

    Returns
    -------
    numpy boolean array, the same shape as image

    """
    ny, nx = image.shape
    Y, X = np.ogrid[:ny, :nx]
    return (
        (xa <= X) & (X <= xb) &
        (ya <= Y) & (Y <= yb)
    )


if __name__ == '__main__':
    print('No tests here yet')

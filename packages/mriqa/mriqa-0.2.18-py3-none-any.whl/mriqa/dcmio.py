"""
    dcmio.py: routines for extracting dicom header info across multiple manufacturers
"""

import re
import struct
from fnmatch import fnmatchcase
from collections.abc import Sequence
from os.path import isfile, isdir, normpath, basename, dirname, join
from glob import iglob
from datetime import datetime
from math import isnan

import numpy as np

from pydicom import dcmread
from pydicom.fileset import FileSet
from pydicom.uid import UID
from pydicom.datadict import add_private_dict_entries
from pydicom.values import convert_SQ, converters
try:
    from pydicom.charset import text_VRs
except ImportError:
    # Seems to have been dropped in pydicom 2.3.0
    text_VRs = ('SH', 'LO', 'ST', 'LT', 'UC', 'UT')
from pydicom.uid import ImplicitVRLittleEndian, ExplicitVRBigEndian
from pydicom.tag import Tag
from pydicom.datadict import private_dictionary_VR
from pydicom.errors import InvalidDicomError
from pydicom.datadict import private_dictionaries
from dcmextras.siemenscsa import csa, phoenix

# just so as to make available in this namespace as was historically the case
from dcmfetch import fetch_series  # noqa: F401


EnhancedMRImageStorage = UID('1.2.840.10008.5.1.4.1.1.4.1')


def _filter_dobjs_by_date(dobjs, studydate='all'):
    """
    Filter on ISO date.

    Used to handle StudyID ambiguity in load_series/fetch_series.
    Selects closest study to specified (ISO) date if multiple dates present.

    Parameters
    ----------
    dobjs : sequence of pydicom objects
            input dicom objects
    studydate : str
            'all' or 'earliest'/'first' or 'latest'/'last' or ISO date string

    Returns
    -------
    dobjs : list of pydicom objects
            dicom objects matching date criterion

    """
    if studydate == 'all':
        return list(dobjs)

    if not all('StudyDate' in d for d in dobjs):
        return list(dobjs)

    # Assume Study Dates are ISO date strings so sortable lexographically
    study_dates = sorted(set(d.StudyDate for d in dobjs))
    if len(study_dates) == 1:
        return list(dobjs)

    if studydate in ('earliest', 'first'):
        chosen_date = study_dates[0]
    elif studydate in ('latest', 'last'):
        chosen_date = study_dates[-1]
    else:
        # Closest to specified, NB will raise if not a valid date string
        def days_between(a, b=studydate):
            return abs((
                datetime.strptime(a, '%Y%m%d') -
                datetime.strptime(b, '%Y%m%d')).days
            )
        chosen_date = min(study_dates, key=days_between)

    return [d for d in dobjs if d.StudyDate == chosen_date]


def get_dicom_objects_with_dicomdir(dicomdir, patid, stuid, sernos):
    """
    Filter DICOM objects from a DICOMDIR file.
    Requires pydicom >= 2.2.0
    Replaces retired "patient_records" interface in earlier versions of pydicom

    Parameters
    ----------
    dicomdir: str
        DICOMDIR file
    patid: str
        Patient ID pattern (supports wildcards like 'PATIENT001*')
    stuid: str
        Study ID pattern (supports wildcards)
    sernos: list[int]
        List of series numbers to include (e.g., [1, 2, 5])

    Returns
    ----------
    List of loaded DICOM objects
    """
    fs = FileSet(dicomdir)
    dobjs = []

    # Get all patient IDs and filter by pattern
    matching_patient_ids = [
        pid for pid in fs.find_values("PatientID")
        if fnmatchcase(pid.lower(), patid.lower())
    ]

    # Process each matching patient
    for patient_id in matching_patient_ids:
        for instance in fs.find(PatientID=patient_id):
            # Load the DICOM file to access  StudyID / SeriesNumber attributes
            dobj = instance.load()
            # Filter by StudyID / SeriesNumber
            if not fnmatchcase(getattr(dobj, 'StudyID', '0'), stuid):
                continue
            if int(getattr(dobj, 'SeriesNumber', '0')) not in sernos:
                continue
            dobjs.append(dobj)

    return dobjs

def get_dicom_objects_from_directory_tree(basedir, globpattern, patid, stuid, sernos):
    """
    Filter DICOM objects from a directory hierarchy.

    Parameters
    ----------
    basedir: str
        root of directory hierarchy
    globpattern: str
            glob pattern for matching DICOM filenames
    patid: str
        Patient ID pattern (supports wildcards like 'PATIENT001*')
    stuid: str
        Study ID pattern (supports wildcards)
    sernos: list[int]
        List of series numbers to include (e.g., [1, 2, 5])

    Returns
    ----------
    List of loaded DICOM objects
    """

    # Use recursive directory walk and glob pattern to find and select dicom files
    # Clean up glob pattern for use with recursive iglob - no '/' or '**'
    globpattern = globpattern.replace('/', '')
    globpattern = re.sub(r'\*{2,}', '*', globpattern)
    dobjs = []
    for filename in iglob(join(basedir, '**', globpattern), recursive=True):
        # Exclude anything that looks like a DICOMDIR
        if basename(normpath(filename)) == 'DICOMDIR':
            continue
        # Read the file to get further information
        try:
            dobj = dcmread(filename)
        except (IOError, InvalidDicomError):
            continue
        if not fnmatchcase(dobj.PatientID.lower(), patid.lower()):
            continue
        if not fnmatchcase(dobj.StudyID, stuid):
            continue
        if int(dobj.SeriesNumber) not in sernos:
            continue
        dobjs.append(dobj)

    return dobjs


def load_series(patid, stuid='1', sernos=1, directory='.',
                globpattern='*', studydate='all', imagesonly=False):
    """
    Load QA series from DICOM files in filesystem.

    Parameters
    ----------
    patid : str
            Patient ID (allows glob style matching)
    stuid : str
            Study ID (allows glob style matching)
    sernos: int or list of ints (or convertible to int)
            Series number(s) to fetch
    directory: str
            A DICOMDIR file or a directory containing DICOM part 10 files
    globpattern: str
            glob pattern for matching DICOM filenames
    studydate :  str
            'all' or 'earliest'/'first' or 'latest'/'last' or ISO date string
    imagesonly :  bool
            Ignore non-image dicom objects

    Returns
    -------
    dobjs : list of dicom objects
            dicom objects sorted on series and instance number

    """
    # Fix up for strings and single numbers and remove duplicates
    if isinstance(sernos, str) or not isinstance(sernos, Sequence):
        sernos = [sernos]
    sernos = list(set(map(int, sernos)))

    # Look for a DICOMDIR either specified as a file or at top level of directory
    if isfile(directory):
        dicomdir = directory
        basedir = dirname(normpath(directory))
    elif isdir(directory):
        dicomdir = join(directory, 'DICOMDIR')
        basedir = normpath(directory)
    else:
        raise OSError("'%s' is neither a filesystem directory nor a DICOMDIR" % directory)
    if isfile(dicomdir):
        try:
            dobjs = get_dicom_objects_with_dicomdir(dicomdir, patid, stuid, sernos)
        except (OSError, IOError, InvalidDicomError):
            dobjs = get_dicom_objects_from_directory_tree(basedir, globpattern, patid, stuid, sernos)
    else:
        dobjs = get_dicom_objects_from_directory_tree(basedir, globpattern, patid, stuid, sernos)

    # Restrict by date if not unique.
    dobjs = _filter_dobjs_by_date(dobjs, studydate=studydate)

    # Optionally reject non-image objects such as Philips PresentationState objects
    if imagesonly:
        dobjs = [dobj for dobj in dobjs if 'PixelData' in dobj]

    # Remove any duplicates based on SOP Instance UID
    dobjs = {dobj.SOPInstanceUID: dobj for dobj in dobjs}.values()

    # Sort by series and instance numbers
    return sorted(
        dobjs, key=lambda d: (int(d.SeriesNumber), int(d.InstanceNumber))
    )


def has_private_section(dobj, section):
    """
    Whether object has specified private tag section.

    Parameters
    ----------
    dobj : dicom object
            object in which to look for private tag section
    section: str
            name of private creator
    Returns
    -------
    bool

    """
    return next(
        # work around for non dictionary-like behaviour of dicom obj
        (k for k in dobj.keys() if dobj[k].name == 'Private Creator' and dobj[k].value == section),
        None
    ) is not None


def has_csa(dobj):
    """
    Whether object has a siemens csa private tag section.

    Parameters
    ----------s
    dobj : dicom object
            object in which to look for csa

    Returns
    -------
    bool

    """
    return has_private_section(dobj, 'SIEMENS CSA HEADER')


def has_sds(dobj):
    """
    Whether object has a siemens xa11 series private tag section.

    Detects sdi both in Enhanced and Interoperability modes.

    Parameters
    ----------
    dobj : dicom object
            object in which to look for sds

    Returns
    -------
    bool

    """
    if has_private_section(dobj, 'SIEMENS MR SDS 01'):
        return True
    if 'SharedFunctionalGroupsSequence' in dobj:
        return has_private_section(
            dobj.SharedFunctionalGroupsSequence[0], 'SIEMENS MR SDS 01'
        )
    return False


def has_sdi(dobj):
    """
    Whether object has a siemens xa11 image private tag section.

    Detects sdi both in Enhanced and Interoperability modes.

    Parameters
    ----------
    dobj : dicom object
            object in which to look for sdi

    Returns
    -------
    bool

    """
    if has_private_section(dobj, 'SIEMENS MR SDI 02'):
        return True
    if 'PerFrameFunctionalGroupsSequence' in dobj:
        return has_private_section(
            dobj.PerFrameFunctionalGroupsSequence[0], 'SIEMENS MR SDI 02'
        )
    return False


def _lookup_private(private_creator, tag_name):
    try:
        # last two digit characters are the (hex) offset
        return int(
            next(k for k, v in private_dictionaries[private_creator].items() if v[2] == tag_name)[-2:],
            16
        )
    except StopIteration:
        raise KeyError(f"Private Tag {tag_name} not found in private dictionary {private_creator}")


def _private_tag(dobj, section, name_or_offset):
    """
    Get tag from specified private section.

    Parameters
    ----------
    dobj : dicom object
            object in which to look for private tag section
    section: str
            name of private creator
    name_or_offset: str | int
            name of tag or offset for tag from 0 to 0xff
    Returns
    -------
    dicom tag or None

    """
    try:
        priv_creator = next(
            # work around for non dictionary-like behaviour of dicom obj
            key for key in dobj.keys()
            if dobj[key].name == 'Private Creator' and dobj[key].value == section
        )
    except StopIteration:
        raise KeyError(f'Private group for {section} not found in dicom object')

    offset = _lookup_private(section, name_or_offset) if isinstance(name_or_offset, str) else name_or_offset
    group, element_base = priv_creator.group, 256 * priv_creator.element
    return dobj[group, element_base + offset]


def get_sds_tag(dobj, name_or_offset):
    """
    Get tag from Siemens sds private section.

    Parameters
    ----------
    dobj : dicom object
            object in which to look for private tag section
    name_or_offset: str | int
            name or offset for tag from 0 to 0xff
    Returns
    -------
    dicom tag value

    """
    if has_sds(dobj):
        if 'SharedFunctionalGroupsSequence' in dobj:
            sfgs = dobj.SharedFunctionalGroupsSequence[0]
            privseq = _private_tag(sfgs, 'SIEMENS MR SDS 01', 0xfe)
            return _private_tag(privseq[0], 'SIEMENS MR SDS 01', name_or_offset).value

        return _private_tag(dobj, 'SIEMENS MR SDS 01', name_or_offset).value

    raise KeyError("Siemens SDS Section not found in object")


def has_sds_tag(dobj, name_or_offset):
    """
    Check whether tag from Siemens sds private section is present.

    Parameters
    ----------
    dobj : dicom object
            object in which to look for private tag section
    name_or_offset: str | int
            name or offset for tag from 0 to 0xff
    Returns
    -------
    True iff present

    """
    try:
        get_sds_tag(dobj, name_or_offset)
        return True
    except KeyError:
        return False


def get_sdi_tag(dobj, name_or_offset):
    """
    Get tag from Siemens sdi private section.

    Parameters
    ----------
    dobj : dicom object
            object in which to look for private tag section
    name_or_offset: str | int
            name or offset for tag from 0 to 0xff
    Returns
    -------
    dicom tag value

    """
    if has_sdi(dobj):
        if 'PerFrameFunctionalGroupsSequence' in dobj:
            sfgs = dobj.PerFrameFunctionalGroupsSequence[0]
            privseq = _private_tag(sfgs, 'SIEMENS MR SDI 02', 0xfe)
            return _private_tag(privseq[0], 'SIEMENS MR SDI 02', name_or_offset).value

        return _private_tag(dobj, 'SIEMENS MR SDI 02', name_or_offset).value

    raise KeyError("Siemens SDI Section not found in object")


def has_sdi_tag(dobj, name_or_offset):
    """
    Check whether tag from Siemens sdi private section is present.

    Parameters
    ----------
    dobj : dicom object
            object in which to look for private tag section
    name_or_offset: str | int
            name or offset for tag from 0 to 0xff
    Returns
    -------
    True iff present

    """
    try:
        get_sdi_tag(dobj, name_or_offset)
        return True
    except KeyError:
        return False


#
# Generalised routines for getting useful fields irrespective of vendor
# and whether the SOP class is the standard MR one or the newer enhanced MR
#


def scanner_operator(dobj, default=''):
    """
    Operator as entered on the scanner.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from
    default: str
            value to return if empty

    Returns
    -------
    str : MR Scanner Operator

    """
    pname = getattr(dobj, 'OperatorsName', '')

    # PatientName3 or PatientName instead of str in later pydicm versions
    try:
        components = pname.components
    except AttributeError:
        components = pname.split('^')

    try:
        # first non-empty element of dicom PN
        name = next(c for c in components if c).strip()
        return name if name else default
    except StopIteration:
        return default


def qa_date(dobj):
    """
    Date of QA scan (normally acquisition date).

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    str : date of scan in DICOM (ISO-8601) form


    """
    if 'AcquisitionDate' in dobj and dobj.AcquisitionDate:
        return dobj.AcquisitionDate
    if 'AcquisitionDateTime' in dobj and dobj.AcquisitionDateTime:
        return dobj.AcquisitionDateTime[:8]
    if 'ContentDate' in dobj and dobj.ContentDate:
        return dobj.ContentDate
    if 'SeriesDate' in dobj and dobj.SeriesDate:
        return dobj.SeriesDate
    return getattr('StudyDate', '')


def manufacturer(dobj):
    """
    Code string for manufacturer.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    str : code string for Manufacturer

    """
    man = dobj.Manufacturer.strip().lower()
    if man.startswith('siemens'):
        return 'Siemens'
    if man.startswith('philips'):
        return 'Philips'
    if man.startswith('ge'):
        return 'GE'

    return man.split()[0].capitalize()


def series_number(dobj):
    """
    Series number.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    int : Series number

    """
    return int(dobj.SeriesNumber)


def instance_number(dobj):
    """
    Instance number.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    int : Instance number

    """
    return int(dobj.InstanceNumber)


def acquisition_number(dobj):
    """
    Acquisition number.

    Likely not be defined for multiframes

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    int : Acquisition number

    """
    return int(getattr(dobj, 'AcquisitionNumber', 1))


def software_versions(dobj):
    """
    Software versions.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    str : versions

    """
    version = getattr(dobj, 'SoftwareVersions', '')
    return version if isinstance(version, str) else ':'.join(version)


def seq_name(dobj):
    """
    Representative sequence name.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    str : sequence name

    """
    # GE private sequence name tags
    if manufacturer(dobj) == 'GE':
        for tag in [(0x0019, 0x109C), (0x0019, 0x109E)]:
            if tag in dobj and dobj[tag].value != '':
                return dobj[tag].value

    # Standard tags
    for tag in ['PulseSequenceName', 'SequenceName', 'ScanningSequence']:
        if tag in dobj and getattr(dobj, tag) != '':
            return getattr(dobj, tag)

    # Siemens private sequence name in csa
    if manufacturer(dobj) == 'Siemens' and 'SequenceName' in csa(dobj, 'image'):
        return csa(dobj, 'image')['SequenceName']

    return 'UnknownSequence'


def protocol_name(dobj):
    """
    Representative protocol name.

    Protocol name either from standard tag or from series description.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    str : protocol name

    """
    protocol = (
        dobj.ProtocolName if 'ProtocolName' in dobj else
        dobj.SeriesDescription if 'SeriesDescription' in dobj else
        'UnknownProtocol'
    )
    return protocol.strip()


def rx_coil_name(dobj):
    """
    Receive Coil.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    str: name of coil

    """
    if manufacturer(dobj) == 'GE':
        # Private Tag
        for tag in [(0x0043, 0x1081)]:
            if tag in dobj and dobj[tag].value != '':
                return dobj[tag].value
    elif manufacturer(dobj) == 'Siemens':
        try:
            # Enhanced MR
            for seqobja in dobj.SharedFunctionalGroupsSequence:
                for seqobjb in seqobja.MRReceiveCoilSequence:
                    return seqobjb.ReceiveCoilName
        except AttributeError:
            pass

        # Private Tag
        for tag in [(0x0051, 0x100f)]:
            if tag in dobj and dobj[tag].value != '':
                return dobj[tag].value

        if has_csa(dobj):
            if 'ImaCoilString' in csa(dobj, 'image'):
                return csa(dobj, 'image')['ImaCoilString']
            if 'CoilString' in csa(dobj, 'series'):
                return csa(dobj, 'series')['CoilString']

    elif manufacturer(dobj) == 'Philips':
        # Enhanced MR
        try:
            for seqobja in dobj.SharedFunctionalGroupsSequence:
                for seqobjb in seqobja.MRReceiveCoilSequence:
                    if 'ReceiveCoilName' in seqobjb:
                        return seqobjb.ReceiveCoilName
        except AttributeError:
            pass
        try:
            for seqobja in dobj.PerFrameFunctionalGroupsSequence:
                for seqobjb in seqobja.MRReceiveCoilSequence:
                    if 'ReceiveCoilName' in seqobjb:
                        return seqobjb.ReceiveCoilName
        except AttributeError:
            pass

    # Standard Locations
    for tag in ['ReceiveCoilName']:
        if tag in dobj and getattr(dobj, tag) != '':
            return getattr(dobj, tag)

    return 'UnknownCoil'


def t_r(dobj):
    """
    Repetition Time.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    float : repetition time in millseconds

    """
    if 'RepetitionTime' in dobj:
        return float(dobj.RepetitionTime)

    if 'SharedFunctionalGroupsSequence' in dobj:
        return float(
            dobj.SharedFunctionalGroupsSequence[0].MRTimingAndRelatedParametersSequence[0].RepetitionTime
        )

    if manufacturer(dobj) == 'Siemens' and has_csa(dobj) and 'RepetitionTime' in csa(dobj, 'image'):
        return float(csa(dobj, 'image')['RepetitionTime'])

    raise KeyError('Repetition time not available in dicom object')


def t_e(dobj):
    """
    Echo Time.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    float : echo time in millseconds

    """
    if 'EchoTime' in dobj:
        return float(dobj.EchoTime)

    if 'PerFrameFunctionalGroupsSequence' in dobj and 'MREchoSequence' in dobj.PerFrameFunctionalGroupsSequence[0]:
        mre = dobj.PerFrameFunctionalGroupsSequence[0].MREchoSequence[0]
        return float(mre.EffectiveEchoTime)

    if 'SharedFunctionalGroupsSequence' in dobj and 'MREchoSequence' in dobj.SharedFunctionalGroupsSequence[0]:
        mre = dobj.SharedFunctionalGroupsSequence[0].MREchoSequence[0]
        return float(mre.EffectiveEchoTime)

    if manufacturer(dobj) == 'Siemens' and has_csa(dobj) and 'EchoTime' in csa(dobj, 'image'):
        return float(csa(dobj, 'image')['EchoTime'])

    raise KeyError('Echo time not available in dicom object')


def flip_angle(dobj):
    """
    Flip Angle.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    float : flip angle in degrees

    """
    if 'FlipAngle' in dobj:
        return float(dobj.FlipAngle)
    if 'PerFrameFunctionalGroupsSequence' in dobj:
        return float(dobj.SharedFunctionalGroupsSequence[0].MRTimingAndRelatedParametersSequence[0].FlipAngle)

    raise KeyError('Flip angle not available in dicom object')


def pix_spacing_yx(dobj):
    """
    Pixel spacing in mm vertical first.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    tuple of floats: (y spacing, x spacing)

    """
    if 'PixelSpacing' in dobj:
        return tuple(map(float, dobj.PixelSpacing))
    try:
        return tuple(
            map(float, dobj.PerFrameFunctionalGroupsSequence[0].PixelMeasuresSequence[0].PixelSpacing)
        )
    except (AttributeError, IndexError):
        pass

    raise KeyError('Pixel spacing not available in dicom object')


def matrix_yx(dobj):
    """
    Pixel matrix shape.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    tuple of ints: (rows, columns)

    """
    if 'Rows' in dobj and 'Columns' in dobj:
        return (int(dobj.Rows), int(dobj.Columns))

    raise KeyError('Matrix dimensions not available in dicom object')


def phase_enc_dirn(dobj):
    """
    Phase encoding direction - row or column.

    Parameters
    ----------
    dobj : dicom object
               object to extract field from

    Returns
    -------
    str : "ROW" or "COL"

    """
    if 'InPlanePhaseEncodingDirection' in dobj:
        return dobj.InPlanePhaseEncodingDirection
    # Usually shared
    try:
        # nb: enhanced mr has 'COLUMN' as opposed to 'COL' so just use first 3 chars
        return dobj.SharedFunctionalGroupsSequence[0].MRFOVGeometrySequence[0].InPlanePhaseEncodingDirection[:3]
    except (AttributeError, IndexError):
        pass
    # But sometimes perframe eg for scouts - just take the first one
    try:
        return dobj.PerFrameFunctionalGroupsSequence[0].MRFOVGeometrySequence[0].InPlanePhaseEncodingDirection[:3]
    except (AttributeError, IndexError):
        pass

    raise KeyError('Phase encoding direction not available in dicom object')


def slice_thickness(dobj):
    """
    Slice thickness in mm.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    float : slice thickness in mm

    """
    if 'SliceThickness' in dobj:
        return float(dobj.SliceThickness)
    try:
        return float(dobj.PerFrameFunctionalGroupsSequence[0].PixelMeasuresSequence[0].SliceThickness)
    except (AttributeError, IndexError):
        pass

    raise KeyError('Slice Thickness not available in dicom object')


def slice_location(dobj, frame=0):
    """
    Slice location in mm

    Parameters
    ----------
    dobj : dicom object
            object to extract field from
    frame: index (base 0) of frame to use if a multiframe (or 'all')

    Returns
    -------
    float:
        position of slice in mm from isocentre (or list of positions for multiframe)
    """
    def _loc_of_frame(dobj, frame):
        if not 0 <= frame < len(dobj.PerFrameFunctionalGroupsSequence):
            raise IndexError(
                f'slice_location: nonexistent frame {frame}'
            )
        pffg = dobj.PerFrameFunctionalGroupsSequence[frame]
        pmeasures = pffg.PixelMeasuresSequence[0]
        porient = pffg.PlaneOrientationSequence[0]
        pposn = pffg.PlanePositionSequence[0]
        if 'SliceLocation' in pmeasures:
            return float(pmeasures.SliceLocation)
        elif 'ImageOrientationPatient' in porient and 'ImagePositionPatient' in pposn:
            orient = np.array([float(f) for f in porient.ImageOrientationPatient])
            row, col = orient[:3], orient[3:]
            normal = np.cross(row, col)
            position = np.array([float(f) for f in pposn.ImagePositionPatient])
            ny, nx = matrix_yx(dobj)
            dy, dx = pix_spacing_yx(dobj)
            centre = position + row * dx * nx / 2 + col * dy * ny / 2
            return np.dot(centre, normal)
        else:
            raise KeyError(
                f'slice_location: no slice position information for frame {frame}'
            )

    if is_enhancedmr(dobj):
        if frame != 'all':
            return _loc_of_frame(dobj, frame=frame)
        else:
            return [
                _loc_of_frame(dobj, i)
                for i in range(len(dobj.PerFrameFunctionalGroupsSequence))
            ]
    elif 'SliceLocation' in dobj:
        locn = float(dobj.SliceLocation)
        if frame == 0:
            return locn
        elif frame == 'all':
            return [locn]
        else:
            raise IndexError(
                f'slice_location: frame {frame} specified for single frame object'
            )
    elif 'ImageOrientationPatient' in dobj and 'ImagePositionPatient' in dobj:
        # Derive from slice geometry tags
        orient = np.array(image_orientation_pat(dobj))
        row, col = orient[:3], orient[3:]
        normal = np.cross(row, col)

        position = np.array(image_position_pat(dobj))
        dy, dx = pix_spacing_yx(dobj)
        ny, nx = matrix_yx(dobj)

        centre = position + row * dx * nx / 2 + col * dy * ny / 2
        locn = np.dot(centre, normal)
        if frame == 0:
            return locn
        elif frame == 'all':
            return [locn]
        else:
            raise IndexError(
                f'slice_location: frame {frame} specified for single frame object'
            )
    else:
        raise KeyError(
            'slice_location: no slice position information found'
        )


def number_of_averages(dobj):
    """
    Number of Signal Averages.

    This is the number of averages of each line of k space.
    It is called NSA by Siemens and NEX by GE.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    int: signal averages.

    """
    #  OK in Siemens and GE, buried in Philips and EnhancedMR
    if 'NumberOfAverages' in dobj:
        return int(dobj.NumberOfAverages)
    if 'SharedFunctionalGroupsSequence' in dobj and 'MRAveragesSequence' in dobj.SharedFunctionalGroupsSequence[0]:
        return int(dobj.SharedFunctionalGroupsSequence[0].MRAveragesSequence[0].NumberOfAverages)
    if 'PerFrameFunctionalGroupsSequence' in dobj and 'MRAveragesSequence' in dobj.PerFrameFunctionalGroupsSequence[0]:
        return int(dobj.PerFrameFunctionalGroupsSequence[0].MRAveragesSequence[0].NumberOfAverages)
    if has_csa(dobj) and 'NumberOfAverages' in csa(dobj, 'image'):
        return int(csa(dobj, 'image')['NumberOfAverages'])
    if manufacturer(dobj) == 'Philips' and (0x2001, 0x1088) in dobj:
        return int(dobj[0x2001, 0x1088].value)
    raise KeyError('Number of Signal Averages not available')


def number_of_phase_encoding_steps(dobj):
    """
    Number of Phase Encoding Lines.

    This is the number of lines of k space acquired.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    int: k space lines.

    """
    # OK in Siemens and Philips, missing in GE
    if 'NumberOfPhaseEncodingSteps' in dobj:
        return int(dobj.NumberOfPhaseEncodingSteps)
    if 'SharedFunctionalGroupsSequence' in dobj and 'MRFOVGeometrySequence' in dobj.SharedFunctionalGroupsSequence[0]:
        return int(
            dobj.SharedFunctionalGroupsSequence[0].MRFOVGeometrySequence[0].MRAcquisitionPhaseEncodingStepsInPlane
        )

    # Fall back to using acquisition matrix
    if 'AcquisitionMatrix' in dobj:
        _, _, row_len, col_len = map(int, dobj.AcquisitionMatrix)
        pe_dirn = dobj.InPlanePhaseEncodingDirection
        return row_len if pe_dirn == 'ROW' else col_len

    raise KeyError('Number of Phase Encoding steps not available')


def number_of_frames(dobj):
    """
    Number of frames in a multiframe.

    For single frame object this will return one.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    int : number of frames

    """
    return int(getattr(dobj, 'NumberOfFrames', 1))


def is_multiframe(dobj):
    """
    Whether dicom object is multiframe.

    Parameters
    ----------
    dobj : dicom object

    Returns
    -------
    bool

    """
    return number_of_frames(dobj) > 1


def is_enhancedmr(dobj):
    """
    Whether dicom object has enhanced mr sop class.

    NB will be False even for up to date MRSpectroscopy

    Parameters
    ----------
    dobj : dicom object

    Returns
    -------
    bool

    """
    return dobj.SOPClassUID == EnhancedMRImageStorage


def image_orientation_pat(dobj):
    """
    Image orientation in DICOM patient coordinate system.

    This is represented as six direction cosines.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    tuple of 6 floats: 3 row cosines and 3 column cosines

    """
    if 'ImageOrientationPatient' in dobj:
        tagval = dobj.ImageOrientationPatient
    elif 'PerFrameFunctionalGroupsSequence' in dobj:
        pffg = dobj.PerFrameFunctionalGroupsSequence[0]
        tagval = pffg.PlaneOrientationSequence[0].ImageOrientationPatient
    else:
        raise KeyError('Image orientation not available in dicom object')
    return tuple(map(float, tagval))


def image_position_pat(dobj):
    """
    Image Position in DICOM patient coordinate system.


    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    tuple of 3 floats

    """
    if 'ImagePositionPatient' in dobj:
        tagval = dobj.ImagePositionPatient
    elif 'PerFrameFunctionalGroupsSequence' in dobj:
        pffg = dobj.PerFrameFunctionalGroupsSequence[0]
        tagval = pffg.PlanePositionSequence[0].ImagePositionPatient
    else:
        raise KeyError('Image position not available in dicom object')
    return tuple(map(float, tagval))


def approx_slice_orientation(dobj):
    """
    Best estimate of slice orientation (main axes only).

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    str: orientation "Sagittal", "Coronal" or "Axial"

    """
    orient = image_orientation_pat(dobj)
    # Choose axis based on the largest component of the normal to the imaging plane
    row, col = orient[:3], orient[3:]
    perp = np.cross(row, col)
    axis = np.argmax(np.abs(perp))
    return ['Sagittal', 'Coronal', 'Axial'][axis]


def approx_phase_orientation(dobj):
    """
    Best estimate of phase encoding direction (main axes only).

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    str: orientation "RL", "AP" etc.

    """
    penc_dirn = phase_enc_dirn(dobj)
    orient = image_orientation_pat(dobj)
    row, col = orient[:3], orient[3:]
    dirn = row if penc_dirn == 'ROW' else col
    axis = np.argmax(np.abs(dirn))
    return (['RL', 'AP', 'FH'] if dirn[axis] > 0 else ['LR', 'PA', 'HF'])[axis]


def readout_bandwidth(dobj):
    """
    Per-Pixel Readout bandwidth.

    This is the reciprocal of the readout window length, in Hertz per pixel.

    Parameters
    ----------
    dobj : dicom object
        object to extract field from

    Returns
    -------
    float: bandwidth in Hz/pixel

    """
    if 'PixelBandwidth' in dobj:
        return float(dobj.PixelBandwidth)
    if ('SharedFunctionalGroupsSequence' in dobj and
          'MRImagingModifierSequence' in dobj.SharedFunctionalGroupsSequence[0] and
          'PixelBandwidth' in dobj.SharedFunctionalGroupsSequence[0].MRImagingModifierSequence[0]):
        return float(dobj.SharedFunctionalGroupsSequence[0].MRImagingModifierSequence[0].PixelBandwidth)

    raise KeyError('Readout bandwidth not available in dicom object')


def epi_phase_encode_bandwidth(dobj):
    """
    Per-Pixel bandwidth in the EPI phase encode direction.

    This is the reciprocal of the EPI readout window length, in Hz per pixel.

    Parameters
    ----------
    dobj : dicom object
        object to extract field from

    Returns
    -------
    float: bandwidth in Hz/pixel

    """
    # TODO: error nicely if tags missing - should maybe return Inf rather than zero
    # TODO: use private groups properly
    # TODO: implementations for Philips and GE
    _PerPixelBandwidthPhaseEncodeVE11 = (0x0019, 0x1028)
    _SDSSequence = (0x0021, 0x11fe)
    _PerPixelBandwidthPhaseEncodeXA11 = (0x0021, 0x1153)
    if manufacturer(dobj) == 'Siemens':
        if is_enhancedmr(dobj):
            pffg0 = dobj.PerFrameFunctionalGroupsSequence[0]
            sdi0 = pffg0[_SDSSequence][0]
            bw = float(
                sdi0[_PerPixelBandwidthPhaseEncodeXA11].value if _PerPixelBandwidthPhaseEncodeXA11 in sdi0 else 0
            )
        else:
            bw = float(
                dobj[_PerPixelBandwidthPhaseEncodeVE11].value if _PerPixelBandwidthPhaseEncodeVE11 in dobj else 0
            )
        return bw

    # TODO: we might be able to get this from other tags
    raise KeyError('Bandwidth per pixel phase encode only defined for Siemens currently')


def larmor_frequency(dobj):
    """Resonant frequency in MHz.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    float: resonant frequency in MHz

    """
    if manufacturer == 'Philips':
        try:
            block = dobj.private_block(0x2001, 'Philips Imaging DD 001')
            return float((block[0x83].value))
        except KeyError:
            pass

    if 'ImagingFrequency' in dobj:
        return float(dobj.ImagingFrequency)

    if 'TransmitterFrequency' in dobj:
        return float(dobj.TransmitterFrequency)

    if ( 'SharedFunctionalGroupsSequence' in dobj and
         'MRImagingModifierSequence' in dobj.SharedFunctionalGroupsSequence[0] and
         'TransmitterFrequency' in dobj.SharedFunctionalGroupsSequence[0].MRImagingModifierSequence[0]):
        return float(dobj.SharedFunctionalGroupsSequence[0].MRImagingModifierSequence[0].TransmitterFrequency)

    if manufacturer(dobj) == 'Siemens' and has_csa(dobj) and 'ImagingFrequency' in csa(dobj, 'image'):
        return float(csa(dobj, 'image')['ImagingFrequency'])

    raise KeyError('Larmor frequency not available in dicom object')


def readout_sensitivity(dobj):
    """
    Distortion sensitivity of readout to off-resonance in mm/ppm.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    float: readout sensitivity in mm/ppm

    """
    readout_spacing = pix_spacing_yx(dobj)[0] if phase_enc_dirn(dobj) == 'COL' else pix_spacing_yx(dobj)[1]
    return readout_spacing * larmor_frequency(dobj) / readout_bandwidth(dobj)


def coil_elements(dobj):
    """
    Coil elements used in image.

    This will typically be all the elements but, for instance, in the case of
    separate coil element images there will be a single index.

    Currently supported for Siemens only.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    list of indices: indices of coil elements used

    """
    if manufacturer(dobj) == 'Siemens':
        if has_csa(dobj):
            csatags = csa(dobj, 'image')
            if 'UsedChannelString' in csatags:
                # VD13/VE11 - a string with an 'X' where element used and '-' where not
                channels = csatags['UsedChannelString']
                return [i for i, c in enumerate(channels) if c == 'X']
            if 'UsedChannelMask' in csatags:
                # VB17 - a binary mask of elements, one where used and zero where not
                mask = csatags['UsedChannelMask']
                return [i for i, bit in enumerate(bin(mask)[:1:-1]) if bit == '1']
            raise KeyError('Coil Element Indices not available in Siemens CSA')
        if has_sdi(dobj):
            channels = get_sdi_tag(dobj, 'UsedChannelString')
            return [i for i, c in enumerate(channels) if c == 'X']

    elif manufacturer(dobj) == 'Philips' and not is_multiframe(dobj):
        # Chemical Shift Number MR
        # TODO: should respect Private Creator (2001, 0010) 'Philips Imaging DD 001'
        return [int(dobj[(0x2001, 0x1002)].value)]

    raise KeyError('Coil Element not implemented yet for GE or Philips Enhanced')


def recon_scale_factor(dobj):
    """
    Overall scale factor used in reconstruction.

    This will normally be unity but can be set in the UI and for
    noise images it would tyically be set higher.

    A factor of about 40 is adequate for the noise only images on
    the Skyra 32 channel head coil but with the signal image care
    needs to be taken not to overflow in the foreground regions so
    it is safest left at unity.

    Doesn't seem to be defined in VB17 so returns unity if not available.

    Currently supported for Siemens VD/VE/XA only.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    float: factor image has been scaled by.

    """
    if manufacturer(dobj) == 'Siemens':
        tags = phoenix(dobj)
        if 'sCoilSelectMeas.dOverallImageScaleCorrectionFactor' in tags:
            return float(tags['sCoilSelectMeas.dOverallImageScaleCorrectionFactor'])
        return 1.0

    raise KeyError('Recon scale factor not implemented yet for Philips/GE')


# RHD: TODO implement for Philips, GE
def rx_coil_id(dobj):
    """
    Best guess identifier for entire receive coil

    This should return Head_32 etc rather than the element names.
    It relies on searching through the phoenix protocol.
    In case of more than one choose the most common
    TODO: use structured phoenix protocol when available in dcmextras

    Currently supported for Siemens only.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    string: identifier string for coil.

    """
    if manufacturer(dobj) == 'Siemens':
        # VD/VE/XA
        pattern = r'sCoilSelectMeas\.aRxCoilSelectData\[\d\]\.asList\[\d{1,2}\]\.sCoilElementID\.tCoilID'
        cids = [v for k, v in phoenix(dobj).items() if re.match(pattern, k)]
        if cids:
            return max(set(cids), key=cids.count)
        # VB
        pattern = r'sCoilSelectUI\.asList\[\d{1,2}\]\.sCoilElementID\.tCoilID'
        cids = [v for k, v in phoenix(dobj).items() if re.match(pattern, k)]
        return max(set(cids), key=cids.count) if cids else ''
    raise KeyError('Not implemented yet for Philips/GE')


# TODO (RHD): Implement for GE
def is_distortion_corrected(dobj):
    """
    Whether image has had distortion correction applied.

    Currently supported for Siemens and Philips only.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    True iff (2D or 3D) distortion correction applied

    """
    if manufacturer(dobj) == 'Siemens':
        if has_sdi_tag(dobj, 'DistortionCorrectionType'):
            corrn_type = get_sdi_tag(dobj, 'DistortionCorrectionType')
            if corrn_type in {'DIS2D', 'DIS3D'}:
                return True
            if corrn_type == 'ND':
                return False
        image_types = set(dobj.ImageType)
        if has_sdi_tag(dobj, 'ImageType4MF'):
            image_types |= set(get_sdi_tag(dobj, 'ImageType4MF'))
        return 'DIS2D' in image_types or 'DIS3D' in image_types

    if manufacturer(dobj) == 'Philips':
        try:
            block = dobj.private_block(0x2005, 'Philips MR Imaging DD 001')
            return block[0xa9].value != 'NONE'
        except KeyError:
            pass
    raise KeyError('Distortion correction status not implemented/available')


# TODO (RHD): Implement for Philips, GE
# TODO (RHD): This is maybe getting hidden on XA30 MFSPLIT
# TODO (RHD): We have phoenix 'PreScanNormalizeFilter': {'Mode': 2}
# TODO (RHD): but not clear what it means
def is_uniformity_corrected(dobj):
    """
    Whether image has had uniformity correction applied.

    Currently supported for Siemens only.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    True iff uniformity correction applied

    """
    if manufacturer(dobj) == 'Siemens':
        image_types = set(dobj.ImageType)
        if has_sdi_tag(dobj, 'ImageType4MF'):
            image_types |= set(get_sdi_tag(dobj, 'ImageType4MF'))
        return 'NORM' in image_types
    raise KeyError('Not implemented yet for Philips/GE')


# TODO (RHD): Implement for Philips and GE
def flow_venc(dobj):
    """
    Velocity Encoding of PC flow sequence.

    Currently supported for Siemens only.

    Parameters
    ----------
    dobj : dicom object
            object to extract field frrom

    Returns
    -------
    float:
        value in cm/sec

    """
    if is_enhancedmr(dobj):
        pffg = dobj.PerFrameFunctionalGroupsSequence[0]
        if 'MRVelocityEncodingSequence' in pffg:
            mrve = pffg.MRVelocityEncodingSequence[0]
            venc_lower = float(mrve.VelocityEncodingMinimumValue)
            venc_upper = float(mrve.VelocityEncodingMaximumValue)
            if venc_upper != -venc_lower:
                raise ValueError('Asymmetric venc')
            return venc_upper
        return 0

    if manufacturer(dobj) == 'Siemens':
        if has_csa(dobj):
            venc = csa(dobj, 'image').get('FlowVenc', 0)
            return float(venc) if venc else 0
        if has_sdi_tag(dobj, 'FlowEncodingDirection'):
            flowencoding = get_sdi_tag(dobj, 'FlowEncodingDirection')
            # Format is v<venc>_<direction>
            if flowencoding and flowencoding[0] == 'v' and '_' in flowencoding:
                venc = flowencoding.split('_')[0][1:]
                return float(venc) if venc.isdigit() else 0
            else:
                return 0
        if has_sds_tag(dobj, 'MRPhoenixProtocol'):
            try:
                return float(phoenix(dobj, raw=False)['Angio']['FlowArray']['Elm'][0]['Velocity'])
            except (KeyError, ValueError):
                return 0
        return 0

    raise KeyError('Only implemented for Siemens and generic Enhanced MR')


def diffusion_bvalue(dobj, frame=0):
    """
    Diffusion Encoding B Value in sec/mm^2

    Parameters
    ----------
    dobj : dicom object
            object to extract field from
    frame: index of frame to use (base 0) if a multiframe (or 'all')

    Returns
    -------
    float:
        value in sec/mm^2

    """
    if is_enhancedmr(dobj):
        sfg = dobj.SharedFunctionalGroupsSequence[0]
        if 'MRDiffusionSequence' in sfg:
            mrd = sfg.MRDiffusionSequence[0]
            return float(mrd.DiffusionBValue)
        pffgs = dobj.PerFrameFunctionalGroupsSequence
        if any('MRDiffusionSequence' in pffg for pffg in pffgs):
            # This will be a list organised in the same way as the multiframe
            bvalues = []
            for pffg in pffgs:
                if 'MRDiffusionSequence' in pffg:
                    mrd = pffg.MRDiffusionSequence[0]
                if 'DiffusionBValue' in mrd:
                    bvalues.append(float(mrd.DiffusionBValue))
                else:
                    bvalues.append(float('nan'))
            if all(isnan(bvalue) for bvalue in bvalues):
                raise KeyError(f'Diffusion b-value not found in {manufacturer(dobj)} scan')
            bvalues = [0 if isnan(bvalue) else bvalue for bvalue in bvalues]
            return bvalues if frame == 'all' else bvalues[frame]
    elif 'DiffusionBValue' in dobj:
        # Not official in single frames but GE seems to use it
        return float(dobj.DiffusionBValue)
    elif manufacturer(dobj) == 'Siemens':
        if has_csa(dobj):
            bvalue = float(csa(dobj, 'image')['B_value'])
            return bvalue if frame != 'all' else [bvalue]
        elif has_sdi(dobj):
            bvalue = float(get_sdi_tag(dobj, 'BValue'))
            return bvalue if frame != 'all' else [bvalue]
    elif manufacturer(dobj) == 'GE':
        # Try here if not in DiffusionBValue
        _SlopInteger6ToSlopInteger9 = (0x0043, 0x1039)
        if _SlopInteger6ToSlopInteger9 in dobj:
            # Pretty weird: have to mask off upper part in decimal
            bvalue = float(
                int(dobj[_SlopInteger6ToSlopInteger9][0]) % 100_000
            )
            return bvalue if frame != 'all' else [bvalue]
    elif manufacturer(dobj) == 'Philips':
        # no private single frame handling for philips for now - need examples
        pass

    raise KeyError(f'Diffusion b-value not found in {manufacturer(dobj)} scan')


# RHD: TODO implement for Philips, GE
def trigger_time(dobj):
    """
    Trigger Time of PC flow sequence.

    The time from the R wave the image is nominally acquired at.
    Currently supported for Siemens only.

    If not available then returns 0

    For an enhancedmr multiframe returns a list

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    float | list:
        time(s) in milliseconds

    """
    if manufacturer(dobj) == 'Siemens':
        if is_enhancedmr(dobj):
            pffgs = dobj.PerFrameFunctionalGroupsSequence
            if all('CardiacSynchronizationSequence' in pffg for pffg in pffgs):
                css = [pffg.CardiacSynchronizationSequence[0] for pffg in pffgs]
                return [float(cs.NominalCardiacTriggerDelayTime) for cs in css]
            return [0] * len(pffgs)

        return float(dobj.TriggerTime) if 'TriggerTime' in dobj else 0

    raise KeyError('Not implemented yet for Philips/GE')


def rescale_slope_and_intercept(dobj):
    """
    Recale Slope and Intercept for calibration of images

    Parameters
    ----------
    dobj : dicom object
            object to extract slope and intercept from

    Returns
    -------
    tuple:
        float values for slope and intecept

    """
    if 'RescaleSlope' in dobj and 'RescaleIntercept' in dobj:
        return float(dobj.RescaleSlope), float(dobj.RescaleIntercept)
    if 'PerFrameFunctionalGroupsSequence' in dobj:
        pffg = dobj.PerFrameFunctionalGroupsSequence[0]
        if 'PixelValueTransformationSequence' in pffg:
            pvt = pffg.PixelValueTransformationSequence[0]
            return float(pvt.RescaleSlope), float(pvt.RescaleIntercept)
    return 1.0, 0.0


# RHD: TODO implement for Philips and GE
def spectroscopy_data(dobj):
    """
    Complex 1D time domain signal from FID or SVS acquisition.

    Currently supported on Siemens SVS and FID only.

    Parameters
    ----------
    dobj : dicom object
            object to extract fid from

    Returns
    -------
    ndarray:
        1D array of complex time domain values

    """
    if manufacturer(dobj) == 'Siemens':
        _SpectroscopyData = 0x7fe1, 0x1010

        if _SpectroscopyData in dobj:
            # Pre-XA, data in Siemens CSA
            info = csa(dobj, 'image')
            if info['DataRepresentation'].upper() != 'COMPLEX':
                raise KeyError('Spectroscopy data not in complex form')
            if int(info['NumberOfFrames']) > 1:
                raise KeyError('Multiphase (CSI) spectroscopy data not supported')
            tagval = dobj[_SpectroscopyData].value
            # 32 bit floats, alternating re/imag (cf rda files uses doubles)
            x = np.array(struct.unpack('%df' % (len(tagval)//4), tagval))
            re, im = x[::2], x[1::2]
        elif 'SpectroscopyData' in dobj:
            # XA11- uses MR Spectroscopy SOP Class
            if dobj.DataRepresentation != 'COMPLEX':
                raise KeyError('Spectroscopy data not in complex form')
            if int(dobj.DataPointRows) != 1:
                raise KeyError('Multiphase (CSI) spectroscopy data not supported')
            tagval = dobj.SpectroscopyData
            # 32 bit floats, alternating re/imag as in old format
            x = np.array(struct.unpack('%df' % (len(tagval)//4), tagval))
            # but dicom standard has convention that fft will give +ve freq scale
            # fix to match old Siemens convention by taking complex conj
            re, im = x[::2], -x[1::2]
        else:
            raise KeyError('Spectroscopy data not available in dicom object')
    else:
        raise KeyError('Not implemented yet for Philips/GE')

    return re + 1j*im


# RHD: TODO implement for Philips, GE
def dwell_time(dobj):
    """Effective dwell time in ms.

    The "real" dwell time in Siemens spectroscopy acquisition.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    float: dwell time in ms

    """
    if manufacturer(dobj) == 'Siemens':
        if has_csa(dobj) and 'RealDwellTime' in csa(dobj, 'image'):
            # Siemens VB/VD/VE has value as ns
            return float(csa(dobj, 'image')['RealDwellTime']) * 1e-6
        if 'SpectralWidth' in dobj:
            # XA11 uses MR Spectroscopy SOP Class; spectral width in Hz
            return 1000 / float(dobj.SpectralWidth)

    raise KeyError('Dwell time not available in dicom object')


def gradient_sensitivities(dobj):
    """Calibration factors for gradient sensitivities (Field of View).

    The gradient scale factors used for the image scaling.

    Parameters
    ----------
    dobj : dicom object
            object to extract fields from

    Returns
    -------
    3-tuple of floats: gradient scale factors (x, y, z)

    """
    if manufacturer(dobj) == 'Siemens':
        tags = phoenix(dobj)
        return tuple(
            float(tags['sGRADSPEC.asGPAData[0].flSensitivity' + axis])
            for axis in 'XYZ'
        )
    raise KeyError('Gradient sensitivities not available in dicom object')


def transmitter_calibration(dobj):
    """RF transmitter adustment.

    RF Transmitter Calibration (volts).

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    float: transmitter calibration volts

    """
    if manufacturer(dobj) == 'Siemens':
        if has_csa(dobj) and 'TransmitterCalibration' in csa(dobj, 'series'):
            return float(csa(dobj, 'series')['TransmitterCalibration'])
        if has_sds(dobj):
            return float(get_sds_tag(dobj, 'TransmitterCalibration'))

    raise KeyError('Transmitter Calibration not available in dicom object')


def tales_reference_power(dobj):
    """TALES reference power.

    TALES reference power for SAR.

    Parameters
    ----------
    dobj : dicom object
            object to extract field from

    Returns
    -------
    float: tales reference power

    """
    if manufacturer(dobj) == 'Siemens':
        if has_csa(dobj) and 'TalesReferencePower' in csa(dobj, 'series'):
            return float(csa(dobj, 'series')['TalesReferencePower'])
        if has_sds(dobj):
            return float(get_sds_tag(dobj, 'TalesReferencePower'))

    raise KeyError('TALES reference power not available in dicom object')


def augment_private_dictionaries():
    """
    Incorporate additional entries for Philips and Siemens XA in global private tags dictionary
    NB: This is an (idempotent) side effect on the pydicom global private dictionary table
    """
    additional_private_dicts = {
        'SIEMENS MR SDS 01': {
            0x00211001: ('IS', '1', 'UsedPatientWeight', ''),
            0x00211002: ('DS', '3', 'SARWholeBody', ''),
            0x00211003: ('OB', '1', 'MRProtocol', ''),
            0x00211004: ('DS', '1', 'SliceArrayCatenations', ''),  # "1.0"
            0x00211005: ('IS', '3', 'RelTablePosition', ''),
            0x00211006: ('LO', '1', 'CoilForGradient', ''),  # "void"
            0x00211007: ('LO', '1', 'LongModelName', ''),  # "void"
            0x00211008: ('SH', '1', 'GradientMode', ''),
            0x00211009: ('LO', '1', 'PATModeText', ''),
            0x0021100A: ('DS', '1', 'SWCorrectionFactor', ''),  # "1.0"
            0x0021100B: ('DS', '1', 'RFPowerErrorIndication', ''),  # "1.0"
            0x0021100C: ('SH', '1', 'PositivePCSDirections', ''),  # "+LPH"
            0x0021100D: ('US', '1', 'ProtocolChangeHistory', ''),  # 0
            0x0021100E: ('LO', '1', 'DataFileName', ''),
            0x0021100F: ('DS', '3', 'Stimlim', ''),
            0x00211010: ('IS', '1', 'MrProtocolVersion', ''),  # "61120000" ??
            0x00211011: ('DS', '1', 'PhaseGradientAmplitude', ''),  # "0.0"
            0x00211012: ('FD', '1', 'ReadOutOS', ''),  # 2.0
            0x00211013: ('DS', '1', 'tpulsmax', ''),
            0x00211014: ('IS', '1', 'NumberOfPrescans', ''),  # "0"
            0x00211015: ('FL', '1', 'MeasurementIndex', ''),
            0x00211016: ('DS', '1', 'dBdtThreshold', ''),  # "0.0"
            0x00211017: ('DS', '1', 'SelectionGradientAmplitude', ''),  # "0.0"
            0x00211018: ('SH', '1', 'RFSWDMostCriticalAspect', ''),  # "Bore Local"
            0x00211019: ('OB', '1', 'MRPhoenixProtocol', ''),
            0x0021101A: ('LO', '1', 'CoilString', ''),
            0x0021101B: ('DS', '1', 'SliceResolution', ''),  # "0.0"
            0x0021101C: ('DS', '3', 'Stimmaxonline', ''),  # [2.79276, 8.55129, 10.8006]
            0x0021101D: ('IS', '1', 'OperationModeFlag', ''),  # "0"
            0x0021101E: ('FL', '16', 'AutoAlignMatrix', ''),
            0x0021101F: ('DS', '2', 'CoilTuningReflection', ''),
            0x00211020: ('UI', '1', 'RepresentativeImage', ''),
            0x00211022: ('SH', '1', 'SequenceFileOwner', ''),
            0x00211023: ('IS', '1', 'RFWatchdogMask', ''),  # "0"
            0x00211024: ('LO', '1', 'PostProcProtocol', ''),
            0x00211025: ('SL', '3', 'TablePositionOrigin', ''),  # [2.79276, 8.55129, 10.8006]
            0x00211026: ('IS', '32', 'MiscSequenceParam', ''),
            0x00211027: ('US', '1', 'IsoCentered', ''),  # 1
            0x0021102A: ('IS', '1-n', 'CoilID', ''),  # [255, 0, 0, 0, 0, 4885, 4884, 8986, 8987, 0, 0]
            0x0021102B: ('ST', '1', 'PatReinPattern', ''),  # '1;HFS;50;;O;0;0;-300303149'
            0x0021102C: ('DS', '3', 'SED', ''),  # [14400, 5.83033, 0]
            0x0021102D: ('DS', '3', 'SARMostCriticalAspect', ''),  # [14400, 5.83033, 0]
            0x0021102E: ('IS', '1', 'StimmOnMode', ''),  # "2"
            0x0021102F: ('DS', '3', 'GradientDelayTime', ''),  # [14400, 5.83033, 0]
            0x00211030: ('DS', '1', 'ReadOutGradientAmplitude', ''),  # "0.0"
            0x00211031: ('IS', '1', 'AbsTablePosition', ''),
            0x00211032: ('SS', '1', 'RFSWDOperationMode', ''),  # 0
            0x00211033: ('SH', '1', 'CoilForGradient2', ''),  # 'GC25'
            0x00211034: ('DS', '1', 'StimFactor', ''),  # "1.0"
            0x00211035: ('DS', '1', 'Stimmaxgesnormonline', ''),  # "0.4865"
            0x00211036: ('DS', '1', 'dBdtmax', ''),  # "0.0"
            0x00211037: ('SH', '1', 'SDS37SH', ''),  # 'No'
            0x00211038: ('DS', '1', 'TransmitterCalibration', ''),  # "439.403"
            0x00211039: ('OB', '1', 'MREVAProtocol', ''),
            0x0021103B: ('DS', '1', 'dBdtLimit', ''),  # "0.0"
            0x0021103C: ('OB', '1', 'VFModelInfo', ''),
            0x0021103D: ('CS', '1', 'PhaseSliceOversampling', ''),  # 'NONE'
            0x0021103E: ('OB', '1', 'VFSettings', ''),
            0x0021103F: ('UT', '1', 'AutoAlignData', ''),
            0x00211040: ('UT', '1', 'FMRIModelParameters', ''),
            0x00211041: ('UT', '1', 'FMRIModelInfo', ''),
            0x00211042: ('UT', '1', 'FMRIExternalParameters', ''),
            0x00211043: ('UT', '1', 'FMRIExternalInfo', ''),
            0x00211044: ('DS', '2', 'B1RMS', ''),  # [100, 0.478768]
            0x00211045: ('CS', '1', 'B1RMSSupervision', ''),  # 'YES'
            0x00211046: ('DS', '1', 'TalesReferencePower', ''),  # "2837.57"
            0x00211047: ('CS', '1', 'SafetyStandard', ''),  # 'IEC'
            0x00211048: ('CS', '1', 'DICOMImageFlavor', ''),
            0x00211049: ('CS', '1', 'DICOMAcquisitionContrast', ''),
            0x00211050: ('US', '1', 'RFEchoTrainLength4MF', ''),  # 1 ??
            0x00211051: ('US', '1', 'GradientEchoTrainLength4MF', ''),  # 0 ??
            0x00211052: ('LO', '1', 'VersionInfo', ''),
            0x00211053: ('CS', '1', 'Laterality4MF', ''),  # 'U'
            0x0021105A: ('CS', '1', 'SDS5ACS', ''),  # 'SE'
            0x0021105B: ('CS', '1', 'SDS5BCS', ''),  # 'SP'
            0x0021105D: ('SL', '1', 'SDS5DSL', ''),  # 0
            0x0021105E: ('LO', '1', 'SDS5ELO', ''),  # 'FoV 250*250'
            0x0021105F: ('SH', '1', 'SDS5FSH', '')  # 'TP 0'
        },
        'SIEMENS MRS 05': {
            0x00211001: ('FD', '1', 'TransmitterReferenceAmplitude', ''),
            0x00211002: ('US', '1', 'HammingFilterWidth', ''),
            0x00211003: ('FD', '3', 'CSIGridShiftVector', ''),
            0x00211004: ('FD', '1', 'MixingTime', ''),
            0x00211040: ('CS', '1', 'SeriesProtocolInstance', ''),
            0x00211041: ('CS', '1', 'SpectroResultType', ''),
            0x00211042: ('CS', '1', 'SpectroResultExtendType', ''),
            0x00211043: ('CS', '1', 'PostProcProtocol', ''),
            0x00211044: ('CS', '1', 'RescanLevel', ''),
            0x00211045: ('OF', '1', 'SpectroAlgoResult', ''),
            0x00211046: ('OF', '1', 'SpectroDisplayParams', ''),
            0x00211047: ('IS', '1', 'VoxelNumber', ''),
            0x00211048: ('SQ', '1', 'APRSequence', ''),
            0x00211049: ('CS', '1', 'SyncData', ''),
            0x0021104A: ('CS', '1', 'PostProcDetailedProtocol', ''),
            0x0021104B: ('CS', '1', 'SpectroResultExtendTypeDetailed', '')
        },
        'SIEMENS MR SDI 02': {
            0x00211101: ('US', '1', 'NumberOfImagesiInMosaic', ''),
            0x00211102: ('FD', '3', 'SliceNormalVector', ''),
            0x00211103: ('DS', '1', 'SliceMeasurementDuration', ''),  # "127500.0"
            0x00211104: ('DS', '1', 'TimeAfterStart', ''),  # "0.0" ??
            0x00211105: ('IS', '1', 'BValue', ''),
            0x00211106: ('LO', '1', 'ICEDims', ''),
            0x0021111A: ('SH', '1', 'RFSWDDataType', ''),  # 'predicated' | 'measured'
            0x0021111B: ('US', '1', 'MoCoQMeasure', ''),
            0x0021111C: ('IS', '1', 'PhaseEncodingDirectionPositive', ''),  # "1"
            0x0021111D: ('OB', '1', 'PixelFile', ''),
            0x0021111F: ('IS', '1', 'FMRIStimulInfo', ''),
            0x00211120: ('DS', '1', 'VoxelInPlaneRot', ''),
            0x00211121: ('CS', '1', 'DiffusionDirectionality4MF', ''),
            0x00211122: ('DS', '1', 'VoxelThickness', ''),
            0x00211123: ('FD', '6', 'BMatrix', ''),
            0x00211124: ('IS', '1', 'MultistepIndex', ''),
            0x00211125: ('LT', '1', 'CompAdjustedParam', ''),
            0x00211126: ('IS', '1', 'CompAlgorithm', ''),
            0x00211127: ('DS', '1', 'VoxelNormalCor', ''),
            0x00211129: ('SH', '1', 'FlowEncodingDirection', ''),
            0x0021112A: ('DS', '1', 'VoxelNormalSag', ''),
            0x0021112B: ('DS', '1', 'VoxelPositionSag', ''),
            0x0021112C: ('DS', '1', 'VoxelNormalTra', ''),
            0x0021112D: ('DS', '1', 'VoxelPositionTra', ''),
            0x0021112E: ('UL', '1', 'UsedChannelMask', ''),
            0x0021112F: ('DS', '1', 'RepetitionTimeEffective', ''),
            0x00211130: ('DS', '6', 'CSIImageOrientationPatient', ''),
            0x00211132: ('DS', '1', 'CSISliceLocation', ''),
            0x00211133: ('IS', '1', 'EchoColumnPosition', ''),  # "128"
            0x00211134: ('FD', '1', 'FlowVENC', ''),
            0x00211135: ('IS', '1', 'MeasuredFourierLines', ''),
            0x00211136: ('SH', '1', 'LQAlgorithm', ''),
            0x00211137: ('DS', '1', 'VoxelPositionCor', ''),
            0x00211138: ('IS', '1', 'Filter2', ''),
            0x00211139: ('FD', '1', 'FMRIStimulLevel', ''),
            0x0021113A: ('DS', '1', 'VoxelReadoutFOV', ''),
            0x0021113B: ('IS', '1', 'NormalizeManipulated', ''),
            0x0021113C: ('FD', '3', 'RBMoCoRot', ''),
            0x0021113D: ('IS', '1', 'CompManualAdjusted', ''),
            0x0021113F: ('SH', '1', 'SpectrumTextRegionLabel', ''),
            0x00211140: ('DS', '1', 'VoxelPhaseFOV', ''),
            0x00211141: ('SH', '1', 'GSWDDataType', ''),  # 'predicated' | 'measured'
            0x00211142: ('IS', '1', 'RealDwellTime', ''),  # "7500"
            0x00211143: ('LT', '1', 'CompJobID', ''),
            0x00211144: ('IS', '1', 'CompBlended', ''),
            0x00211145: ('SL', '3', 'ImaAbsTablePosition', ''),  # [0, 0, -1130]
            0x00211146: ('FD', '3', 'DiffusionGradientDirection', ''),
            0x00211147: ('IS', '1', 'FlowEncodingDirection', ''),
            0x00211148: ('IS', '1', 'EchoPartitionPosition', ''),  # "32"
            0x00211149: ('IS', '1', 'EchoLinePosition', ''),  # "128"
            0x0021114B: ('LT', '1', 'CompAutoParam', ''),
            0x0021114C: ('IS', '1', 'OriginalImageNumber', ''),
            0x0021114D: ('IS', '1', 'OriginalSeriesNumber', ''),
            0x0021114E: ('IS', '1', 'Actual3DImaPartNumber', ''),
            0x0021114F: ('LO', '1', 'ImaCoilString', ''),  # 'HE1-4;NE1,2'
            0x00211150: ('DS', '2', 'CSIPixelSpacing', ''),
            0x00211151: ('UL', '1', 'SequenceMask', ''),  # 134217728 = 0x8000000
            0x00211152: ('US', '1', 'ImageGroup', ''),
            0x00211153: ('FD', '1', 'BandwidthPerPixelPhaseEncode', ''),
            0x00211154: ('US', '1', 'NonPlanarImage', ''),
            0x00211155: ('OB', '1', 'PixelFileName', ''),
            0x00211156: ('LO', '1', 'ImaPATModeText', ''),
            0x00211157: ('DS', '3', 'CSIImagePositionPatient', ''),
            0x00211158: ('SH', '1', 'AcquisitionMatrixText', ''),
            0x00211159: ('IS', '3', 'ImaRelTablePosition', ''),  # [0, 0, 0]
            0x0021115A: ('FD', '3', 'RBMoCoTrans', ''),
            0x0021115B: ('FD', '3', 'SlicePositionPCS', ''),  # [-124.99999999938788, -125.00000000061212, 0.0]
            0x0021115C: ('DS', '1', 'CSISliceThickness', ''),
            0x0021115E: ('IS', '1', 'ProtocolSliceNumber', ''),  # "0"
            0x0021115F: ('IS', '1', 'Filter1', ''),
            0x00211160: ('SH', '1', 'TransmittingCoil', ''),
            0x00211161: ('DS', '1', 'NumberOfAveragesN4', ''),
            0x00211162: ('FD', '1-n', 'MosaicRefAcqTimes', ''),
            0x00211163: ('IS', '1', 'AutoInlineImageFilterEnabled', ''),  # "1"
            0x00211165: ('FD', '1-n', 'QCData', ''),
            0x00211166: ('LT', '1', 'ExamLandmarks', ''),
            0x00211167: ('ST', '1', 'ExamDataRole', ''),
            0x00211168: ('OB', '1', 'MRDiffusion', ''),
            0x00211169: ('OB', '1', 'RealWorldValueMapping', ''),
            0x00211170: ('OB', '1', 'DataSetInfo', ''),
            0x00211171: ('UT', '1', 'UsedChannelString', ''),
            0x00211172: ('CS', '1', 'PhaseContrastN4', ''),
            0x00211173: ('UT', '1', 'MRVelocityEncoding', ''),
            0x00211174: ('FD', '3', 'VelocityEncodingDirectionN4', ''),
            0x00211175: ('CS', '1-n', 'ImageType4MF', ''),
            0x00211176: ('LO', '1-n', 'ImageHistory', ''),
            0x00211177: ('LO', '1', 'SequenceInfo', ''),  # ?? '*sd2d1'  ??
            0x00211178: ('CS', '1', 'ImageTypeVisible', ''),  # ?? 'DIS2D' ??
            0x00211179: ('CS', '1', 'DistortionCorrectionType', ''),  # eg 'DIS2D'
            0x00211180: ('CS', '1', 'ImageFilterType', ''),  # ?? "0.0" ??
            0x00211188: ('DS', '1', 'SDI88DS', ''),  # "0.0"
            0x0021118A: ('IS', '1', 'SDI8ASH', '')  # 'SP  0.0'
        },
        'Philips Imaging DD 001': {
            0x20010001: ('FL', '1', 'ChemicalShift', ''),
            0x20010002: ('IS', '1', 'ChemicalShiftNumberMR', ''),
            0x20010003: ('FL', '1', 'DiffusionBFactor', ''),
            0x20010004: ('CS', '1', 'DiffusionDirection', ''),
            0x20010005: ('SS', '1', 'GraphicAnnotationParentID', ''),
            0x20010006: ('CS', '1', 'ImageEnhanced', ''),
            0x20010007: ('CS', '1', 'ImageTypeEDES', ''),
            0x20010008: ('IS', '1', 'PhaseNumber', ''),
            0x20010009: ('FL', '1', 'ImagePrepulseDelay', ''),
            0x2001000A: ('IS', '1', 'SliceNumber', ''),
            0x2001000B: ('CS', '1', 'SliceOrientation', ''),
            0x2001000C: ('CS', '1', 'ArrhythmiaRejection', ''),
            0x2001000E: ('CS', '1', 'CardiacCycled', ''),
            0x2001000F: ('SS', '1', 'CardiacGateWidth', ''),
            0x20010010: ('CS', '1', 'CardiacSync', ''),
            0x20010011: ('FL', '1', 'DiffusionEchoTime', ''),
            0x20010012: ('CS', '1', 'DynamicSeries', ''),
            0x20010013: ('SL', '1', 'EPIFactor', ''),
            0x20010014: ('SL', '1', 'NumberOfEchoes', ''),
            0x20010015: ('SS', '1', 'NumberOfLocations', ''),
            0x20010016: ('SS', '1', 'NumberOfPCDirections', ''),
            0x20010017: ('SL', '1', 'NumberOfPhases', ''),
            0x20010018: ('SL', '1', 'NumberOfSlices', ''),
            0x20010019: ('CS', '1', 'PartialMatrixScanned', ''),
            0x2001001A: ('FL', '3', 'PCVelocity', ''),
            0x2001001B: ('FL', '1', 'PrepulseDelay', ''),
            0x2001001C: ('CS', '1', 'PrepulseType', ''),
            0x2001001D: ('IS', '1', 'ReconstructionNumber', ''),
            0x2001001E: ('CS', '1', 'ReformatAccuracy', ''),
            0x2001001F: ('CS', '1', 'RespirationSync', ''),
            0x20010020: ('LO', '1', 'ScanningTechnique', ''),
            0x20010021: ('CS', '1', 'SPIR', ''),
            0x20010022: ('FL', '1', 'WaterFatShift', ''),
            0x20010023: ('DS', '1', 'FlipAngle', ''),
            0x20010024: ('CS', '1', 'SeriesIsInteractive', ''),
            0x20010025: ('SH', '1', 'EchoTimeDisplay', ''),
            0x20010026: ('CS', '1', 'PresentationStateSubtractionActive', ''),
            0x20010029: ('FL', '1', 'DD001Private20010029FL', ''),
            0x2001002B: ('CS', '1', 'DD001Private2001002BCS', ''),
            0x2001002D: ('SS', '1', 'NumberOfSlicesInStack', ''),
            0x20010032: ('FL', '1', 'StackRadialAngle', ''),
            0x20010033: ('CS', '1', 'StackRadialAxis', ''),
            0x20010035: ('SS', '1', 'StackSliceNumber', ''),
            0x20010036: ('CS', '1', 'StackType', ''),
            0x20010039: ('FL', '1', 'DD001Private20010039FL', ''),
            0x2001003D: ('UL', '1', 'ContourFillColor', ''),
            0x2001003F: ('CS', '1', 'DisplayedAreaZoomInterpolationMeth', ''),
            0x20010043: ('IS', '2', 'EllipsDisplShutMajorAxFrstEndPnt', ''),
            0x20010044: ('IS', '2', 'EllipsDisplShutMajorAxScndEndPnt', ''),
            0x20010045: ('IS', '2', 'EllipsDisplShutOtherAxFrstEndPnt', ''),
            0x20010046: ('CS', '1', 'GraphicLineStyle', ''),
            0x20010047: ('FL', '1', 'GraphicLineWidth', ''),
            0x20010048: ('SS', '1', 'GraphicAnnotationID', ''),
            0x2001004B: ('CS', '1', 'InterpolationMethod', ''),
            0x2001004C: ('CS', '1', 'PolyLineBeginPointStyle', ''),
            0x2001004D: ('CS', '1', 'PolyLineEndPointStyle', ''),
            0x2001004E: ('CS', '1', 'WindowSmoothingTaste', ''),
            0x20010050: ('LO', '1', 'GraphicMarkerType', ''),
            0x20010051: ('IS', '1', 'OverlayPlaneID', ''),
            0x20010052: ('UI', '1', 'ImagePresentationStateUID', ''),
            0x20010053: ('CS', '1', 'PresentationGLTrafoInvert', ''),
            0x20010054: ('FL', '1', 'ContourFillTransparency', ''),
            0x20010055: ('UL', '1', 'GraphicLineColor', ''),
            0x20010056: ('CS', '1', 'GraphicType', ''),
            0x20010058: ('UL', '1', 'ContrastTransferTaste', ''),
            0x2001005A: ('ST', '1', 'GraphicAnnotationModel', ''),
            0x2001005D: ('ST', '1', 'MeasurementTextUnits', ''),
            0x2001005E: ('ST', '1', 'MeasurementTextType', ''),
            0x2001005F: ('SQ', '1', 'StackSequence', ''),
            0x20010060: ('SL', '1', 'NumberOfStacks', ''),
            0x20010061: ('CS', '1', 'SeriesTransmitted', ''),
            0x20010062: ('CS', '1', 'SeriesCommitted', ''),
            0x20010063: ('CS', '1', 'ExaminationSource', ''),
            0x20010064: ('SH', '1', 'TextType', ''),
            0x20010065: ('SQ', '1', 'GraphicOverlayPlane', ''),
            0x20010067: ('CS', '1', 'LinearPresentationGLTrafoShapeSub', ''),
            0x20010068: ('SQ', '1', 'LinearModalityGLTrafo', ''),
            0x20010069: ('SQ', '1', 'DisplayShutter', ''),
            0x2001006A: ('SQ', '1', 'SpatialTransformation', ''),
            0x2001006B: ('SQ', '1', 'DD001Private2001006BSQ', ''),
            0x2001006D: ('LO', '1', 'TextFont', ''),
            0x2001006E: ('SH', '1', 'SeriesType', ''),
            0x20010071: ('CS', '1', 'GraphicConstraint', ''),
            0x20010072: ('IS', '1', 'EllipsDisplShutOtherAxScndEndPnt', ''),
            0x20010074: ('DS', '1', 'DD001Private20010074DS', ''),
            0x20010075: ('DS', '1', 'DD001Private20010075DS', ''),
            0x20010076: ('UL', '1', 'NumberOfFrames', ''),
            0x20010077: ('CS', '1', 'GLTrafoType', ''),
            0x2001007A: ('FL', '1', 'WindowRoundingFactor', ''),
            0x2001007B: ('IS', '1', 'AcquisitionNumber', ''),
            0x2001007C: ('US', '1', 'FrameNumber', ''),
            0x20010080: ('LO', '1', 'DD001Private20010080LO', ''),
            0x20010081: ('IS', '1', 'NumberOfDynamicScans', ''),
            0x20010082: ('IS', '1', 'EchoTrainLength', ''),
            0x20010083: ('DS', '1', 'ImagingFrequency', ''),
            0x20010084: ('DS', '1', 'InversionTime', ''),
            0x20010085: ('DS', '1', 'MagneticFieldStrength', ''),
            0x20010086: ('IS', '1', 'NrOfPhaseEncodingSteps', ''),
            0x20010087: ('SH', '1', 'ImagedNucleus', ''),
            0x20010088: ('DS', '1', 'NumberOfAverages', ''),
            0x20010089: ('DS', '1', 'PhaseFOVPercent', ''),
            0x2001008A: ('DS', '1', 'SamplingPercent', ''),
            0x2001008B: ('SH', '1', 'TransmittingCoil', ''),
            0x20010090: ('LO', '1', 'TextForegroundColor', ''),
            0x20010091: ('LO', '1', 'TextBackgroundColor', ''),
            0x20010092: ('LO', '1', 'TextShadowColor', ''),
            0x20010093: ('LO', '1', 'TextStyle', ''),
            0x2001009A: ('SQ', '1', 'DD001Private2001009ASQ', ''),
            0x2001009B: ('UL', '1', 'GraphicNumber', ''),
            0x2001009C: ('LO', '1', 'GraphicAnnotationLabel', ''),
            0x2001009F: ('US', '2', 'PixelProcessingKernelSize', ''),
            0x200100A1: ('CS', '1', 'IsRawImage', ''),
            0x200100A3: ('UL', '1', 'TextColorForeground', ''),
            0x200100A4: ('UL', '1', 'TextColorBackground', ''),
            0x200100A5: ('UL', '1', 'TextColorShadow', ''),
            0x200100C8: ('LO', '1', 'ExamCardName', ''),
            0x200100CC: ('ST', '1', 'DerivationDescription', ''),
            0x200100DA: ('CS', '1', 'DD001Private200100DACS', ''),
            0x200100F1: ('FL', '6', 'ProspectiveMotionCorrection', ''),
            0x200100F2: ('FL', '6', 'RetrospectiveMotionCorrection', '')
        },
        'Philips Imaging DD 002': {
            0x20010001: ('US', '1', 'DD002Private20011101US', ''),
            0x20010002: ('FD', '1', 'DD002Private20011102FD', ''),
            0x20010013: ('SS', '1', 'DD002Private20011113SS', ''),
            0x20010014: ('FD', '1', 'DD002Private20011114FD', ''),
            0x20010015: ('FD', '1', 'DD002Private20011115SS', ''),
            0x20010016: ('FD', '1', 'DD002Private20011116SS', ''),
            0x20010017: ('FD', '1', 'DD002Private20011117SS', ''),
            0x20010018: ('CS', '1', 'DD002Private20011118CS', ''),
            0x20010019: ('FD', '1', 'DD002Private20011119FD', ''),
            0x2001001A: ('FD', '1', 'DD002Private2001111AFD', ''),
            0x2001001B: ('FD', '1', 'DD002Private2001111BFD', ''),
            0x2001001C: ('FD', '1', 'DD002Private2001111CFD', ''),
            0x2001001D: ('FD', '1', 'DD002Private2001111DFD', ''),
            0x2001001E: ('FD', '1', 'DD002Private2001111EFD', ''),
            0x2001001F: ('FD', '1', 'DD002Private2001111FFD', ''),
            0x20010020: ('FD', '1', 'DD002Private20011120FD', ''),
            0x20010021: ('FD', '1', 'DD002Private20011121FD', ''),
            0x20010022: ('FD', '1', 'DD002Private20011122FD', ''),
            0x20010023: ('FD', '1', 'DD002Private20011123FD', ''),
            0x20010024: ('FD', '1', 'DD002Private20011124FD', ''),
            0x20010025: ('FD', '1', 'DD002Private20011125FD', ''),
            0x20010026: ('FD', '1', 'DD002Private20011126FD', ''),
            0x20010027: ('FD', '1', 'DD002Private20011127FD', ''),
            0x20010028: ('US', '1', 'DD002Private20011128US', ''),
            0x20010029: ('US', '1', 'DD002Private20011129US', ''),
            0x2001002A: ('US', '1', 'DD002Private2001112AUS', ''),
            0x2001002B: ('SS', '1', 'DD002Private2001112BSS', ''),
            0x2001002C: ('FD', '1', 'DD002Private2001112CFD', ''),
            0x2001002D: ('FD', '1', 'DD002Private2001112DFD', ''),
            0x2001002E: ('SS', '1', 'DD002Private2001112ESS', ''),
            0x2001002F: ('SS', '1', 'DD002Private2001112FSS', ''),
            0x20010030: ('SS', '1', 'DD002Private20011130SS', ''),
            0x20010031: ('SS', '1', 'DD002Private20011131SS', ''),
            0x20010032: ('SS', '1', 'DD002Private20011132SS', ''),
            0x20010033: ('SS', '1', 'DD002Private20011133SS', ''),
            0x20010034: ('SS', '1', 'DD002Private20011134SS', ''),
            0x20010035: ('FD', '1', 'DD002Private20011135FD', ''),
            0x20010036: ('FD', '1', 'DD002Private20011136FD', ''),
            0x20010037: ('FD', '1', 'DD002Private20011137FD', ''),
            0x20010039: ('CS', '1', 'DD002Private20011139CS', ''),
            0x2001003A: ('SQ', '1', 'DD002Private2001113ASQ', ''),
            0x2001003B: ('SQ', '1', 'DD002Private2001113BSQ', ''),
            0x2001003C: ('SQ', '1', 'DD002Private2001113CSQ', ''),
            0x2001003D: ('SQ', '1', 'DD002Private2001113DSQ', ''),
            0x2001003E: ('SS', '1', 'DD002Private2001113ESS', ''),
            0x2001003F: ('SS', '1', 'DD002Private2001113FSS', ''),
            0x20010040: ('SS', '1', 'DD002Private20011140SS', ''),
            0x2001006B: ('LO', '1', 'DD002Private2001116BLO', ''),
            0x2001006C: ('LO', '1', 'DD002Private2001116CLO', ''),
            0x20010072: ('FL', '2', 'DD002Private20011172FL', ''),
            0x20010073: ('FL', '2', 'DD002Private20011173FL', ''),
            0x200100B8: ('CS', '1', 'DD002Private200111B8CS', ''),
            0x2001116B: ('LO', '1', "DD002Private2001116BLO", '')
        },
        'Philips MR Imaging DD 001': {
            0x20050000: ('FL', '1', 'ImageAngulationAP', ''),
            0x20050001: ('FL', '1', 'ImageAngulationFH', ''),
            0x20050002: ('FL', '1', 'ImageAngulationRL', ''),
            0x20050003: ('IS', '1', 'ImageAnnotationCount', ''),
            0x20050004: ('CS', '1', 'ImageDisplayOrientation', ''),
            0x20050005: ('CS', '1', 'SynergyReconstructionType', ''),
            0x20050007: ('IS', '1', 'ImageLineCount', ''),
            0x20050008: ('FL', '1', 'ImageOffcenterAP', ''),
            0x20050009: ('FL', '1', 'ImageOffcenterFH', ''),
            0x2005000A: ('FL', '1', 'ImageOffCentreRL',  ''),
            0x2005000B: ('FL', '1', 'MaxFP', ''),
            0x2005000C: ('FL', '1', 'MinFP', ''),
            0x2005000D: ('FL', '1', 'ScaleIntercept', ''),
            0x2005000E: ('FL', '1', 'ScaleSlope', ''),
            0x2005000F: ('DS', '1', 'WindowCenter', ''),
            0x20050010: ('DS', '1', 'WindowWidth', ''),
            0x20050011: ('CS', '1-n', 'ImageType', ''),
            0x20050012: ('CS', '1', 'CardiacGating', ''),
            0x20050013: ('CS', '1', 'DevelopmentMode', ''),
            0x20050014: ('CS', '1', 'Diffusion', ''),
            0x20050015: ('CS', '1', 'FatSaturation', ''),
            0x20050016: ('CS', '1', 'FlowCompensation', ''),
            0x20050017: ('CS', '1', 'FourierInterpolation', ''),
            0x20050018: ('LO', '1', 'HardcopyProtocol', ''),
            0x20050019: ('CS', '1', 'InverseReconstructed', ''),
            0x2005001A: ('SS', '1', 'LabelSyntax', ''),
            0x2005001B: ('CS', '1', 'MagnetizationPrepared', ''),
            0x2005001C: ('CS', '1', 'MagnetizationTransferContrast', ''),
            0x2005001D: ('SS', '1', 'MeasurementScanResolution', ''),
            0x2005001E: ('SH', '1', 'MIPProtocol', ''),
            0x2005001F: ('SH', '1', 'MPRProtocol', ''),
            0x20050020: ('SL', '1', 'NumberOfChemicalShifts', ''),
            0x20050021: ('SS', '1', 'NumberOfMixes', ''),
            0x20050022: ('IS', '1', 'NumberOfReferences', ''),
            0x20050023: ('SS', '1', 'NumberOfSlabs', ''),
            0x20050025: ('SS', '1', 'NumberOfVolumes', ''),
            0x20050026: ('CS', '1', 'OverSamplingPhase', ''),
            0x20050027: ('CS', '1', 'PackageMode', ''),
            0x20050028: ('CS', '1', 'PartialFourierFrequency', ''),
            0x20050029: ('CS', '1', 'PartialFourierPhase', ''),
            0x2005002A: ('IS', '1', 'PatientReferenceID', ''),
            0x2005002B: ('SS', '1', 'PercentScanComplete', ''),
            0x2005002C: ('CS', '1', 'PhaseEncodeReordering', ''),
            0x2005002D: ('IS', '1', 'PlanScanSurveyNumberOfImages', ''),
            0x2005002E: ('CS', '1', 'PPGPPUGating', ''),
            0x2005002F: ('CS', '1', 'SpatialPresaturation', ''),
            0x20050030: ('FL', '1-n', 'RepetitionTime', ''),
            0x20050031: ('CS', '1', 'RespiratoryGating', ''),
            0x20050032: ('CS', '1', 'SampleRepresentation', ''),
            0x20050033: ('FL', '1', 'AcquisitionDuration', ''),
            0x20050034: ('CS', '1', 'SegmentedKSpace', ''),
            0x20050035: ('CS', '1', 'DataType', ''),
            0x20050036: ('CS', '1', 'IsCardiac', ''),
            0x20050037: ('CS', '1', 'IsSpectro', ''),
            0x20050038: ('CS', '1', 'Spoiled', ''),
            0x20050039: ('CS', '1', 'SteadyState', ''),
            0x2005003A: ('SH', '1', 'SubAnatomy', ''),
            0x2005003B: ('CS', '1', 'TimeReversedSteadyState', ''),
            0x2005003C: ('CS', '1', 'TiltOptimizedNonsaturatedExcitation', ''),
            0x2005003D: ('SS', '1', 'NumberOfRRIntervalRanges', ''),
            0x2005003E: ('SL', '1-n', 'RRIntervalsDistribution', ''),
            0x2005003F: ('SL', '1', 'PlanScanAcquisitionNumber',  ''),
            0x20050040: ('SL', '1-n', 'PlanScanSurveyChemicalShiftNumber', ''),
            0x20050041: ('SL', '1-n', 'PlanScanSurveyDynamicScanNumber', ''),
            0x20050042: ('SL', '1-n', 'PlanScanSurveyEchoNumber', ''),
            0x20050043: ('CS', '1-n', 'PlanScanSurveyImageType', ''),
            0x20050044: ('SL', '1-n', 'PlanScanSurveyPhaseNumber', ''),
            0x20050045: ('SL', '1-n', 'PlanScanSurveyReconstructionNumber', ''),
            0x20050046: ('CS', '1-n', 'PlanScanSurveyScanningSequence', ''),
            0x20050047: ('SL', '1-n', 'PlanScanSurveyCSliceNumber', ''),
            0x20050048: ('IS', '1-n', 'ReferencedAcquisitionNumber', ''),
            0x20050049: ('IS', '1-n', 'ReferencedChemicalShiftNumber', ''),
            0x2005004A: ('IS', '1-n', 'ReferenceDynamicScanNumber', ''),
            0x2005004B: ('IS', '1-n', 'ReferencedEchoNumber', ''),
            0x2005004C: ('CS', '1-n', 'ReferencedEntity', ''),
            0x2005004D: ('CS', '1-n', 'ReferencedImageType', ''),
            0x2005004E: ('FL', '1-n', 'SlabFOVRL', ''),
            0x2005004F: ('FL', '1-n', 'SlabOffcentreAP', ''),
            0x20050050: ('FL', '1-n', 'SlabOffcentreFH', ''),
            0x20050051: ('FL', '1-n', 'SlabOffcentreRL', ''),
            0x20050052: ('CS', '1-n', 'SlabType', ''),
            0x20050053: ('CS', '1-n', 'SlabViewAxis', ''),
            0x20050054: ('FL', '1-n', 'VolumeAngulationAP', ''),
            0x20050055: ('FL', '1-n', 'VolumeAngulationFH', ''),
            0x20050056: ('FL', '1-n', 'VolumeAngulationRL', ''),
            0x20050057: ('FL', '1-n', 'VolumeFOVAP', ''),
            0x20050058: ('FL', '1-n', 'VolumeFOVFH', ''),
            0x20050059: ('FL', '1-n', 'VolumeFOVRL', ''),
            0x2005005A: ('FL', '1-n', 'VolumeOffcentreAP', ''),
            0x2005005B: ('FL', '1-n', 'VolumeOffcentreFH', ''),
            0x2005005C: ('FL', '1-n', 'VolumeOffcentreRL', ''),
            0x2005005D: ('CS', '1-n', 'VolumeType', ''),
            0x2005005E: ('CS', '1-n', 'VolumeViewAxis', ''),
            0x2005005F: ('CS', '1', 'StudyOrigin', ''),
            0x20050060: ('IS', '1', 'StudySequenceNumber', ''),
            0x20050061: ('CS', '1', 'PrepulseType', ''),
            0x20050063: ('SS', '1', 'fMRIStatusIndication', ''),
            0x20050064: ('IS', '1-n', 'ReferencePhaseNumber', ''),
            0x20050065: ('IS', '1-n', 'ReferenceReconstructionNumber', ''),
            0x20050066: ('CS', '1-n', 'ReferenceScanningSequence', ''),
            0x20050067: ('IS', '1-n', 'ReferenceSliceNumber', ''),
            0x20050068: ('CS', '1-n', 'ReferenceType', ''),
            0x20050069: ('FL', '1-n', 'SlabAngulationAP', ''),
            0x2005006A: ('FL', '1-n', 'SlabAngulationFH', ''),
            0x2005006B: ('FL', '1-n', 'SlabAngulationRL', ''),
            0x2005006C: ('FL', '1-n', 'SlabFOVAP', ''),
            0x2005006D: ('FL', '1-n', 'SlabFOVFH', ''),
            0x2005006E: ('CS', '1-n', 'ScanningSequence', ''),
            0x2005006F: ('CS', '1', 'AcquisitionType', ''),
            0x20050070: ('LO', '1', 'HardcopyProtocolEV', ''),
            0x20050071: ('FL', '1-n', 'StackAngulationAP', ''),
            0x20050072: ('FL', '1-n', 'StackAngulationFH', ''),
            0x20050073: ('FL', '1-n', 'StackAngulationRL', ''),
            0x20050074: ('FL', '1-n', 'StackFOVAP', ''),
            0x20050075: ('FL', '1-n', 'StackFOVFH', ''),
            0x20050076: ('FL', '1-n', 'StackFOVRL', ''),
            0x20050078: ('FL', '1-n', 'StackOffcentreAP', ''),
            0x20050079: ('FL', '1-n', 'StackOffcentreFH', ''),
            0x2005007A: ('FL', '1-n', 'StackOffcentreRL', ''),
            0x2005007B: ('CS', '1-n', 'StackPreparationDirection', ''),
            0x2005007E: ('FL', '1-n', 'StackSliceDistance', ''),
            0x20050080: ('SQ', '1', 'SeriesPlanScan', ''),
            0x20050081: ('CS', '1-n', 'StackViewAxis', ''),
            0x20050083: ('SQ', '1', 'SeriesSlab', ''),
            0x20050084: ('SQ', '1', 'SeriesReference', ''),
            0x20050085: ('SQ', '1', 'SeriesVolume', ''),
            0x20050086: ('SS', '1', 'NumberOfGeometry', ''),
            0x20050087: ('SL', '1-n', 'NumberOfGeometrySlices', ''),
            0x20050088: ('FL', '1-n', 'GeomAngulationAP', ''),
            0x20050089: ('FL', '1-n', 'GeomAngulationFH', ''),
            0x2005008A: ('FL', '1-n', 'GeomAngulationRL', ''),
            0x2005008B: ('FL', '1-n', 'GeomFOVAP', ''),
            0x2005008C: ('FL', '1-n', 'GeomFOVFH', ''),
            0x2005008D: ('FL', '1-n', 'GeomFOVRL', ''),
            0x2005008E: ('FL', '1-n', 'GeomOffCentreAP', ''),
            0x2005008F: ('FL', '1-n', 'GeomOffCentreFH', ''),
            0x20050090: ('FL', '1-n', 'GeomOffCentreRL', ''),
            0x20050091: ('CS', '1-n', 'GeomPreparationDirect', ''),
            0x20050092: ('FL', '1-n', 'GeomRadialAngle', ''),
            0x20050093: ('CS', '1-n', 'GeomRadialAxis', ''),
            0x20050094: ('FL', '1-n', 'GeomSliceDistance', ''),
            0x20050095: ('SL', '1-n', 'GeomSliceNumber', ''),
            0x20050096: ('CS', '1-n', 'GeomType', ''),
            0x20050097: ('CS', '1-n', 'GeomViewAxis', ''),
            0x20050098: ('CS', '1-n', 'GeomColour', ''),
            0x20050099: ('CS', '1-n', 'GeomApplicationType', ''),
            0x2005009A: ('SL', '1-n', 'GeomId', ''),
            0x2005009B: ('SH', '1-n', 'GeomApplicationName', ''),
            0x2005009C: ('SH', '1-n', 'GeomLabelName', ''),
            0x2005009D: ('CS', '1-n', 'GeomLineStyle', ''),
            0x2005009E: ('SQ', '1', 'SeriesGeometry', ''),
            0x2005009F: ('CS', '1', 'SpectralSelectiveExcitationPulse', ''),
            0x200500A0: ('FL', '1', 'DynamicScanBeginTime', ''),
            0x200500A1: ('CS', '1', 'SyncraScanType', ''),
            0x200500A2: ('CS', '1', 'IsCOCA', ''),
            0x200500A3: ('IS', '1', 'StackCoilID', ''),
            0x200500A4: ('IS', '1', 'StackCBBCoil1', ''),
            0x200500A5: ('IS', '1', 'StackCBBCoil2', ''),
            0x200500A6: ('IS', '1', 'StackChannelCombi', ''),
            0x200500A7: ('CS', '1', 'StackCoilConnection', ''),
            0x200500A8: ('DS', '1', 'InversionTime', ''),
            0x200500A9: ('CS', '1', 'GeometryCorrection', ''),
            0x200500B0: ('FL', '1', 'DiffusionDirectionRL', ''),
            0x200500B1: ('FL', '1', 'DiffusionDirectionAP', ''),
            0x200500B2: ('FL', '1', 'DiffusionDirectionFH', ''),
            0x200500C0: ('CS', '1', 'ScanSequence', '')
        },
        'Philips MR Imaging DD 002': {
            0x20050015: ('LO', '1', 'UserName', ''),
            0x20050016: ('LO', '1', 'PassWord', ''),
            0x20050017: ('LO', '1', 'ServerName', ''),
            0x20050018: ('LO', '1', 'DataBaseName', ''),
            0x20050019: ('LO', '1', 'RootName', ''),
            0x20050020: ('LO', '1', 'DMIApplicationName', ''),
            0x2005002D: ('LO', '1', 'RootId', ''),
            0x20050032: ('SQ', '1', 'BlobDataObjectArray', ''),
            0x20050034: ('LT', '1', 'SeriesTransactionUID', ''),
            0x20050035: ('IS', '1', 'ParentID', ''),
            0x20050036: ('LO', '1', 'ParentType', ''),
            0x20050037: ('LO', '1', 'BlobName', ''),
            0x20050038: ('LO', '1', 'ApplicationName', ''),
            0x20050039: ('LO', '1', 'TypeName', ''),
            0x20050040: ('LO', '1', 'VersionStr', ''),
            0x20050041: ('LO', '1', 'CommentStr', ''),
            0x20050042: ('CS', '1', 'BlobInFile', ''),
            0x20050043: ('SL', '1', 'ActualBlobSize', ''),
            0x20050044: ('OW', '1', 'BlobData', ''),
            0x20050045: ('LO', '1', 'BlobFilename', ''),
            0x20050046: ('SL', '1', 'BlobOffset', ''),
            0x20050047: ('CS', '1', 'BlobFlag', ''),
            0x20050099: ('UL', '1', 'NumberOfRequestExcerpts', '')
        },
        'Philips MR Imaging DD 003': {
            0x20050000: ('UL', '1', 'NumberOfSOPCommon', ''),
            0x20050001: ('UL', '1', 'NoOfFilmConsumption', ''),
            0x20050013: ('UL', '1', 'NumberOfCodes', ''),
            0x20050034: ('SL', '1', 'NumberOfImagePerSeriesRef', ''),
            0x20050043: ('SS', '1', 'NoDateOfLastCalibration', ''),
            0x20050044: ('SS', '1', 'NoTimeOfLastCalibration', ''),
            0x20050045: ('SS', '1', 'NrOfSoftwareVersion', ''),
            0x20050047: ('SS', '1', 'NrOfPatientOtherNames', ''),
            0x20050048: ('SS', '1', 'NrOfReqRecipeOfResults', ''),
            0x20050049: ('SS', '1', 'NrOfSeriesOperatorsName', ''),
            0x20050050: ('SS', '1', 'NrOfSeriesPerfPhysiName', ''),
            0x20050051: ('SS', '1', 'NrOfStudyAdmittingDiagnosticDescr', ''),
            0x20050052: ('SS', '1', 'NrOfStudyPatientContrastAllergies', ''),
            0x20050053: ('SS', '1', 'NrOfStudyPatientMedicalAlerts', ''),
            0x20050054: ('SS', '1', 'NrOfStudyPhysiciansOfRecord', ''),
            0x20050055: ('SS', '1', 'NrOfStudyPhysiReadingStudy', ''),
            0x20050056: ('SS', '1', 'NrSCSoftwareVersions', ''),
            0x20050057: ('SS', '1', 'NrRunningAttributes', ''),
            0x20050070: ('OW', '1', 'SpectrumPixelData', ''),
            0x20050081: ('UI', '1', 'DefaultImageUID', ''),
            0x20050082: ('CS', '1-n', 'RunningAttributes', '')
        },
        'Philips MR Imaging DD 004': {
            0x20050000: ('SS', '1', 'SpectrumExtraNumber', ''),
            0x20050001: ('SS', '1', 'SpectrumKxCoordinate', ''),
            0x20050002: ('SS', '1', 'SpectrumKyCoordinate', ''),
            0x20050003: ('SS', '1', 'SpectrumLocationNumber', ''),
            0x20050004: ('SS', '1', 'SpectrumMixNumber', ''),
            0x20050005: ('SS', '1', 'SpectrumXCoordinate', ''),
            0x20050006: ('SS', '1', 'SpectrumYCoordinate', ''),
            0x20050007: ('FL', '1', 'SpectrumDCLevel', ''),
            0x20050008: ('FL', '1', 'SpectrumNoiseLevel', ''),
            0x20050009: ('FL', '1', 'SpectrumBeginTime', ''),
            0x20050010: ('FL', '1', 'SpectrumEchoTime', ''),
            0x20050012: ('FL', '1', 'SpectrumInversionTime', ''),
            0x20050013: ('SS', '1', 'SpectrumNumber', ''),
            0x20050014: ('SS', '1', 'SpectrumNumberOfAverages', ''),
            0x20050015: ('SS', '1', 'SpectrumNumberOfSamples', ''),
            0x20050016: ('SS', '1', 'SpectrumScanSequenceNumber', ''),
            0x20050017: ('SS', '1', 'SpectrumNumberOfPeaks', ''),
            0x20050018: ('SQ', '1', 'SpectrumPeak', ''),
            0x20050019: ('FL', '1-n', 'SpectrumPeakIntensity', ''),
            0x20050020: ('LO', '1-n', 'SpectrumPeakLabel', ''),
            0x20050021: ('FL', '1-n', 'SpectrumPeakPhase', ''),
            0x20050022: ('FL', '1-n', 'SpectrumPeakPosition', ''),
            0x20050023: ('CS', '1-n', 'SpectrumPeakType', ''),
            0x20050024: ('FL', '1-n', 'SpectrumPeakWidth', ''),
            0x20050025: ('CS', '1', 'SpectroSIB0Correction', ''),
            0x20050026: ('FL', '1', 'SpectroB0EchoTopPosition', ''),
            0x20050027: ('CS', '1', 'SpectroComplexComponent', ''),
            0x20050028: ('CS', '1', 'SpectroDataOrigin', ''),
            0x20050029: ('FL', '1', 'SpectroEchoTopPosition', ''),
            0x20050030: ('CS', '1-n', 'InPlaneTransforms', ''),
            0x20050031: ('SS', '1', 'NumberOfSpectraAcquired', ''),
            0x20050033: ('FL', '1', 'PhaseEncodingEchoTopPositions', ''),
            0x20050034: ('CS', '1', 'PhysicalQuantityForChemicalShift', ''),
            0x20050035: ('CS', '1', 'PhysicalQuantitySpatial', ''),
            0x20050036: ('FL', '1', 'ReferenceFrequency', ''),
            0x20050037: ('FL', '1', 'SampleOffset', ''),
            0x20050038: ('FL', '1', 'SamplePitch', ''),
            0x20050039: ('SS', '2', 'SearchIntervalForPeaks', ''),
            0x20050040: ('CS', '1', 'SignalDomainForChemicalShift', ''),
            0x20050041: ('CS', '1', 'SignalDomainSpatial', ''),
            0x20050042: ('CS', '1', 'SignalType', ''),
            0x20050043: ('CS', '1', 'SpectroAdditionalRotations', ''),
            0x20050044: ('SS', '1-n', 'SpectroDisplayRanges', ''),
            0x20050045: ('CS', '1', 'SpectroEchoAcquisition', ''),
            0x20050046: ('CS', '1', 'SpectroFrequencyUnit', ''),
            0x20050047: ('FL', '1', 'SpectroGamma', ''),
            0x20050048: ('CS', '1', 'SpectroHiddenLineRemoval', ''),
            0x20050049: ('FL', '1', 'SpectroHorizontalShift', ''),
            0x20050050: ('FL', '2', 'SpectroHorizontalWindow', ''),
            0x20050051: ('SS', '1', 'SpectroNumberOfDisplayRanges', ''),
            0x20050052: ('SS', '1', 'SpectroNumberOfEchoPulses', ''),
            0x20050053: ('LO', '1-n', 'SpectroProcessingHistory', ''),
            0x20050054: ('CS', '1', 'SpectroScanType', ''),
            0x20050055: ('FL', '1-n', 'SpectroSICSIntervals', ''),
            0x20050056: ('CS', '1', 'SpectroSIMode', ''),
            0x20050057: ('SS', '1', 'SpectroSpectralBW', ''),
            0x20050058: ('LO', '1', 'SpectroTitleLine', ''),
            0x20050059: ('FL', '1', 'SpectroTurboEchoSpacing', ''),
            0x20050060: ('FL', '1', 'SpectroVerticalShift', ''),
            0x20050061: ('FL', '2', 'SpectroVerticalWindow', ''),
            0x20050062: ('FL', '1', 'SpectroOffset', ''),
            0x20050063: ('FL', '1', 'SpectrumPitch', ''),
            0x20050064: ('CS', '1', 'VolumeSelection', ''),
            0x20050070: ('SS', '1', 'NumberMixesSpectro', ''),
            0x20050071: ('SQ', '1', 'SeriesSPMix', ''),
            0x20050072: ('SS', '1-2', 'SPMixTResolution', ''),
            0x20050073: ('SS', '1-2', 'SPMixKXResolution', ''),
            0x20050074: ('SS', '1-2', 'SPMixKYResolution', ''),
            0x20050075: ('SS', '1-2', 'SPMixFResolution', ''),
            0x20050076: ('SS', '1-2', 'SPMixXResolution', ''),
            0x20050077: ('SS', '1-2', 'SPMixYResolution', ''),
            0x20050078: ('SS', '1-2', 'SPMixNumberOfSpectraIntended', ''),
            0x20050079: ('SS', '1-2', 'SPMixNumberOfAverages', ''),
            0x20050080: ('SL', '1', 'NumberOfMFImageObjects', ''),
            0x20050081: ('IS', '1', 'ScanoGramSurveyNumberOfImages', ''),
            0x20050082: ('UL', '1', 'NumberOfProcedureCodes', ''),
            0x20050083: ('CS', '1-n', 'SortAttributes', ''),
            0x20050084: ('SS', '1', 'NumberOfSortAttributes', ''),
            0x20050085: ('CS', '1', 'ImageDisplayDirection', ''),
            0x20050086: ('CS', '1', 'InsetScanogram', ''),
            0x20050087: ('SS', '1', 'DisplayLayoutNumberOfColumns', ''),
            0x20050088: ('SS', '1', 'DisplayLayoutNumberOfRows', ''),
            0x20050089: ('SQ', '1', 'ViewingProtocol', ''),
            0x20050090: ('CS', '1', 'StackCoilFunction', ''),
            0x20050091: ('PN', '1', 'PatientNameJobInParams', ''),
            0x20050092: ('IS', '1', 'GeolinkID', ''),
            0x20050093: ('IS', '1', 'StationNumber', ''),
            0x20050094: ('CS', '1-n', 'ProcessingHistory', ''),
            0x20050095: ('ST', '1', 'ViewProcedureString', ''),
            0x20050096: ('CS', '1', 'FlowImagesPresent', ''),
            0x20050097: ('LO', '1', 'AnatomicRegionCodeValue', ''),
            0x20050098: ('CS', '1', 'MobiviewEnabled', ''),
            0x20050099: ('CS', '1', 'IViewBoldEnabled', '')
        },
        'Philips MR Imaging DD 005': {
            0x20050000: ('CS', '1', 'VolumeViewEnabled', ''),
            0x20050001: ('UL', '1', 'NumberOfStudyReference', ''),
            0x20050002: ('SQ', '1', 'SPSCode', ''),
            0x20050003: ('UL', '1', 'NumberOfSPSCodes', ''),
            0x20050004: ('SS', '1', 'MRDD005Private20051404SS', ''),
            0x20050006: ('SS', '1', 'NumberOfPSSpecificCharacterSets', ''),
            0x20050007: ('SS', '1', 'NumberOfSpecificCharacterSet', ''),
            0x20050009: ('DS', '1', 'RescaleInterceptOriginal', ''),
            0x2005000a: ('DS', '1', 'RescaleSlopeOriginal', ''),
            0x2005000b: ('LO', '1', 'RescaleTypeOriginal', ''),
            0x2005000e: ('SQ', '1', 'PrivateSharedSequence', ''),
            0x2005000f: ('SQ', '1', 'PrivatePerFrameSequence', ''),
            0x20050010: ('IS', '1', 'MFConvTreatSpectroMixNumber', ''),
            0x20050011: ('UI', '1', 'MFPrivateReferencedSOPInstanceUID', ''),
            0x20050012: ('IS', '1', 'DiffusionBValueNumber', ''),
            0x20050013: ('IS', '1', 'GradientOrientationNumber', ''),
            0x20050014: ('SL', '1', 'NumberOfDiffusionBValues', ''),
            0x20050015: ('SL', '1', 'NumberOfDiffusionGradientOrientations', ''),
            0x20050016: ('CS', '1', 'PlanMode', ''),
            0x20050017: ('FD', '3', 'DiffusionBMatrix', ''),
            0x20050018: ('CS', '3', 'OperatingModeType', ''),
            0x20050019: ('CS', '3', 'OperatingMode', ''),
            0x2005001a: ('CS', '1', 'FatSaturationTechnique', ''),
            0x2005001b: ('IS', '1', 'VersionNumberDeletedImages', ''),
            0x2005001c: ('IS', '1', 'VersionNumberDeletedSpectra', ''),
            0x2005001d: ('IS', '1', 'VersionNumberDeletedBlobsets', ''),
            0x2005001e: ('UL', '1', 'LUT1Offset', ''),
            0x2005001f: ('UL', '1', 'LUT1Range', ''),
            0x20050020: ('UL', '1', 'LUT1BeginColor', ''),
            0x20050021: ('UL', '1', 'LUT1EndColor', ''),
            0x20050022: ('UL', '1', 'LUT2Offset', ''),
            0x20050023: ('UL', '1', 'LUT2Range', ''),
            0x20050024: ('UL', '1', 'LUT2BeginColor', ''),
            0x20050025: ('UL', '1', 'LUT2EndColor', ''),
            0x20050026: ('CS', '1', 'ViewingHardcopyOnly', ''),
            0x20050027: ('CS', '1', 'MRDD005Private20050027CS', ''),
            0x20050028: ('SL', '1', 'NumberOfLabelTypes', ''),
            0x20050029: ('CS', '1', 'LabelType', ''),
            0x2005002a: ('CS', '1', 'ExamPrintStatus', ''),
            0x2005002b: ('CS', '1', 'ExamExportStatus', ''),
            0x2005002c: ('CS', '1', 'ExamStorageCommitStatus', ''),
            0x2005002d: ('CS', '1', 'ExamMediaWriteStatus', ''),
            0x2005002e: ('FL', '1', 'DBdt', ''),
            0x2005002f: ('FL', '1', 'ProtonSAR', ''),
            0x20050030: ('FL', '1', 'NonProtonSAR', ''),
            0x20050031: ('FL', '1', 'LocalSAR', ''),
            0x20050032: ('CS', '1', 'SafetyOverrideMode', ''),
            0x20050033: ('DT', '1', 'EVDVDJobInParamsDatetime', ''),
            0x20050034: ('DT', '1', 'DVDJobInParamsVolumeLabel', ''),
            0x20050035: ('CS', '1', 'SpectroExamcard', ''),
            0x20050036: ('UI', '1', 'ReferencedSeriesInstanceUID', ''),
            0x20050037: ('CS', '1', 'ColorLUTType', ''),
            0x20050038: ('LT', '1', 'MRDD005Private20050038LT', ''),
            0x20050039: ('LT', '1', 'MRDD005Private20050039LT', ''),
            0x2005003a: ('LT', '1', 'DataDictionaryContentsVersion', ''),
            0x2005003b: ('CS', '1', 'IsCoilSurvey', ''),
            0x2005003c: ('FL', '1', 'StackTablePosLong', ''),
            0x2005003d: ('FL', '1', 'StackTablePosLat', ''),
            0x2005003e: ('FL', '1', 'StackPosteriorCoilPos', ''),
            0x2005003f: ('CS', '1', 'AIMDLimitsApplied', ''),
            0x20050040: ('FL', '1', 'AIMDHeadSARLimit', ''),
            0x20050041: ('FL', '1', 'AIMDWholeBodySARLimit', ''),
            0x20050042: ('FL', '1', 'AIMDB1RMSLimit', ''),
            0x20050043: ('FL', '1', 'AIMDdbDtLimit', ''),
            0x20050044: ('IS', '1', 'TFEFactor', ''),
            0x20050045: ('CS', '1', 'AttenuationCorrection', ''),
            0x20050046: ('FL', '1', 'FWHMShim', ''),
            0x20050047: ('FL', '1', 'PowerOptimization', ''),
            0x20050048: ('FL', '1', 'CoilQ', ''),
            0x20050049: ('FL', '1', 'ReceiverGain', ''),
            0x2005004a: ('FL', '1', 'DataWindowDuration', ''),
            0x2005004b: ('FL', '1', 'MixingTime', ''),
            0x2005004c: ('FL', '1', 'FirstEchoTime', ''),
            0x2005004d: ('CS', '1', 'IsB0Series', ''),
            0x2005004e: ('CS', '1', 'IsB1Series', ''),
            0x2005004f: ('CS', '1', 'VolumeSelect', ''),
            0x20050050: ('SS', '1', 'NumberOfPatientOtherIDs', ''),
            0x20050051: ('IS', '1', 'OriginalSeriesNumber', ''),
            0x20050052: ('UI', '1', 'OriginalSeriesInstanceUID', ''),
            0x20050053: ('CS', '1', 'SplitSeriesJobParams', ''),
            0x20050054: ('SS', '1', 'PreferredDimensionForSplitting', ''),
            0x20050055: ('FD', '3', 'VelocityEncodingDirection', ''),
            0x20050056: ('SS', '1', 'ContrastBolusNumberOfInjections', ''),
            0x20050057: ('LT', '1', 'ContrastBolusAgentCode', ''),
            0x20050058: ('LT', '1', 'ContrastBolusAdminRouteCode', ''),
            0x20050059: ('DS', '1', 'ContrastBolusVolume', ''),
            0x2005005a: ('DS', '1', 'ContrastBolusIngredientConcentration', ''),
            0x2005005b: ('IS', '1', 'ContrastBolusDynamicNumber', ''),
            0x2005005c: ('SQ', '1', 'ContrastBolusSequence', ''),
            0x2005005d: ('IS', '1', 'ContrastBolusID', ''),
            0x20050060: ('CS', '1', 'LUTToRGBJobParams', ''),
            0x20050090: ('SQ', '1', 'OriginalVOILUTSequence', ''),
            0x20050091: ('SQ', '1', 'OriginalModalityLUTSequence', ''),
            0x20050092: ('FL', '1', 'SpecificEnergyDose', ''),
            0x20051492: ('FL', '1', 'Specific Energy Dose', '')
        },
        'Philips MR Imaging DD 006': {
            0x20050053: ('FL', '1', 'MREFrequency', ''),
            0x20050054: ('FL', '1', 'MREAmplitude', ''),
            0x20050055: ('FL', '1', 'MREMEGFrequency', ''),
            0x20050056: ('FL', '1', 'MREMEGPairs', ''),
            0x20050057: ('CS', '1', 'MREMEGDirection', ''),
            0x20050058: ('FL', '1', 'MREMEGAmplitude', ''),
            0x20050059: ('FL', '1', 'MRENumberOfPhaseDelays', ''),
            0x20050060: ('IS', '1', 'MRENumberOfMotionCycles', ''),
            0x20050061: ('FL', '1', 'MREMotionMEGPhaseDelay', ''),
            0x20050062: ('LT', '1', 'MREInversionAlgorithmVersion', ''),
            0x20050063: ('CS', '1', 'SagittalSliceOrder', ''),
            0x20050064: ('CS', '1', 'CoronalSliceOrder', ''),
            0x20050065: ('CS', '1', 'TransversalSliceOrder', ''),
            0x20050066: ('CS', '1', 'SeriesOrientation', ''),
            0x20050067: ('IS', '1', 'MRStackReverse', ''),
            0x20050068: ('IS', '1', 'MREPhaseDelayNumber', ''),
            0x20050071: ('IS', '1', 'NumberOfInversionDelays', ''),
            0x20050072: ('FL', '1', 'InversionDelayTime', ''),
            0x20050073: ('IS', '1', 'InversionDelayNumber', ''),
            0x20050074: ('DS', '1', 'MaxDBDT', ''),
            0x20050075: ('DS', '1', 'MaxSAR', ''),
            0x20050076: ('LT', '1', 'SARType', ''),
            0x20050078: ('CS', '1', 'MetalImplantStatus', ''),
            0x20050079: ('CS', '1-n', 'OrientationMirrorFlip', ''),
            0x20050081: ('CS', '1', 'SAROperationMode', ''),
            0x20050082: ('IS', '1', 'SpatialGradient', ''),
            0x20050083: ('LT', '1', 'AdditionalConstraints', ''),
            0x20050085: ('DS', '1', 'GradientSlewRate', ''),
            0x20050086: ('LT', '1', 'MRDD006Private20051586LT', ''),
            0x20050087: ('DS', '1', 'B1RMS', ''),
            0x20050092: ('SQ', '1', 'ContrastInformationSequence', ''),
            0x20051595: ('CS', '1', 'Diffusion2KDTI', ''),
            0x20051596: ('IS', '1', 'DiffusionOrder', ''),
            0x20051597: ('CS', '1', 'IsJEditingSeries', ''),
            0x20051598: ('SS', '1', 'MRSpectrumEditingType', ''),
            0x20051599: ('SL', '1', 'MRSeriesNrOfDiffOrder', '')
        }
    }

    for private_creator, private_dict in additional_private_dicts.items():
        add_private_dict_entries(private_creator, private_dict)


def update_unknown_vrs(dobj):
    """
    Use private dictionary to process tags in dataset with unknown VR.

    If dicom dataset has passed through an implicit encoding
    then the VRs of the private tags will have been lost and the tag values will remain
    the uninterpreted byte string and they will have a VR of 'UN'.
    This converts the tags according to the known VRs in the global private dictionary.
    Parameters
    ----------
    dobj: pydicom.Dataset
        dicom dataset to process (in place)
    """
    for item in dobj:
        tag = item.tag
        if tag.is_private and item.VR == 'UN':
            try:
                # Find the private creator section the tag belongs to
                private_creator_tag = Tag(tag.group, tag.element >> 8)
                if private_creator_tag not in dobj:
                    raise KeyError('No private creator found for tag %s' % tag)
                private_creator = dobj[private_creator_tag].value
                # Look up new element VR in private dictionary and change accordingly
                item.VR = private_dictionary_VR(tag, private_creator)
                # Convert value according to new VR
                if item.value:
                    if isinstance(converters[item.VR], tuple):
                        converter, number_format = converters[item.VR]
                    else:
                        converter, number_format = converters[item.VR], None
                    if item.VR == 'SQ':
                        item.value = convert_SQ(item.value, dobj.is_implicit_VR, dobj.is_little_endian, item.value)
                    elif item.VR in text_VRs or item.VR == 'PN':
                        item.value = converter(item.value)
                    else:
                        item.value = converter(item.value, dobj.is_little_endian, number_format)
            except (KeyError, ValueError, IOError):
                continue
        # Apply recursively to sequences (including ones newly recognised above)
        if item.VR == 'SQ':
            for seq_dobj in item.value:
                # Setting these attributes was previously needed for interpreting sequence datasets correctly.
                # It seems to be no longer required and setting these attributes now generates
                # deprecation warnings for removal in pydicom 4.
                #seq_dobj.read_encoding = None
                #seq_dobj.is_little_endian = dobj.is_little_endian
                #seq_dobj.is_implicit_VR = dobj.is_implicit_VR
                update_unknown_vrs(seq_dobj)


# NB Side effect on import.
augment_private_dictionaries()

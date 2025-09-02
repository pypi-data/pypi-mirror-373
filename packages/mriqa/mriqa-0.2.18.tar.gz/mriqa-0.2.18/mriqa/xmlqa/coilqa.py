# -*- coding: utf-8 -*-
"""coilqa.py: Routines for reading Siemens xml records for receiver Coil QA
"""
import shlex
import fnmatch
from glob import glob
from base64 import b64decode
from collections.abc import Sequence
import os
import dateutil
import datetime as dt

from lxml import etree
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# Minimum percentage we hope to exceed Siemens Spec by
MARGIN = 20
MINCOILSERNO = 50

# TODO: fix odd effects with font size changing depending on how subplots made
# TODO: fix suptitle hidden behind plot
# TODO: resolve remaining issues in uniquely identifying all coils currently on system
# TODO: filter out aborted or incomplete qa in coil_snr_history()
# TODO: table of dates of most recent valid QA results


def _params_from_xml(group, typedict=None):
    """
    Extract 'Parameter' fields from a specified 'Group' Tag.

    Parameters
    ----------
    group : xml tag
        group tag.
    typedict : dict
        optional elements types mapping

    Returns
    -------
    dict
        extracted parameters

    """
    if typedict is None:
        typedict = {}

    paramdict = {}
    parameters = group.findall('Parameter')
    for parameter in parameters:
        name = parameter.get('Name')
        value = parameter.text
        if name in typedict:
            value = typedict[name](value)
        paramdict[name] = value
    return paramdict


def image_and_roi(filename):
    """
    Image and ROI from 'Binary' XML file.

    This has a single <Binary> element with descriptive <Group> sub-elements
    'General' and 'ROI' along with a base64 encoded <Data> sub-element for
    the 16 bit image data.

    Parameters
    ----------
    filename : str
        Name of XML file with base64 image

    Returns
    -------
    tuple(numpy array, dictionary)
        Image array and ROI description

    """
    root = etree.parse(filename).getroot()

    GENERAL_TYPES = {'Columns': int, 'Rows': int}
    ROI_TYPES = {'Height': int, 'Type': str, 'Width': int, 'X': int, 'Y': int}

    for group in root.findall('Group'):
        if group.get('Name') == 'General':
            general_params = _params_from_xml(group, typedict=GENERAL_TYPES)
        elif group.get('Name') == 'ROI':
            roi_params = _params_from_xml(group, typedict=ROI_TYPES)

    nx, ny = general_params['Columns'], general_params['Rows']

    imagedata = root.find('Data')
    image = np.frombuffer(b64decode(imagedata.text), dtype=np.uint16).reshape((ny, nx))

    return image, roi_params


def plot_image_files(filenames, elements=None, title=None, figure=None):
    """
    Plot Images and ROIs from XML files.

    Parameters
    ----------
    filenames : list(str)
           XML filenames
    elements: Optional[list]
           Subset of coil elements to show
    title : Optional[str]
           Title of plot
    figure: Optional[matplotlib Figure instance]
           Existing figure to plot into

    """
    images_and_rois = [image_and_roi(filename) for filename in filenames]
    nimages = len(images_and_rois)
    ncols = min(5, nimages)
    nrows = int(np.ceil(float(nimages)/ncols))

    if elements is None:
        elements = ['%2d' % i for i in range(1, len(filenames)+1)]
    assert len(elements) >= nimages

    if figure is None:
        figure, axess = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols*2.5, nrows*2.5))
        if nrows == ncols == 1:
            axess = np.array([axess])
    else:
        # preexisting figure
        axess = np.array([[figure.add_subplot(nrows, ncols, j*ncols+i+1) for i in range(ncols)] for j in range(nrows)])

    for i, (image, roi) in enumerate(images_and_rois):
        ax = axess.ravel()[i]
        ax.imshow(image, cmap='gray')
        if roi['Type'] == 'Rectangle':
            x0, y0, dx, dy = [roi[k] for k in ['X', 'Y', 'Width', 'Height']]
            ax.add_patch(plt.Rectangle((x0, y0), dx, dy, fill=False, edgecolor="red"))
        ax.axis('off')
        label_str = elements[i] if len(elements[i]) < 18 else elements[i][:8] + '..' + elements[i][-8:]
        ax.text(20, 20, label_str, color='red')

    if nimages < nrows*ncols:
        for i in range(nimages, nrows*ncols):
            ax = axess.ravel()[i]
            ax.imshow(np.zeros_like(images_and_rois[0][0]), cmap='gray')
            ax.axis('off')

    figure.subplots_adjust(hspace=0.001, wspace=0.001)
    figure.tight_layout()
    figure.suptitle(title, fontsize=15)

    return


def _snr_results_by_element(root):
    """
    SNR results for each coil element.

    Parameters
    ----------
    root :  xml element tree
        root of xml tree.

    Returns
    -------
    dict
        Measured and reference SNR values indexed by coil element

    """
    snr_results = {}
    tables = root.findall('Table')
    numerics = root.findall('Numeric')

    snr_tables = [
        t for t in tables
        if t.get('ID').endswith(('Aspect0.EvaResultsSN', 'Aspect0.EvaResults'))
    ]
    for table in snr_tables:
        table_numerics = [n for n in numerics if n.get('RefTable') == table.get('ID') and n.get('ID').endswith('SN')]
        for numeric in table_numerics:
            value = numeric.find('Value')
            if value is not None:
                ref_table = numeric.get('RefTable')
                coil_element = ref_table.split('-')[3]
            else:
                coil_element = None

            range_ = numeric.find('Range')
            min_ = range_.get('Min') if range_ is not None else None

            if coil_element is not None:
                snr_results[coil_element] = float(value.text), float(min_)

    return dict(sorted([(k, v) for k, v in snr_results.items()], key=lambda kv: (len(kv[0]), kv[0])))


def _rois_by_element(root, qa_dir):
    """
    Information on ROIs for each coil element.

    Parameters
    ----------
    root :  xml element tree
        root of xml tree.
    qa_dir: Optional[str]
        directory under which Siemens QA logs stored

    Returns
    -------
    dict
        roi info and images indexed by coil element

    """
    rois = {}
    binaries = [b for b in root.findall('Binary') if b.get('ID').endswith('Aspect0.SignalScrolled')]
    # info_tables = [t for t in root.findall('Table') if t.get('ID').endswith('Aspect0.RoiInfo')]

    for binary in binaries:
        coil_element = binary.get('ID').split('-')[3]
        image_file = binary.get('RefData')
        rois[coil_element] = image_and_roi(os.path.join(qa_dir, image_file))
    return rois


def _image_files_by_element(root):
    """
    Image file names for each coil element.

    Parameters
    ----------
    root :  xml element tree
        root of xml tree.

    Returns
    -------
    dict
        image files indexed by coil element

    """
    rois = {}
    binaries = [b for b in root.findall('Binary') if b.get('ID').endswith('Aspect0.SignalScrolled')]
    for binary in binaries:
        coil_element = binary.get('ID').split('-')[3]
        image_file = binary.get('RefData')
        rois[coil_element] = image_file
    return rois


def coil_name(filename):
    """
    Name of coil name.

    Parameters
    ----------
    filename : str
        name of XML coil QA results file

    Returns
    -------
    str
        name of coil

    """
    root = etree.parse(filename).getroot()
    return dict(token.split(':') for token in shlex.split(root.get('Tags')))['Coil']


def siemens_system_serialno(filename):
    """
    Siemens syetem serial number.

    Parameters
    ----------
    filename : str
        name of XML coil QA results file

    Returns
    -------
    int
        scanner serial number

    """
    root = etree.parse(filename).getroot()
    return int(dict(token.split(':') for token in shlex.split(root.get('Tags')))['SystemSerialNumber'])


def siemens_coil_serialno(filename):
    """
    Siemens Coil serial number.

    Parameters
    ----------
    filename : str
        name of XML coil QA results file

    Returns
    -------
    int | None
        coil serial number if specified in file

    """
    root = etree.parse(filename).getroot()

    info_tables = [
        table for table in root.findall('Table')
        if table.get('ID').endswith('CoilInfo.Table')
    ]
    info_texts = [
        text for text in root.findall('Text')
        if text.get('ID') is not None and text.get('ID').endswith('SerialNumber')
    ]
    for table in info_tables:
        table_texts = [
            text for text in info_texts
            if text.get('RefTable') == table.get('ID')
        ]
        for text in table_texts:
            span = text.find('Span')
            if span is not None:
                return int(span.text)
    return None


def siemens_coil_partno(filename):
    """Siemens Coil part number.

    Parameters
    ----------
    filename : str
        name of XML coil QA results file

    Returns
    -------
    int | None
        coil part number if specified in file

    """
    root = etree.parse(filename).getroot()

    info_tables = [
        table for table in root.findall('Table')
        if table.get('ID').endswith('CoilInfo.Table')
    ]
    info_texts = [
        text for text in root.findall('Text')
        if text.get('ID') is not None and text.get('ID').endswith('PartNumber')
    ]
    for table in info_tables:
        table_texts = [
            text for text in info_texts
            if text.get('RefTable') == table.get('ID')
        ]
        for text in table_texts:
            span = text.find('Span')
            if span is not None:
                return int(span.text)
    return None


def coil_serialno(filename, digits=5):
    """
    Composite coil serial number.

    Obtained from a combination of the Siemens part and serial numbers.
    This is because, unfortunately, the serial numbers alone are not unique.
    Assume here that coil serial numbers are small numbers (at most 10 digits).

    Parameters
    ----------
    filename : str
        name of XML coil QA results file
    digits : Optional[int]
        maximum number of digits in siemens coil serial number

    Returns
    -------
    int | None
        coil xomposite part,serial number if specified in file

    """
    serial_no = siemens_coil_serialno(filename)
    if serial_no is None:
        return None

    part_no = siemens_coil_partno(filename)
    if part_no is None:
        return None

    assert serial_no < 10**digits
    return part_no * 10**digits + serial_no


def _time_stamp(path):
    """
    QA timestamp.

    Python timestamp string encoded in the filename. This is a bit brittle as
    it depends on the name rather than the contents of the file.

    Parameters
    ----------
    path : str
           path to XML file

    Returns
    -------
    datetime
        timestamp

    """
    # Encoding in file name is YYYYMMDD_hhmmss_ffffffZ ie UTC
    # We extract just the date part for now
    return dateutil.parser.parse(
        ' '.join(os.path.basename(path)[:23].split('_')[:2])
    )


def _coil_snr_values(root):
    """
    SNR values.

    The snr values extracted fom the <Numeric> tags with the appropriate ID.

    Parameters
    ----------
    root : xml context

    Returns
    -------
    dict
        snr values by coil name

    """
    '''
    snr = {}
    numerics = [numeric for numeric in root.findall('Numeric') if numeric.get('ID').endswith('SN')]
    for numeric in numerics:
        id_ =  numeric.get('ID')
        value = numeric.find('Value')
        if value is not None:
            coil_element = id_.split('.')[1].split('-')[-4]
            snr[coil_element] = float(value.text)
    return snr
    '''
    return dict([(k, v[0]) for k, v in _snr_results_by_element(root).items()])


def find_qa_results_file(coil, qa_dir='MrSeso/site/Reports/Workflows/QA', glob_pattern='*/SfpCoilCheckLocalCoils/*Z.xml', datebefore=None):
    """
    SNR results file for a coil specified by name or id.

    File must be uniquely specified both in terms of the coil and the date.
    If no date range is specified the most recent results file is returned.

    Parameters
    ----------
    coil : int or str
        coil serial no or coil name
    qa_dir: Optional[str]
        directory under which Siemens QA logs stored
    glob_pattern: Optional[str]
        rexexp for matching coil QA results xml file
    datebefore: Optional[datetime]
        if specified consider results only before specified date

    Returns
    -------
    str
        full path of qa results file

    """
    # get those corresponding to specified coil
    try:
        coil = int(coil)
    except ValueError:
        coils = coil_names(qa_dir=qa_dir, glob_pattern=glob_pattern)
        specified_coils = [k for (k, v) in coils.items() if v == coil]
        if len(specified_coils) < 1:
            raise ValueError('No QA data found for coil called %s - try specifing by coil id instead' % coil)
        if len(specified_coils) > 1:
            noserial_coils = [c for c in specified_coils if c < MINCOILSERNO]
            serial_coils = [c for c in specified_coils if c >= MINCOILSERNO]
            if len(noserial_coils) == 1:
                specified_coils = noserial_coils
            elif len(serial_coils) == 1:
                specified_coils = serial_coils
            else:
                raise ValueError('Coil %s ambiguous - try specifying by coil id instead' % coil)
        if specified_coils[0] >= MINCOILSERNO:
            files = [
                xmlfile for xmlfile in glob(os.path.join(qa_dir, glob_pattern))
                if coil_serialno(xmlfile) == specified_coils[0]
            ]
        else:
            # Dummy coilno implies no serialno found so select by name instead
            files = [
                xmlfile for xmlfile in glob(os.path.join(qa_dir, glob_pattern))
                if coil_name(xmlfile) == coil
            ]
    else:
        files = [
            xmlfile for xmlfile in glob(os.path.join(qa_dir, glob_pattern))
            if coil_serialno(xmlfile) == coil
        ]

    if not files:
        raise ValueError('No QA results found for coil %s' % coil)

    # date order sorted and filtered for timestamp before specified date
    timestamps = [dt.datetime.strptime(os.path.basename(f), '%Y%m%d_%H%M%S_%fZ.xml') for f in files]
    files, timestamps = zip(*sorted(zip(files, timestamps), key=lambda f_d: f_d[1]))
    if datebefore is None:
        datebefore = dt.datetime.now()
    files, _ = zip(*filter(lambda f_d: f_d[1] < datebefore, zip(files, timestamps)))

    if not files:
        raise ValueError('No QA results found for coil %s before %s' % (coil, str(datebefore)))

    return files[-1]


def coil_snr(coil, qa_dir='MrSeso/site/Reports/Workflows/QA', glob_pattern='*/SfpCoilCheckLocalCoils/*Z.xml', margin=MARGIN):
    """
    SNR table of (most recent) results for a coil specified by name of id.

    Parameters
    ----------
    coil : int or str
        coil id or coil name
    qa_dir: Optional[str]
        directory under which Siemens QA logs stored
    glob_pattern: Optional[str]
        rexexp for matching coil QA results xml file
    margin: Optional[numeric]
        percentage SNR above minimum considered marginal
    Returns
    -------
    pandas dataframe
        QA results, indexed by coil element

    """
    xmlfile = find_qa_results_file(coil, qa_dir=qa_dir, glob_pattern=glob_pattern)

    root = etree.parse(xmlfile).getroot()
    snr = _snr_results_by_element(root)
    df = pd.DataFrame(snr, ['Measured', 'Specification']).T
    df['Margin'] = ((df['Measured'] / df['Specification'] - 1) * 100).astype(np.int)
    df['OK'] = df['Margin'] >= margin

    # sort combined elements to end of dataframe
    df['Element'] = pd.Categorical(df.index, sorted(set(df.index), key=lambda x: (len(x), x)))
    df = df.sort_values(by='Element').drop('Element', axis=1)
    df.index.name = 'Element'
    return df


def plot_coil_images(coil, elements=None, qa_dir='MrSeso/site/Reports/Workflows/QA', glob_pattern='*/SfpCoilCheckLocalCoils/*Z.xml', figure=None):
    """
    Plot (most recent) Siemens Coil QA images as mosaic.

    Parameters
    ----------
    coil : int or str
        coil id or coil name
    elements : str or list
        glob pattern or explicit list of elements to display (default: all)
    qa_dir: Optional[str]
        directory under which Siemens QA logs stored
    glob_pattern: Optional[str]
        rexexp for matching coil QA image xml files
    figure: Optional[matplotlib Figure instance]
           Existing figure to plot into

    """
    xmlfile = find_qa_results_file(coil, qa_dir=qa_dir, glob_pattern=glob_pattern)

    basedir = os.path.split(xmlfile)[0]
    imfiles = _image_files_by_element(root=etree.parse(xmlfile).getroot())

    if elements is not None:
        if isinstance(elements, Sequence):
            if isinstance(elements, str):
                # treat as glob pattern
                elements = fnmatch.filter(imfiles.keys(), elements)
            imfiles = {k: imfiles[k] for k in elements}
            if not imfiles:
                raise ValueError('Coils %s does not have any elements matching %s' % (coil, elements))
        else:
            raise ValueError("The parameter 'elements', if specified, must be a string or a list")

    # sort combined element images to end
    sorted_keys = sorted(imfiles.keys(), key=lambda x: (len(x), x))
    image_pathnames = [os.path.join(basedir, imfiles[k]) for k in sorted_keys]
    plot_image_files(image_pathnames, elements=sorted_keys, title='%s' % str(coil), figure=figure)
    return


def coil_snr_history(coil, qa_dir='MrSeso/site/Reports/Workflows/QA', glob_pattern='*/SfpCoilCheckLocalCoils/*Z.xml'):
    """
    Historical table of SNR values for a coil specified by name of id.

    Parameters
    ----------
    coil : int or str
        coil id or coil name
    qa_dir: Optional[str]
        directory under which Siemens QA logs stored
    glob_pattern: Optional[str]
        rexexp for matching coil QA results xml files

    Returns
    -------
    pandas dataframe
        SNR values for each element, indexed by timestamp

    """
    try:
        coil = int(coil)
    except ValueError:
        coils = coil_names(qa_dir=qa_dir, glob_pattern=glob_pattern)
        specified_coils = [k for (k, v) in coils.items() if v == coil]

        if len(specified_coils) < 1:
            raise ValueError('No QA data found for coil called %s - try specifing by coil id instead' % coil)
        if len(specified_coils) > 1:
            noserial_coils = [c for c in specified_coils if c < MINCOILSERNO]
            serial_coils = [c for c in specified_coils if c >= MINCOILSERNO]
            if len(noserial_coils) == 1:
                specified_coils = noserial_coils
            elif len(serial_coils) == 1:
                specified_coils = serial_coils
            else:
                raise ValueError('Coil %s ambiguous - try specifying by coil id instead' % coil)

        if specified_coils[0] >= MINCOILSERNO:
            files = [
                xmlfile for xmlfile in glob(os.path.join(qa_dir, glob_pattern))
                if coil_serialno(xmlfile) == specified_coils[0]
            ]
        else:
            # Dummy coilno implies no serialno found so select by name instead
            files = [
                xmlfile for xmlfile in glob(os.path.join(qa_dir, glob_pattern))
                if coil_name(xmlfile) == coil
            ]
    else:
        files = [
            xmlfile for xmlfile in glob(os.path.join(qa_dir, glob_pattern))
            if coil_serialno(xmlfile) == coil
        ]

    if not files:
        raise ValueError('No QA results found for coil %s' % coil)

    results = []
    timestamps = []
    for f in files:
        root = etree.parse(f).getroot()
        results.append(_coil_snr_values(root))
        # date parsed from filename
        timestamps.append(_time_stamp(f))
    timestamps, results = zip(*sorted(zip(timestamps, results), key=lambda x: x[0]))
    # beware zip converts to a tuple which DataFrame doesn't like
    df = pd.DataFrame(list(results), index=list(timestamps))
    df = df.reindex_axis(sorted(df.columns, key=lambda x: (len(x), x)), axis=1)
    df.index.name = 'Date'
    df.columns.name = 'Element'
    return df


def coil_names(qa_dir='MrSeso/site/Reports/Workflows/QA', glob_pattern='*/SfpCoilCheckLocalCoils/*Z.xml', max_age_days=None):
    """
    Coils present in QA directory.

    Handle files (old style) where the coil serial number is missing by
    substituting a dummy (small) serial number.
    Coils are identified where possible by the (extended) serial number.

    Parameters
    ----------
    qa_dir: Optional[str]
        directory under which Siemens QA logs stored
    glob_pattern: Optional[str]
        rexexp for matching coil QA results xml files
    max_age_days: Optional[int]
        discard results older than given number of days before present
    Returns
    -------
    dict
        coil names indexed by coil id (extended serial number)

    """
    dummy_serno = MINCOILSERNO - 1
    dummied = []
    names = {}
    for xmlfile in glob(os.path.join(qa_dir, glob_pattern)):
        name = coil_name(xmlfile)
        serial_no = coil_serialno(xmlfile)
        qa_date = _time_stamp(xmlfile)

        if max_age_days is not None and (dt.datetime.now() - qa_date) > dt.timedelta(days=max_age_days):
            continue
        if serial_no is None:
            if name not in dummied:
                dummied.append(name)
                serial_no = dummy_serno
                dummy_serno -= 1
                names[serial_no] = name
        else:
            names[serial_no] = name

    # if we have a real serial no for a coil then remove any dummy ones arising from bad records
    reversed_names = {}
    for k, v in names.items():
        reversed_names.setdefault(v, []).append(k)

    clean_names = {}
    for name, serialnos in reversed_names.items():
        if any(n > 1000 for n in serialnos):
            serialnos = [n for n in serialnos if n > 1000]
        for n in serialnos:
            clean_names[n] = name

    return dict(sorted(clean_names.items()))

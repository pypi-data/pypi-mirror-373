# mriqa

This is a python package for the analysis of MRI QA images.

It currently depends on the auxiliary packages [dcmfetch](https://bitbucket.org/rtrhd/dcmfetch) and [dcmextras](https://bitbucket.org/rtrhd/dcmextras) as well as the python DICOM package [pydicom](https://github.com/pydicom/pydicom). Images are generally obtained (using dcmfetch) via a DICOM connection to a PACS that uses [dcm4che3](https://github.com/dcm4che/dcm4che) for the network transport or the [DICOM REST API](https://www.dicomstandard.org/dicomweb/restful-structure/) as provided by servers such as [Orthanc](https://www.orthanc-server.com/), but images can also be read directly from local storage using pydicom.

There are currently reports for SNR, image uniformity, geometric distortion and scale, slice profile, mtf, ghosting, single voxel spectroscopy (Siemens only), long term stability (fBIRN), background phase offset in PC flow, and ADC calibration with the NIST diffusion phantom.

The geometric distortion, slice profile and mtf reports are tested primarily with images of the Philips PIQT phantom, but they can also be used with images of the Eurospin TO2/TO4 phantoms and the standard size ACR phantom.

The reports produce [matplotlib](https://matplotlib.org/) plots and return [pandas](https://pandas.pydata.org/) dataframes of the results. They are intended to be used from within a [Jupyter](https://jupyter.org/) notebook.


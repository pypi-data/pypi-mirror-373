import os
import pydicom
from pydicom.tag import Tag
from collections import defaultdict

from dicom_sequence_classifier.Model.DICOMMetaData import DicomMetadata

def load_dicom_series(directory):
    series_dict = defaultdict(list)
    for root, _, files in os.walk(directory):
        for f in files:
            if f.lower().endswith(".dcm"):
                try:
                    path = os.path.join(root, f)
                    dcm = pydicom.dcmread(path, stop_before_pixels=True)
                    series_uid = getattr(dcm, "SeriesInstanceUID", None)
                    if series_uid:
                        series_dict[series_uid].append(dcm)
                except Exception as e:
                    print(f"Errore con file {f}: {e}")
    return series_dict

def load_dicom_file(file):
    dcm = pydicom.dcmread(file, stop_before_pixels=True)
    return dcm

def extract_metadata(dcm) -> DicomMetadata:
    def safe_get_tag(tag):
        return getattr(dcm, tag, None)
    
    def safe_get_code(first_arg, second_arg):
        tag = dcm.get(Tag(first_arg, second_arg))
        if tag is None:
            return None
        return tag.value

    return DicomMetadata(
        SeriesDescription=safe_get_tag("SeriesDescription"),
        ProtocolName=safe_get_tag("ProtocolName"),
        Modality=safe_get_tag("Modality"),
        EchoTime=safe_get_tag("EchoTime"),
        RepetitionTime=safe_get_tag("RepetitionTime"),
        FlipAngle=safe_get_tag("FlipAngle"),
        ScanningSequence=safe_get_tag("ScanningSequence"),
        SequenceName=safe_get_tag("SequenceName"),
        SequenceVariant=safe_get_tag("SequenceVariant"),
        InversionTime=safe_get_tag("InversionTime"),
        EchoTrainLength=safe_get_tag("EchoTrainLength"),
        ImageType=safe_get_tag("ImageType"),
        SliceThickness=safe_get_tag("SliceThickness"),
        Manufacturer=safe_get_tag("Manufacturer"),
        ManufacturerModelName=safe_get_tag("ManufacturerModelName"),
        MRAcquisitionType=safe_get_tag("MRAcquisitionType"),
        GEImageTag = safe_get_code(0x0019, 0x109C),
        VelocityEncodingDirection = safe_get_code(0x0018, 0x9090),
        GEDiffusionDirections = safe_get_code(0x0021,0x105A),
        PhilipsDiffusionDirections = safe_get_code(0x2005,0x1415)
    )
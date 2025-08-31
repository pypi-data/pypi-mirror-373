from dicom_sequence_classifier.Model.DICOMMetaData import DicomMetadata

def is_mr(meta: DicomMetadata) -> bool:
    modality = (meta.Modality or "").lower()
    return modality == "mr"

def is_primary(meta: DicomMetadata) -> bool:
    image_type = meta.ImageType
    return "ORIGINAL" in image_type and "PRIMARY" in image_type

def is_3d(meta: DicomMetadata) -> bool:
    mr_acquisition_type = (meta.MRAcquisitionType or "").lower()
    return mr_acquisition_type == "3d"

def is_inversion_recovery(meta: DicomMetadata) -> bool:
    scanning_sequence = (meta.ScanningSequence or "")
    inversion_time = (meta.InversionTime or 0)
    
    # Turbo Spin Echo Flair can be
    # - IR (GE)
    # - SE (Siemens)
    # - IR/SE (Philips)
    # All have Inversion Time > 0
    return (scanning_sequence == "IR" or "IR" in scanning_sequence) or inversion_time > 0 # maybe scanning_sequence useless?

def is_gradient_echo(meta: DicomMetadata) -> bool:
    scanning_sequence = (meta.ScanningSequence or "")
    return scanning_sequence == "GR" or "GR" in scanning_sequence

def is_3dflair_ge(meta: DicomMetadata) -> bool:
    ge_image_tag = (meta.GEImageTag or "")
    return ge_image_tag == "CubeT2flair"

def is_MPRage_ge(meta: DicomMetadata) -> bool:
    ge_image_tag = (meta.GEImageTag or "")
    return ge_image_tag == "MP-RAGE"

def is_phasecontrast_ge(meta: DicomMetadata) -> bool:
    ge_image_tag = (meta.GEImageTag or "")
    return ge_image_tag == "Inh-Vel"

def is_phasecontrast_philips(meta: DicomMetadata) -> bool:
    velocity_encoding_direction = (meta.VelocityEncodingDirection or [])
    return len(velocity_encoding_direction) > 0 and velocity_encoding_direction[0] > 0

def is_dti_ge(meta: DicomMetadata) -> bool:
    diffusion_direction = (meta.GEDiffusionDirections or None)
    return diffusion_direction is not None and diffusion_direction > 10

def is_dti_philips(meta: DicomMetadata) -> bool:
    diffusion_direction = (meta.PhilipsDiffusionDirections or None)
    return diffusion_direction is not None and diffusion_direction > 10

def is_flair(meta: DicomMetadata) -> bool:
    if is_3dflair_ge(meta):
        return True
    
    if not is_inversion_recovery(meta):
        return False
    
    if meta.InversionTime and meta.InversionTime > 1550 and \
           meta.RepetitionTime and meta.RepetitionTime > 3500:
        return True
    
    return False

def is_2dt2(meta: DicomMetadata) -> bool:
    if is_3d(meta):
        return False
    
    if is_gradient_echo(meta):
        return False
    
    if is_inversion_recovery(meta):
        return False
    
    if meta.EchoTime > 60 and meta.RepetitionTime > 2000:
        return True
    
    return False

def is_3dt1(meta: DicomMetadata) -> bool:
    if is_MPRage_ge(meta):
        return True
    
    if not is_3d(meta):
        return False
    
    if is_inversion_recovery(meta):
        if meta.InversionTime > 600 and meta.InversionTime < 950 and meta.RepetitionTime > 1500: # MPRage
            return True
        else:
            return False
    
    if not is_gradient_echo(meta):
        return False # we don't want 3dt1 turbo spin echo
    
    if (meta.EchoTime or 0) < 10 and (meta.RepetitionTime or 0) < 25 and (meta.FlipAngle or 0) >= 8:
        return True
    
    return False
    
    
def is_venous(meta: DicomMetadata) -> bool:
    
    if not is_3d(meta):
        return False
    
    if is_phasecontrast_ge(meta) or is_phasecontrast_philips(meta):
        return True
    # Phase Contrast check for Siemens missing due to unknown metadata to check
    
    return False


def is_dti(meta: DicomMetadata) -> bool:
    
    if is_dti_ge(meta) or is_dti_philips(meta):
        return True
    # DTI check for Siemens missing due to unknown metadata to check

    return False

def is_pet(meta: DicomMetadata) -> bool:
    
    if is_primary(meta) and meta.Modality == "PT":
        return True
    
    return False
    
def classify_dicom(meta: DicomMetadata) -> str:
    
    if not is_mr(meta):
        return "NOT MR"
    
    if is_flair(meta):
        if is_3d(meta):
            return "flair3d"
        else:
            return "flair2d"
    
    if is_venous(meta):
        return "venous"
    
    if is_dti(meta):
        return "dti"
    
    if is_pet(meta):
        return "pet"
    
    if is_2dt2(meta):
        return "t2_cor"
    
    if is_3dt1(meta):
        return "t13d"
    
    return "UNKNOWN"
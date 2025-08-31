from dataclasses import dataclass
from typing import Optional, Union, List

@dataclass
class DicomMetadata:
    # Main fields
    SeriesDescription: Optional[str]
    ProtocolName: Optional[str]
    Modality: Optional[str]
    EchoTime: Optional[float]
    RepetitionTime: Optional[float]
    FlipAngle: Optional[float]

    # Imaging sequence
    ScanningSequence: Optional[Union[str, List[str]]]
    SequenceName: Optional[str]
    SequenceVariant: Optional[str]

    # Acquisition parameters
    InversionTime: Optional[float]
    EchoTrainLength: Optional[int]
    VelocityEncodingDirection: Optional[List[float]]
    GEDiffusionDirections: Optional[int]
    PhilipsDiffusionDirections: Optional[int]

    # Image type / reconstruction
    ImageType: Optional[List[str]]
    SliceThickness: Optional[float]
    MRAcquisitionType: Optional[str] # 3D or 2D acquisition
    GEImageTag: Optional[str] # Custom GE image tag

    # Manufacturer-specific
    Manufacturer: Optional[str]
    ManufacturerModelName: Optional[str]
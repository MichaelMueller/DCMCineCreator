import os, sys
import datetime, uuid, re
from typing import Optional
from types import SimpleNamespace
import argparse
import inspect
from typing import Callable, List, get_type_hints, Annotated, get_origin, get_args
# pip
import cv2
import pydicom
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import generate_uid
from pydicom.encaps import encapsulate
from pydicom.datadict import tag_for_keyword


def generate_random_alphanumeric_uuid():
    random_uuid = uuid.uuid4()    
    uuid_str = str(random_uuid)
    alphanumeric_uuid = re.sub(r'[^a-zA-Z0-9]', '', uuid_str)    
    return alphanumeric_uuid[:10]


def resize_keep_aspect_ratio(image, width):
    ratio = width / image.shape[1]    
    height = int(image.shape[0] * ratio)
    resized_image = cv2.resize(image, (width, height))    
    return resized_image

def create_series(frame_interval:int, patient_id:Optional[str] = None, 
                  patient_name:Optional[str] = None,
                  study_description:Optional[str] = None,
                  series_description:Optional[str] = None):    
    series = SimpleNamespace()
    now = datetime.datetime.now()
    
    # patient    
    series.PatientName = "Unknown" if patient_name is None else patient_name
    series.PatientID = generate_random_alphanumeric_uuid() if patient_id is None else patient_id
    series.PatientBirthDate = now.strftime("%Y%m%d")
    series.PatientSex = ""
    
    # study
    series.StudyInstanceUID = generate_uid()
    series.StudyDate = now.strftime("%Y%m%d")    
    series.StudyTime = now.strftime("%H%M%S.%f") # Format the time as HHMMSS.FFFFFF
    series.ReferringPhysicianName = ""
    series.AccessionNumber = generate_random_alphanumeric_uuid()
    series.Modality = 'OT'  # Other
    series.StudyID = generate_random_alphanumeric_uuid()
    series.StudyDescription = study_description if study_description != None else ""
    
    # series
    series.SeriesInstanceUID = generate_uid()
    series.FrameTime = int(round( frame_interval ))
    series.SeriesDate = now.strftime("%Y%m%d")    
    series.SeriesTime = now.strftime("%H%M%S.%f")
    series.SeriesNumber = '1'
    series.SeriesDescription = series_description if series_description != None else ""
    
    # other?
    series.Laterality = ""
    series.PatientOrientation = ""
    series.ConversionType = "DV"
    return series

def create_dicom_from_frame(out_dir, frame, frame_number, series:SimpleNamespace, jpeg_quality=80, max_width:Optional[int]=None):
    
    # create compressed pixel data    
    if max_width != None:
        frame = resize_keep_aspect_ratio(frame, max_width)
    _, compressed_image = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
    compressed_image_bytes = compressed_image.tobytes()
    encapsulated_pixel_data = encapsulate([compressed_image_bytes])
    
    # create some mandatory metadata for the DICOM file
    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.SecondaryCaptureImageStorage #pydicom.uid.VideoPhotographicImageStorage ???
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = pydicom.uid.JPEGBaseline8Bit
    file_meta.ImplementationClassUID = generate_uid()

    # Main Dataset
    ds = Dataset()
    ds.file_meta = file_meta
    ds.is_little_endian = True
    ds.is_implicit_VR = False
    
    # copy series infos
    for key, value in vars(series).items():
        #tag = tag_for_keyword(key)
        #ds[tag] = value
        setattr(ds, key, value)
    
    # image / instance specific
    ds.SOPInstanceUID = generate_uid()
    ds.SOPClassUID = pydicom.uid.SecondaryCaptureImageStorage    
    ds.InstanceNumber = str(frame_number + 1)

    # Set additional tags required for the image
    ds.PixelData = encapsulated_pixel_data
    ds.SamplesPerPixel = 3
    ds.PhotometricInterpretation = "YBR_FULL_422"
    ds.PlanarConfiguration = 0
    ds.Rows, ds.Columns = frame.shape[:2]
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.HighBit = 7
    ds.PixelRepresentation = 0

    # Save DICOM file
    dir = out_dir
    os.makedirs(dir, exist_ok=True)
    fname = f"{dir}\\frame_{frame_number}.dcm"
    print(f'writing {fname}')
    ds.save_as(fname, write_like_original=False)
    
def create_argparse_instance( func: Callable):

    func_name = func.__name__
    func_help = func.__doc__ if func.__doc__ else "No description available."
    parser = argparse.ArgumentParser( prog=func_name, description=func_help )
    parameters = inspect.signature(func).parameters

    for param_name, param in parameters.items():
        param_type = param.annotation#type_hints.get(param_name, str)
        if get_origin(param_type) is Annotated:
            param_type, metadata = get_args(param_type)
            param_help = metadata.get("help", "")
        else:
            param_help = ""
        
        if param.default is inspect.Parameter.empty:
            parser.add_argument(param_name, type=param_type, help=param_help)
        else:
            parser.add_argument(f"--{param_name}", type=param_type, default=param.default, help=param_help)

    return parser

def video_2_dicom( video_path:Annotated[str, {"help": "Path to the video file"}], 
                   out_dir:Annotated[str, {"help": "The directory where the DICOM files will be created"}] = None,
                   quality:Annotated[int, {"help": "JPEG Quality"}]=80,
                   width:Annotated[int, {"help": "Width of the frames. None for same width"}]=None,
                   patient_id:Annotated[str, {"help": "DICOM PatientID"}] = None, 
                   patient_name:Annotated[str, {"help": "DICOM PatientName"}] = None,
                   study_description:Annotated[str, {"help": "DICOM StudyDescription"}] = None,
                   series_description:Annotated[str, {"help": "DICOM SeriesDescription"}] = None ):    
    
    """ Create a DICOM Series from a video """
    cap = cv2.VideoCapture(video_path)
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    num_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    frame_interval = 1000 / frame_rate  # Frame interval in millisecond
    print(f'starting conversion of file {video_path}, frame_rate: {frame_rate}, num frames: {num_frames}')
    
    study_description = os.path.basename( video_path ) if study_description == None else study_description
    series_description = os.path.basename( video_path ) if series_description == None else series_description
    series = create_series( frame_interval=frame_interval, patient_id=patient_id, patient_name=patient_name, study_description=study_description, series_description=series_description )
    
    frame_number = 0
    while True:
        frame_grabbed, frame = cap.read()        
        if not frame_grabbed:
            break
        if out_dir == None:
            out_dir = os.path.basename( video_path ).replace(".", "_")
        create_dicom_from_frame(out_dir, frame, frame_number, series, jpeg_quality=quality, max_width=width)
        frame_number += 1
        
    print("Conversion completed.")
    cap.release()

if __name__ == "__main__":
    parser = create_argparse_instance(video_2_dicom)
    args = parser.parse_args()
    
    video_2_dicom( **args.__dict__ )
    sys.exit(0)
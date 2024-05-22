# DCMCineCreator

Creates a DICOM Series from arbitrary video files.
As the video will be dumped as single jpeg files, disk consumption will be much higher.
However the video will be visible in most DICOM viewers.

# Usage
Install in a python environment (py>3.10) with requirements.txt

Use _python create_bouncing_ball_video.py_ to create a bouncing ball video.

Use _python video_2_dicom.py bouncing_ball.mp4_.
You will find the invidual frames in the folder "bouncing_ball_mp4".

Further Parameters:
```
positional arguments:
  video_path            Path to the video file

options:
  -h, --help            show this help message and exit
  --out_dir OUT_DIR     The directory where the DICOM files will be created
  --quality QUALITY     JPEG Quality
  --width WIDTH         Width of the frames. None for same width
  --patient_id PATIENT_ID
                        DICOM PatientID
  --patient_name PATIENT_NAME
                        DICOM PatientName
  --study_description STUDY_DESCRIPTION
                        DICOM StudyDescription
  --series_description SERIES_DESCRIPTION
                        DICOM SeriesDescription    
```
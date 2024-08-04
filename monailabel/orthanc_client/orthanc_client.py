import logging
import pydicom

from io import BytesIO
from requests.auth import HTTPBasicAuth
from pydicom.uid import generate_uid
from pydicom.dataset import Dataset
from dicomweb_client.api import DICOMwebClient
from dicomweb_client.session_utils import create_session_from_auth

logger = logging.getLogger(__name__)

ORTHANC_SERVER = "http://localhost:8042/dicom-web"

auth = HTTPBasicAuth('admin', 'admin')
session = create_session_from_auth(auth)

class DICOMWebAPI():
    def __init__(
        self,
    ):
        self.client_web = self._init_dicomweb_client()

    def _init_dicomweb_client(self) -> DICOMwebClient:
        logger.info(f"Using DICOM WEB API: {ORTHANC_SERVER}")

        dw_client = DICOMwebClient(
            url=ORTHANC_SERVER,
            session=session
        )

        return dw_client
    
    def search_for_studies(self):
        # studies = self.client_web.search_for_studies()
        try:
            studies = self.client_web.search_for_studies()
            if studies:
                print("List of studies:")
                for study in studies:
                    print(f"Study Instance UID: {study['0020000D']['Value'][0]}")
                    print(f"Study Date: {study.get('00080020', {'Value': ['N/A']})['Value'][0]}")
                    print(f"Study Description: {study.get('00081030', {'Value': ['N/A']})['Value'][0]}")
                    print("---")
            else:
                print("No studies found.")
        except Exception as e:
            print(f"Failed to query studies: {e}")

        return studies
    
    def search_for_instances(self):
        instances = self.client_web.search_for_instances()

        return instances
    
    async def store_instances(self, files):
        datasets = list()
        try:
            for f in files:
                logger.info(f"Using files type: {f}")
                # Read the uploaded DICOM file
                dicom_data = await f.read()
                dicom_data_io = BytesIO(dicom_data)

                dicom_dataset = pydicom.dcmread(dicom_data_io)
                
                # Modify DICOM attributes if necessary (e.g., generate new UIDs)
                # new_study_uid = generate_uid()
                # new_series_uid = generate_uid()
                # new_sop_uid = generate_uid()

                # dicom_dataset.StudyInstanceUID = new_study_uid
                # dicom_dataset.SeriesInstanceUID = new_series_uid
                # dicom_dataset.SOPInstanceUID = new_sop_uid
                # logger.info(f"dicom_dataset.StudyInstanceUID: {dicom_dataset.StudyInstanceUID}")
                # logger.info(f"dicom_dataset.SeriesInstanceUID: {dicom_dataset.SeriesInstanceUID}")
                # logger.info(f"dicom_dataset.SOPInstanceUID: {dicom_dataset.SOPInstanceUID}")


                # dicom_dataset.PatientName = "Gen a new name"
                # dicom_dataset.StudyDate = "2024-8-4"

                # print(f"Patient Name: {dicom_dataset.PatientName}")
                # print(f"Patient ID: {dicom_dataset.PatientID}")
                # print(f"Modality: {dicom_dataset.Modality}")
                # print(f"Study Date: {dicom_dataset.StudyDate}")
                # print(f"Study Description: {dicom_dataset.StudyDescription}")
                # print(f"Study Instance UID: {dicom_dataset.StudyInstanceUID}")
                # print(f"Series Instance UID: {dicom_dataset.SeriesInstanceUID}")
                # print(f"SOP Instance UID: {dicom_dataset.SOPInstanceUID}")
                # logger.info(f"Using aloooo: {dicom_dataset}")

                datasets.append(dicom_dataset)
            
            
            instances = self.client_web.store_instances(datasets)

        except Exception as e:
            logger.info(f"Using error: {e}")
            raise e

        return instances
    
    def retrieve_study_metadata(self, study_metadata):
        metadata = self.client_web.retrieve_study_metadata(study_instance_uid=study_metadata)
        metadata_datasets = [Dataset.from_json(ds) for ds in metadata]

        return metadata_datasets
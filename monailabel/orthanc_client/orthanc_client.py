import logging
import pydicom

from io import BytesIO
from pydicom.uid import generate_uid
from pydicom.dataset import Dataset
from dicomweb_client import DICOMwebClient

logger = logging.getLogger(__name__)

ORTHANC_SERVER = "http://localhost:8042/dicom-web"

class DICOMWebAPI():
    def __init__(
        self,
    ):
        self.client = self._init_dicomweb_client()

    def _init_dicomweb_client(self) -> DICOMwebClient:
        logger.info(f"Using DICOM WEB API: {ORTHANC_SERVER}")

        dw_client = DICOMwebClient(
            url=ORTHANC_SERVER,
        )

        return dw_client
    
    def search_for_studies(self):
        studies = self.client.search_for_studies()

        return studies
    
    async def store_instances(self, files):
        datasets = list()
        for f in files:
            try:
                logger.info(f"Using files type: {f}")
                # Read the uploaded DICOM file
                dicom_data = await f.read()

                dicom_data_io = BytesIO(dicom_data)

                dicom_dataset = pydicom.dcmread(dicom_data_io)

                # Modify DICOM attributes if necessary (e.g., generate new UIDs)
                new_study_uid = generate_uid()
                new_series_uid = generate_uid()
                new_sop_uid = generate_uid()

                dicom_dataset.StudyInstanceUID = new_study_uid
                dicom_dataset.SeriesInstanceUID = new_series_uid
                dicom_dataset.SOPInstanceUID = new_sop_uid

                datasets.append(dicom_dataset)
            
            except Exception as e:
                logger.info(f"Using error: {e}")
                raise e

        instances = self.client.store_instances(datasets)

        return instances
    
    def retrieve_study_metadata(self, study_metadata):
        metadata = self.client.retrieve_study_metadata(study_instance_uid=study_metadata)
        metadata_datasets = [Dataset.from_json(ds) for ds in metadata]

        return metadata_datasets
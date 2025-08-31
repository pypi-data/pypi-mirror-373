from bson import ObjectId

from lgt_jobs.lgt_data.models.base import BaseModel


class CloudFileModel(BaseModel):
    blob_path: str
    public_url: str
    file_name: str

    def __init__(self, blob_path: str, public_url: str, file_name: str):
        super().__init__()
        if not self.id:
            self.id = str(ObjectId())
        self.blob_path = blob_path
        self.public_url = public_url
        self.file_name = file_name
        
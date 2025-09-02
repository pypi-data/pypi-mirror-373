from azure.storage.blob import BlobServiceClient

class AzureBlobService:
    def __init__(self, account_name, container_name, sas_token):
        self.account_name = account_name
        self.container_name = container_name
        self.sas_token = sas_token
        self.create_container_client()
        
    def create_container_client(self):
        connection_string = f"BlobEndpoint=https://{self.account_name}.blob.core.windows.net/;SharedAccessSignature={self.sas_token}"
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = blob_service_client.get_container_client(self.container_name)

    def read_blob(self, path):
        data = self.container_client.download_blob(path).readall()
        return data

    def list_blobs(self, directory_name):
        blobs = self.container_client.list_blobs(name_starts_with=directory_name)
        return blobs
    
    def upload_blob(self, path, data, overwrite=True):
        return self.container_client.upload_blob(path, data, overwrite=overwrite)

    def delete_blob(self, path):
        return self.container_client.delete_blob(path)
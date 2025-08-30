from azure.identity import DefaultAzureCredential
from datalakesurfer.utils.customcredentials import CustomTokenCredential

def get_credential(token: str, expires_on: int):
    if token:
        return CustomTokenCredential(token=token, expires_on=expires_on)
    return DefaultAzureCredential()

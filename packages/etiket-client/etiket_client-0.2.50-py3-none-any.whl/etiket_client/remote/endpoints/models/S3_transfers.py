from pydantic import BaseModel

from etiket_client.remote.endpoints.models.scope import ScopeRead
from etiket_client.remote.endpoints.models.types import S3ScopeTransferStatus, S3FileTransferStatus
from etiket_client.remote.endpoints.models.S3 import S3BucketRead

class S3TransferStatus(BaseModel):
    scope_transfer_id : int
    scope : ScopeRead
    bucket : S3BucketRead
    status : S3ScopeTransferStatus
    bytes_transferred : int
    total_bytes : int

class S3FileTransfer(BaseModel):
    file_id : int
    scope_transfer_id : int
    transfer_id : int
    file_size : int
    bucket_src_id : int
    bucket_dst_id : int
    s3_key : str
    status : S3FileTransferStatus
    delete_on_completion : bool
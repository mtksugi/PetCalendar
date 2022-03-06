from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    location = 'media'  # mediaのurlをstaticと分けるには、ここで指定するしかない. settings.AWS_LOCATIONはS3Boto3Storage/S3Boto3StaticStorageのどちらにも効いてしまうから.
    file_overwrite = False

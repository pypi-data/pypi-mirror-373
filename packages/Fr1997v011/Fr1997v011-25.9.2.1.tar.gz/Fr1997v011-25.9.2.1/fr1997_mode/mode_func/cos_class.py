from qcloud_cos import CosConfig  # 腾讯云cos  pip install -U cos-python-sdk-v5
from qcloud_cos import CosS3Client
from .base_class import *


# cos
class Cos:

    def __init__(self, **kwargs):
        # 选择服务器
        server_select = kwargs.get("server_select", 'jike')
        if server_select == 'personal':
            self.secret_id = config_dict['cos']['gaoyang']['secret_id']
            self.secret_key = config_dict['cos']['gaoyang']['secret_key']
        else:
            self.secret_id = config_dict['cos']['secret_id']
            self.secret_key = config_dict['cos']['secret_key']
        self.region = config_dict['cos']['region']
        self.scheme = config_dict['cos']['scheme']
        self.config = CosConfig(Region=self.region,
                                SecretId=self.secret_id,
                                SecretKey=self.secret_key,
                                Scheme=self.scheme)
        self.client = CosS3Client(self.config)

    # 创建存储桶
    def create_bucket(self, bucket_name):
        response = self.client.create_bucket(
            Bucket=bucket_name
        )

    # 查看文件是否纯在
    def file_exist(self, Bucket, path, file):
        try:
            response = self.client.head_object(
                Bucket=Bucket,
                Key=f'{path}{file}',  # video/qq.png
            )
            return response
        except:
            return False

    # 上传文件
    def upload_file(self, Bucket, loc_path, path, file):
        try:
            response = self.client.upload_file(
                Bucket=Bucket,
                LocalFilePath=loc_path,  # 本地文件的路径 'qq.png'
                Key=f'{path}{file}',  # 上传到桶之后的文件名  'video/qq.png'
                PartSize=1,  # 上传分成几部分
                MAXThread=10,  # 支持最多的线程数
                EnableMD5=False  # 是否支持MD5
            )
            return response
        except:
            return False

    # 获取链接
    def get_url(self, Bucket, path, file):
        try:
            download_url = self.client.get_presigned_url(
                Bucket=Bucket,
                Key=f'{path}{file}',  # video/qq.png
                Method='GET',
            )
            return download_url
        except Exception as E:
            print('Fr包err cnd获取路径失败', E)

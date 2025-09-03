from base64 import b64decode
from boto3.session import Session

class S3():

    def __init__(self, aws_id,  aws_sec_key):
        self.aws_id = aws_id
        self.secret_key = aws_sec_key
        
        self.aws_session = Session(
            region_name='eu-central-1',
            aws_access_key_id=self.aws_id,
            aws_secret_access_key=self.secret_key
        )

    def get_decoded_auth_creds(self):
        resp = self.aws_session.client('ecr').get_authorization_token()
        encoded = resp.get('authorizationData')[0].get('authorizationToken')
        return b64decode(encoded).decode('UTF-8')

    def get_secure_url(self, bucket, filename, expires_in=7200, insecure=False):
                
        # max is 7 days
        if not expires_in:
            expires_in = 7200
        elif expires_in > 604800:
            expires_in = 604800
        
        url = self.aws_session.client('s3').generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket, 'Key': filename},
            ExpiresIn=expires_in
        )
        
        if insecure:
            return url.split("?")[0]
        else:
            return url

import boto3


class DataStore():
    def __init__(self, bucket_name: str, _prefix: str):
        self.s3 = boto3.client('s3')
        session = boto3.Session()
        self._s3_resource = session.resource('s3')
        self._bucket_name = bucket_name
        self._prefix = _prefix

        list_response = self.s3.list_objects_v2(Bucket=bucket_name, Prefix=_prefix)
        self._in_content = list_response.get('Contents', [])

    def get_inputs(self):
        for obj in self._in_content:
            yield obj

    def get_input_content(self, key, decode_fun):
        response = self.s3.get_object(
            Bucket=self._bucket_name,
            Key=key,
            # Range="0:10"
        )
        data = response['Body'].read()
        return decode_fun(data)

    def write_output(self, name, data, content_type='image/png'):
        object = self._s3_resource.Object(self._bucket_name, self._prefix + '/' + name)
        object.put(Body=data, ContentType=content_type)










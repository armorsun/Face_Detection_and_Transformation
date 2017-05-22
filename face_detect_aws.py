import boto3

client = boto3.client(
    'rekognition',
    aws_access_key_id='YOUR_ACCESS_KEY',
    aws_secret_access_key='YOUR_SECRET_ACCESS_KEY',
    region_name='YOUR_REGION_NAME'
)

p = open("f2.jpg", 'rb')

face_features = client.detect_faces(Image={
    'Bytes': bytearray(p.read())
},
    Attributes=[
        'ALL'
    ])

p.close()

print face_features

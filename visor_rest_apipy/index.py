from flask import Flask, request, jsonify
from datetime import datetime
import time
import boto
import base64
import json
import uuid
import logging
from botocore.exceptions import ClientError
import zlib
from visor_db_api import VisorDatabaseAPI
import visor_model
from flask import Flask, request
import os
import json
import boto3
import zipfile

app = Flask(__name__)
aws_access_key_id = 'accesskey'
aws_secret_access_key = 'secretkey'
predator_bucket_name = 'mypredator'

local_db_url = 'postgres://postgres:predator@localhost/predator_local'
db = VisorDatabaseAPI(local_db_url)


@app.route('/')
def hello_world():
    return "Hello, World  Pooja Version10!!"


@app.route("/create_session/<client_string>", methods=["GET"])
def create_session(client_string):

    try:
        # validate client string here. value tbd
        user_id = get_uuid_from_id_token(request.headers["Authorization"])
    except:
        return "Invalid ID_token", 400

    start_time = datetime.utcnow()
    end_time = None

    new_session = db.create_new_session(
        user_token=user_id, client_string=client_string)
    return new_session.session_id


@app.route("/complete_session/<session_id>/<end_status>", methods=["GET"])
def complete_session(session_id, end_status):
    # check if session exist
    exist_session = db.lookup_session_by_id(session_id)
    if(exist_session.session_id != session_id):
        return "Session not found", 404
    if(exist_session.end_time != None):
        return "Session was already closed", 400
    # Update visor session table
    db.close_session_by_id(exist_session.session_id)

    # session_records = visor_db_api.lookup_all_session_records_by_session_id(exist_session.session_id)
    # check record table for valid, invalid, and duplicate image then return a json format.
    # no need to talk to image table.
    return "Session closed", 200


@app.route("/sign_s3")
def sign_s3():
    # S3_BUCKET = os.environ.get('S3_BUCKET')
    S3_BUCKET = predator_bucket_name

    file_name = request.args.get('file_name')
    file_type = request.args.get('file_type')
    # session_token = request.args('session_token')

    s3 = boto3.client('s3')
    # s3 = boto.connect_s3(aws_access_key_id, aws_secret_access_key)
    # s3_client = boto3.client("s3",
    #                          #  region_name="us-west-1",
    #                          #  aws_access_key_id=aws_access_key_id,
    #                          #  aws_secret_access_key=aws_secret_access_key,
    #                          )

    presigned_post = s3.generate_presigned_post(
        Bucket=S3_BUCKET,
        Key=file_name,
        Fields={"acl": "public-read", "Content-Type": file_type},
        ExpiresIn=3600
    )

    return json.dumps({
        'data': presigned_post,
        'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
    })


@app.route("/image", methods=['POST'])
def create_new_image():
    new_uuid = str(uuid.uuid4())
    print(request)
    args = request.get_json(force=True)

    if request.method == 'POST':
        session_id = args['session_id']
        s3_path = args['image_path']
        image_path = args['image_path']
        print(s3_path)
    try:
        crc = get_crc_from_is2(image_path)

        validate_params(session_id, s3_path)
        # t0 = time.clock()
        upload_file(image_path, new_uuid)
        # t1 = time.clock() - t0
        image_obj = visor_model.VisorImage(
            image_id=new_uuid, session_id=session_id, image_path=s3_path)
        db.create_new_image_with_image_object(image_obj)
        return image_obj
    except Exception as e:
        upload_state_obj = visor_model.VisorSessionRecord(
            session_id=session_id, image_id=new_uuid, upload_state=e, image_path=s3_path)
        db.upload_state_with_session_object(upload_state_obj)


def get_uuid_from_id_token(id_token: str):
    payload = id_token.split('.')[1]
    payload = payload+'=='
    payload_decode = base64.b64decode(payload)
    payload_json = json.loads(payload_decode)
    return payload_json["sub"]


# def Crc32Hasher(file_path):

#     buf_size = 65536
#     crc32 = 0

#     with open(file_path, 'rb') as f:
#         while True:
#             data = f.read(buf_size)
#             if not data:
#                 break
#             crc32 = zlib.crc32(data, crc32)

#     return format(crc32 & 0xFFFFFFFF, '08x')

# this is the function for returning crc please don't use crc32hasher

def get_crc_from_is2(file):
    archieve = zipfile.ZipFile(file)
# take crc of CameraInfo + IR.data
    cameraInfo_crc = ""
    irData_crc = ""

    for f in archieve.infolist():
        if f.filename == 'CameraInfo.gpbenc':
            cameraInfo_crc = hex(f.CRC)
        if f.filename == 'Images/Main/IR.data':
            irData_crc = hex(f.CRC)
    return cameraInfo_crc + irData_crc


def validate_params(session_id, file_name):
    """Upload a file to an S3 bucket
    :param session_id:session id
    :param file_name: Filepath to upload
    :param s3_key: Bucket to upload to
    """
    # Upload the file  // create_new_session_record ... if this session is close ....if it fails return 404
    # /// then check IS2
    # then check crc
    if db.lookup_session_by_id(session_id) is None:
        raise Exception('session id does not exists')
    if not file_name.lower().endswith('.is2'):
        raise Exception('Invalid file')
    if db.lookup_image_by_crc(crc) is not None:
        raise Exception('Duplicate Image')

    return


def upload_file(file_name, s3_key):
    """Upload a file to an S3 bucket

    :param file_name: Filepath to upload
    :param s3_key: Bucket to upload to
    """
    # Upload the file
    s3_connection = boto.connect_s3(aws_access_key_id, aws_secret_access_key)
    bucket = s3_connection.get_bucket(predator_bucket_name)
    try:
        key = boto.s3.key.Key(bucket, s3_key)
        key.set_contents_from_filename(file_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


# Main code
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

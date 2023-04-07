from google.cloud import storage
from PIL import Image
from io import BytesIO


class Server():
    def __init__(self,bucket_name,jsonfile):
        self.bucket_name=bucket_name
        self.jsonfile=jsonfile
        storage_client = storage.Client.from_service_account_json(jsonfile)
        self.bucket = storage_client.get_bucket(self.bucket_name)

    def retrieve_address(self):
        blob = self.bucket.blob("unit_location.txt")
        msg_xdecode = blob.download_as_string()
        message = msg_xdecode.decode('utf-8')
        data = message.split("\r\n")
        unit_data = [i.split(",") for i in data if len(i) > 1]
        return unit_data

    def retrieve_file_string(self, directory):
        blob3 = self.bucket.get_blob(directory)
        data_undecoded = blob3.download_as_string()
        data = data_undecoded.decode('utf-8')
        return data

    def retrieve_img(self,directory):
        blob = self.bucket.get_blob(directory)
        img = Image.open(BytesIO(blob.download_as_bytes()))
        return img

    def retrieve_file(self,directory,data_type):
        destination_file_name="temp/temp."+data_type
        blob = self.bucket.get_blob(directory)
        blob.download_to_filename(destination_file_name)
        file=open(destination_file_name, "rb")
        return file

    #work in progress for retrieve_file
    def upload_string(self,directory,string):
        blob = self.bucket.blob(directory)
        blob.upload_from_string(string)

    def get_directory(self,key,item):
        if item =="details":
            txtfile="_details.txt"
            pass
        elif item=="lidar":
            txtfile = "_lidar_3d.txt"
            pass
        elif item=="pressure":
            txtfile = "_pressure.txt"
            pass
        elif item=="fall":
            txtfile = "_fall.txt"
            pass
        elif item=="calibration":
            txtfile = "_calibration.txt"
            pass
        elif item=="2d lidar":
            txtfile = "_2d_lidar_image.jpg"
            pass

        elif item=="microphone":
            txtfile = "_microphone.mp3"
            pass
        else :
            txtfile="_"+item+".txt"

        directory = "unitdata_readings/" + key + '/'+key+txtfile
        return directory



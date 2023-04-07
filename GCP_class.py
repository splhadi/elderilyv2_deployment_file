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

    def download_file(self,directory,destination):
        blob = self.bucket.get_blob(directory)
        blob.download_to_filename(destination)




    def download_as_bytes(self,directory):
        blob = self.bucket.get_blob(directory)
        data = blob.download_as_bytes()
        return data

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
        elif item=="microphone_true":
            txtfile = "_microphone_true.mp3"
            pass
        elif item=="microphone_false":
            txtfile = "_microphone_false.mp3"
            pass

        else :
            txtfile="_"+item+".txt"

        directory = "unitdata_readings/" + key + '/'+key+txtfile
        return directory

    def create_folder(self,directory,folder_name):
        blob = self.bucket.blob(directory + folder_name + '/')
        # Upload the blob to the bucket (this creates the folder)
        blob.upload_from_string('')
        pass
    def create_unit_file(self,directory,key,filename='empty',filetype='txt',direct_file=False,content=''):
        if direct_file:
            blob = self.bucket.blob(directory)
        else:
            file = key+'_'+filename +'.'+filetype
            file_directory=directory+key+'/'+file
            print(file_directory)
            blob= self.bucket.blob(file_directory)
        if filetype=='txt':
            blob.upload_from_string(content)
        else:
            blob.upload_from_file(content)

    def create_file(self,directory,filename='empty',filetype='txt',direct_file=False,content=''):
        if direct_file:
            blob = self.bucket.blob(directory)
        else:
            file = +filename +'.'+filetype
            blob= self.bucket.blob(directory+file)
        if filetype=='txt':
            blob.upload_from_string(content)
        else:
            blob.upload_from_file(content)

    def delete_folder(self, folder_name):
        """Deletes a folder and all its contents in a Google Cloud Storage bucket."""
        #client = storage.Client()
        #bucket = client.bucket(bucket_name)

        # List all the blobs in the bucket that start with the folder name
        blobs_to_delete = self.bucket.list_blobs(prefix=folder_name)

        # Delete each blob in the folder
        for blob in blobs_to_delete:
            blob.delete()

        # Delete the folder itself
        #self.bucket.delete_blob(folder_name)

    def rename_file(self, old_name, new_name):
        """Renames a file in a Google Cloud Storage bucket."""


        # Get a reference to the old file
        old_blob = self.bucket.blob(old_name)

        # Rename the file
        new_blob = self.bucket.rename_blob(old_blob, new_name)

        print(f'File {old_name} has been renamed to {new_name}.')

    def file_details(self,directory):
        blob = self.bucket.get_blob(directory)

        # Get the details of the blob object
        blob_details = blob.exists()

        if blob_details:
            print("File name:", blob.name)
            print("File size:", blob.size)
            print("Content Type:", blob.content_type)
            print("Updated:", blob.updated)
            print('Time created:',blob_details)

            return [blob.name,blob.size,blob.content_type,blob.updated]
        else:
            print("The specified file does not exist in the bucket")
            return None

from dbupload import DropboxConnection
import requests

email = "me@sachinshinde.com"  # raw_input("Enter Dropbox email address:")
password = "dropboxpass"  # getpass("Enter Dropbox password:")

# Create a little test file
# fh = open("small_test_file.txt","w")
# fh.write("Small test file")
# fh.close()


# Create the connection
conn = DropboxConnection(email, password)
# try:
    # Download file from internet
print "***starting download"
# r = requests.get(
#     "http://50.7.164.194:8182/ucorn5vyrcu4tqukwyalhetmlq3qo6unjderakppp3bx4c5ecz6kn22b7m/video.mp4")
# print len(r.content)
# import io
#
# f = io.BytesIO(r.content)
# print "***file downloaded"

# Upload the file
# conn.upload_file_f(f, "/", "test.mp3")
conn.delete_file("/", "Untitled.png")
conn.delete_dir("/test_folder")
# print("Upload")
# except:
#     print("Upload failed")
# else:
#     print("Uploaded small_test_file.txt to the root of your Dropbox")
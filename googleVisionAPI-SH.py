import io
import os
import requests

from google.cloud import vision
from google.cloud.vision import types

url1 = "antilost.io"

def findcord():

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\brand\\OneDrive\\Documents\\GAuth\\ShellHacks2018-08825c9647d5.json"
    client = vision.ImageAnnotatorClient()

    file_name = os.path.join(os.path.dirname(__file__),"C:\\Users\\brand\\OneDrive\\Documents\\Canada-B.jpg")

    with io.open(file_name,'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    response = client.landmark_detection(image=image)
    landmarks = response.landmark_annotations
    print('Landmarks:')

    for landmark in landmarks:
        print(landmark.description)
        for location in landmark.locations:
            latlng = location.lat_lng
            longi = latlng.longitude
            lati = latlng.latitude
            print('Latitude {}'.format(lati))
            print('Longitude {}'.format(longi))
            return [longi, lati]


    r = requests.post(url1, json=[{lati, longi}])
    print(r.text,)

#for image
findcord()


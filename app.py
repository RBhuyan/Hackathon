#!/usr/bin/python
# -*- coding: utf-8 -*-
import io
import os
from datetime import datetime
from flask import Flask, render_template, jsonify, redirect, url_for, request
import math
import googlemaps
import heapq
import datetime
from google.cloud import vision
from google.cloud.vision import types
import json


with open('config.json','r') as json_data_file:
    credentials = json.load(json_data_file)

gmaps = googlemaps.Client(key=credentials['key'])

app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/find', methods=['GET'])
def find():
    print("Find")
    dataSet = findcord()
    print("We did it 5")
    print(dataSet)
    print(type(dataSet))

    response = app.response_class(response=json.dumps(dataSet), status = 200, mimetype = 'application/json')
    return response
    return dataSet


@app.route('/upload', methods=['POST'])
def upload():
    print("approute")
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            now = datetime.datetime.now()
            filename = os.path.join(app.config['UPLOAD_FOLDER'], "%s.%s" % (now.strftime("%Y-%m-%d-%H-%M-%S-%f"), file.filename.rsplit('.', 1)[1]))
            file.save(filename)
            return jsonify({"success":True})

    dataSet = findcord()
    return jsonify({dataSet})


def findcord():
    print("FindChord")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Google\\HackathonTest-d56580d391fd.json"
    client = vision.ImageAnnotatorClient()

    file_name = os.path.join(os.path.dirname(__file__),"C:\\Users\\bhuya\\OneDrive\\Pictures\\inputPicture.jpg")

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
    print("We did it 4")
    # return get_center_elevation(lati, longi)
    return get_center_elevation(29.653038, -82.329434)


def get_center_elevation(lat,long):
    print("get_center_evelation")
    ret_obj = gmaps.elevation((lat,long))


    print(ret_obj)
    center_elevation = round(ret_obj[0]['elevation'],3)
    print("Center elevation is %s"  %center_elevation)
    json_final = find_max_height(lat,long,center_elevation)
    print("We did it 3")
    return json_final


def find_max_height(lat,long,elevation):
    print("max height")

    original_points = (lat, long)
    heap = []
    heapq.heapify(heap)
    dict = {}
    bearing = 3.6
    radiusEarth = 3959.8728
    dist = 5/radiusEarth


    lat = math.radians(lat)

    lat2_partA = math.sin(lat) * math.cos(dist)
    lat2_partB = math.sin(dist) * math.cos(lat)

    long = math.radians(long)
    long2_partA = math.sin(dist) * math.cos(lat)



    for i in range(0,10):
        new_bearing = bearing * i
        rad_bearing = math.radians(new_bearing)

        lat2 = math.asin((lat2_partA + (lat2_partB * math.cos(rad_bearing))))
        lat2 = math.degrees(lat2)

        long2 = long + math.atan2( math.sin(rad_bearing) * long2_partA , math.cos(dist) - math.sin(lat)*math.sin(lat2) )
        long2 = math.degrees(long2)

        if(long2 < -180):
            long2 = long2 + 360
        elif(long2 > 180):
            long2 = 360 - long2

        path = [(lat,long),(lat2,long2)]
        all_elevation = gmaps.elevation_along_path(path,50)

        for e in all_elevation:
            cur_elevation = round(e['elevation'],3)
            if(cur_elevation > elevation):
                if(len(heap) < 5):
                    heapq.heappush(heap,cur_elevation)
                    if(dict.get(cur_elevation) ==  None):
                        co_ord = [(lat2,long2)]
                        dict[cur_elevation] = co_ord
                    else:
                        temp_co_ord = dict.get(cur_elevation)
                        temp_co_ord.append((lat2,long2))
                        dict.update({cur_elevation:temp_co_ord})
                else:
                    lowest_elevation = heap[0]
                    if(lowest_elevation < cur_elevation):
                        heapq.heappop(heap)
                        dict.pop(lowest_elevation)
                        dict[cur_elevation] = [(lat2,long2)]


    json_obj = distance(heap,dict,original_points)
    print("We did it 2")
    return json_obj

def distance(heap,dict,original_points):
    print("distance function")
    print((heap))
    json_return = {}
    i=5
    while len(heap) > 0:
        cur_elevation = heapq.heappop(heap)
        gps_co_ord = dict.get(cur_elevation)

        now = datetime.datetime.now()
        matrix = gmaps.distance_matrix(original_points,gps_co_ord,
                                       mode = "walking",
                                       units = "imperial",
                                       departure_time = now)
        json_return[i] = [cur_elevation,matrix['rows'][0]['elements'][0]['distance']['text'],matrix['rows'][0]['elements'][0]['duration']['text'],gps_co_ord[0][0],gps_co_ord[0][1]]
        print(json_return)
        i=i-1
    print(json_return)
    print("We did it")
    json_return['og_points']=original_points

    return json_return






def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


if __name__ == "__main__":
    app.run(debug=True)

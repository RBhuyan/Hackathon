import math
import googlemaps
import heapq
import datetime

gmaps=''

def get_center_elevation(lat,long):

    ret_obj = gmaps.elevation((lat,long))


    print(ret_obj)
    center_elevation = round(ret_obj[0]['elevation'],3)
    print("Center elevation is %s"  %center_elevation)
    json_final = find_max_height(lat,long,center_elevation)
    return json_final

def find_max_height(lat,long,elevation):


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



    for i in range(0,50):
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
    return json_obj

def distance(heap,dict,original_points):
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
        i=i-1
    json_return['og_points']=original_points

    return json_return





lat = 29.653038
long =-82.329434
get_center_elevation(lat,long)



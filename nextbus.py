'''nextbus.py

Takes information about JFK's bus routes and does the following:
- Create geojson files of the bus routes
- Create geojson files of bus stop locations and information
'''

import sys
import urllib.request, json

def get_json_parsed(url):
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    return data

#convert json data to geojson
def coords_to_geojson(data, title):
    feature = {}
    feature["type"] = "Feature"
    feature["geometry"] = {}
    feature["geometry"]["type"] = "LineString"
    coordinates = []
    for pair in data:
        add = [] 
        add.append(float(pair["lon"]))
        add.append(float(pair["lat"]))
        coordinates.append(add)
    feature["geometry"]["coordinates"] = coordinates
    feature["properties"] = {}
    feature["properties"]["title"] = title
    feature["properties"]["stroke"] = "#FF0000"
    return feature

locations = ("http://webservices.nextbus.com/service/publicJSONFeed?command=vehicleLocations&a=jfk&r=p6&t=0")
json_locations = get_json_parsed(locations)

routes = ("http://webservices.nextbus.com/service/publicJSONFeed?command=routeList&a=jfk")
json_routes = get_json_parsed(routes)

#Create arrays of the route tags and the route titles, given the agency name (jfk)
titles = []
tags = []
for i in json_routes["route"]:
    if (i == "title"):
        titles.append(i)
        tags.append(json_routes["route"]["tag"])
        print(i)
        break
    else:
        print(i["tag"])
        titles.append(i["title"])
        tags.append(i["tag"])

#create geojson files of each bus route listed on NextBus
counter = 0
for i in tags:
    route_url = ("http://webservices.nextbus.com/service/publicJSONFeed?command=routeConfig&a=jfk&r=" + i)
    json_route = get_json_parsed(route_url)
    points = json_route["route"]["path"]
    path = {}
    path["type"] = "FeatureCollection"
    features = []
    for j in points:
        features.append(coords_to_geojson(j["point"], titles[counter]))
    path["features"] = features
    if (i == "c"):
        with open("jfk_cargo.geojson", "w", encoding="utf-8") as f:
            json.dump(path, f, ensure_ascii=False, indent=4)
    elif (i == "s"):
        with open("jfk_service.geojson", "w", encoding="utf-8") as f:
            json.dump(path, f, ensure_ascii=False, indent=4)
    elif (i == "e"):
        with open("jfk_employee.geojson", "w", encoding="utf-8") as f:
            json.dump(path, f, ensure_ascii=False, indent=4)
    elif (i == "l"):
        with open("jfk_longterm.geojson", "w", encoding="utf-8") as f:
            json.dump(path, f, ensure_ascii=False, indent=4)
    else:
        with open("jfk_misc.geojson", "w", encoding="utf-8") as f:
            json.dump(path, f, ensure_ascii=False, indent=4)
    #print(json_route["route"]["stop"][1])
    counter += 1

#next steps:
#add markers for the bus routes themselves
#get prediction information, stop name, and other information to display at stop
#add markers for vehicle location (update every so often)?

#Description Title: Next Tracked Vehicles
#Decription:
# Route: [Route Name]
# Direction: [Direction]
# Stop: [Stop Name]
# Departures [at first stop]/Arrivals [at other stops]: [Predictions]

def stop_to_geojson(data, title, direction):
    feature = {}
    feature["type"] = "Feature"
    feature["geometry"] = {}
    feature["geometry"]["type"] = "Point"
    coords = [float(data["lon"]), float(data["lat"])]
    feature["geometry"]["coordinates"] = coords
    feature["properties"] = {}
    feature["properties"]["title"] = "Next Tracked Vehicles"
    #feature["properties"]["description"] = {}
    description_items = []
    description_items.append("<p style=\"margin:0\">Route: " + title + "</p>")
    description_items.append("<p style=\"margin:0\">Direction: " + direction + "</p>")
    description_items.append("<p style=\"margin:0\">Stop: " + data["title"] + "</p>")
    feature["properties"]["description"] = "\n".join(description_items)
    return feature

counter2 = 0
for i in tags:
    route_url = ("http://webservices.nextbus.com/service/publicJSONFeed?command=routeConfig&a=jfk&r=" + i + "&terse")
    json_route = get_json_parsed(route_url)
    stops = json_route["route"]["stop"]
    print(json_route["route"]["direction"]["tag"])
    stop_info = {}
    stop_info["type"] = "FeatureCollection"
    features = []
    for j in stops:
        features.append(stop_to_geojson(j,titles[counter2],json_route["route"]["direction"]["tag"]))
    stop_info["features"] = features
    print(json.dumps(stop_info))
    if (i == "c"):
        with open("jfk_cargo_points.geojson", "w", encoding="utf-8") as f:
            json.dump(stop_info, f, ensure_ascii=False, indent=4)
    elif (i == "s"):
        with open("jfk_service_points.geojson", "w", encoding="utf-8") as f:
            json.dump(stop_info, f, ensure_ascii=False, indent=4)
    elif (i == "e"):
        with open("jfk_employee_points.geojson", "w", encoding="utf-8") as f:
            json.dump(stop_info, f, ensure_ascii=False, indent=4)
    elif (i == "l"):
        with open("jfk_longterm_points.geojson", "w", encoding="utf-8") as f:
            json.dump(stop_info, f, ensure_ascii=False, indent=4)
    else:
        with open("jfk_misc_points.geojson", "w", encoding="utf-8") as f:
            json.dump(stop_info, f, ensure_ascii=False, indent=4)
    counter2 += 1

#to do: find way to display description information on multiple lines (realized as a div, so wrap each in style tags?)
'''nextbus.py

Takes information about JFK's bus routes and does the following:
- Create geojson files of the bus routes
- Create geojson files of bus stop locations and information about next arrival departure
- Write geojson file information to Azure site so information on txlink can be updated
'''

import sys
import urllib, json

def get_json_parsed(url):
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    return data

#Convert list of coordinates in JSON to a GeoJSON LineString.
def coords_to_geojson(data, title):
    feature = {}
    feature["type"] = "Feature"
    feature["geometry"] = {}
    feature["geometry"]["type"] = "LineString"
    coordinates = []
    for pair in data:
        toAdd = [] 
        toAdd.append(float(pair["lon"]))
        toAdd.append(float(pair["lat"]))
        coordinates.append(toAdd)
    feature["geometry"]["coordinates"] = coordinates
    feature["properties"] = {}
    feature["properties"]["title"] = title
    feature["properties"]["stroke"] = "#FF0000"
    return feature

# Convert stop-specific information to GeoJSON Points with a description.
# Need to include two different sets of JSON data because stop_data contains coordinates and pred_data has prediction information.
def stop_to_geojson(stop_data, pred_data, direction):
    feature = {}
    feature["type"] = "Feature"
    feature["geometry"] = {}
    feature["geometry"]["type"] = "Point"
    coords = [float(stop_data["lon"]), float(stop_data["lat"])]
    feature["geometry"]["coordinates"] = coords
    feature["properties"] = {}
    feature["properties"]["title"] = "Next Tracked Vehicles"
    description_items = []
    # Include any HTML/CSS desired to style the description box's contents.
    description_items.append("<p style=\"margin:0\">Route: " + pred_data["predictions"]["routeTitle"] + "</p>")
    description_items.append("<p style=\"margin:0\">Direction: " + direction + "</p>")
    description_items.append("<p style=\"margin:0\">Stop: " + stop_data["title"] + "</p>")
    if "direction" in pred_data["predictions"]:     # If the direction object exists, there are predictions. Else there are none.
        times = []      #List to hold the arrival and departure times of the next buses.
        for prediction in pred_data["predictions"]["direction"]["prediction"]:
            times.append(prediction["minutes"])
        pred_times = "<p style=\"margin:0\">"      # Initialize the string we will add to description_items
        if (pred_data["predictions"]["direction"]["prediction"][0]["isDeparture"] == "true"):
            pred_times = pred_times + "Departures: <strong>" + ", ".join(times)
        else:
            pred_times = pred_times + "Arrivals: <strong>" + ", ".join(times)
        description_items.append(pred_times + " minutes </strong></p>")
    else:
        description_items.append("<p style=\"margin:0\"><strong>No Current Predictions</strong></p>")
    feature["properties"]["description"] = "\n".join(description_items)
    return feature

def main():
    routes = ("http://webservices.nextbus.com/service/publicJSONFeed?command=routeList&a=jfk")
    json_routes = get_json_parsed(routes)
    #Create arrays of the route tags and the route titles, given the agency name (jfk)
    titles = []
    tags = []
    for i in json_routes["route"]:
        if (i == "title"):
            titles.append(i)
            tags.append(json_routes["route"]["tag"])
            break
        else:
            titles.append(i["title"])
            tags.append(i["tag"])
    title_counter = 0
    for tag in tags:
        route_url = ("http://webservices.nextbus.com/service/publicJSONFeed?command=routeConfig&a=jfk&r=" + tag)
        json_route = get_json_parsed(route_url)
        points = json_route["route"]["path"]
        path = {}
        path["type"] = "FeatureCollection"
        path_features = []
        for j in points:
            path_features.append(coords_to_geojson(j["point"], titles[title_counter]))
        path["features"] = path_features
        print(tag)
        if (tag == "c"):
            #url for writing to azure: D:\\home\\site\\wwwroot\\NextBus\\jfk_cargo.geojson
            with open("jfk_cargo.geojson", "w") as f:
                json.dump(path, f, ensure_ascii=False, indent=4)
        elif (tag == "s"):
            with open("jfk_service.geojson", "w") as f:
                json.dump(path, f, ensure_ascii=False, indent=4)
        elif (tag == "e"):
            with open("jfk_employee.geojson", "w") as f:
                json.dump(path, f, ensure_ascii=False, indent=4)
        elif (tag == "l"):
            with open("fk_longterm.geojson", "w") as f:
                json.dump(path, f, ensure_ascii=False, indent=4)
        else:
            with open("jfk_misc.geojson", "w") as f:
                json.dump(path, f, ensure_ascii=False, indent=4)
        stops = json_route["route"]["stop"]
        predictions_url = ("http://webservices.nextbus.com/service/publicJSONFeed?command=predictions&a=jfk&r=" + tag)
        stop_info = {}
        stop_info["type"] = "FeatureCollection"
        stop_features = []
        for j in stops:
            stop_url = predictions_url + "&s=" + j["tag"]
            json_stop = get_json_parsed(stop_url)
            stop_features.append(stop_to_geojson(j,json_stop,json_route["route"]["direction"]["tag"]))
        stop_info["features"] = stop_features
        if (tag == "c"):
            print("cargo")
            #url for writing to azure: D:\\home\\site\\wwwroot\\NextBus\\jfk_cargo_points.geojson
            with open("jfk_cargo_points.geojson", "w") as f:
                json.dump(stop_info, f, ensure_ascii=False, indent=4)
        elif (tag == "s"):
            print("service")
            with open("jfk_service_points.geojson", "w") as f:
                json.dump(stop_info, f, ensure_ascii=False, indent=4)
        elif (tag == "e"):
            print("employee")
            with open("jfk_employee_points.geojson", "w") as f:
                json.dump(stop_info, f, ensure_ascii=False, indent=4)
        elif (tag == "l"):
            print("long term")
            with open("jfk_longterm_points.geojson", "w") as f:
                json.dump(stop_info, f, ensure_ascii=False, indent=4)
        else:
            print("misc")
            with open("jfk_misc_points.geojson", "w") as f:
                json.dump(stop_info, f, ensure_ascii=False, indent=4)
        title_counter += 1

if __name__== "__main__":
    main()
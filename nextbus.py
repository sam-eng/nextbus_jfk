'''nextbus.py

Takes information about JFK's bus routes and does the following:
- Create XML files of the bus routes
- Create XML files of bus stop locations and information about next arrival departure
- Write XML file information to Azure site so information on txlink can be updated
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
def stop_to_xml(stop_data, pred_data, direction):
    lat = "<geo:lat>" + stop_data["lat"] + "</geo:lat>"
    lon = "<geo:long>" + stop_data["lon"] + "</geo:long>"
    title = "<title>Next Tracked Vehicles</title>"
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
    description = "<desciption>" + "\n\t\t\t\t".join(description_items) + "\n\t\t\t</description>"
    item = "<item>\n\t\t\t" + title + "\n\t\t\t" + description + "\n\t\t\t" + lat + "\n\t\t\t" + lon + "\n\t\t</item>"
    return item

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
            with open("jfk_longterm.geojson", "w") as f:
                json.dump(path, f, ensure_ascii=False, indent=4)
        else:
            with open("jfk_misc.geojson", "w") as f:
                json.dump(path, f, ensure_ascii=False, indent=4)
        stops = json_route["route"]["stop"]
        predictions_url = ("http://webservices.nextbus.com/service/publicJSONFeed?command=predictions&a=jfk&r=" + tag)
        stop_info = []
        for j in stops:
            stop_url = predictions_url + "&s=" + j["tag"]
            json_stop = get_json_parsed(stop_url)
            stop_info.append(stop_to_xml(j,json_stop,json_route["route"]["direction"]["tag"]))
        xml_header = "<rss version=\"2.0\" xmlns:geo=\"http://www.w3.org/2003/01/geo/wgs84_pos#\">\n\t<channel>\n\t\t"
        xml_content = "<title></title>\n\t\t<link />\n\t\t<description />\n\t\t"
        xml_footer = "\n\t</channel>\n<rss>"
        if (tag == "c"):
            print("cargo")
            #url for writing to azure: D:\\home\\site\\wwwroot\\NextBus\\jfk_cargo_points.geojson
            with open("jfk_cargo_points.xml", "w+") as f:
                f.write(xml_header + xml_content + "\n\t\t".join(stop_info) + xml_footer)
        elif (tag == "s"):
            print("service")
            with open("jfk_service_points.xml", "w+") as f:
                f.write(xml_header + xml_content + "\n\t\t".join(stop_info) + xml_footer)
        elif (tag == "e"):
            print("employee")
            with open("jfk_employee_points.xml", "w+") as f:
                f.write(xml_header + xml_content + "\n\t\t".join(stop_info) + xml_footer)
        elif (tag == "l"):
            print("long term")
            with open("jfk_longterm_points.xml", "w+") as f:
                f.write(xml_header + xml_content + "\n\t\t".join(stop_info) + xml_footer)
        else:
            print("misc")
            with open("jfk_misc_points.xml", "w+") as f:
                f.write(xml_header + xml_content + "\n\t\t".join(stop_info) + xml_footer)
        title_counter += 1

if __name__== "__main__":
    main()
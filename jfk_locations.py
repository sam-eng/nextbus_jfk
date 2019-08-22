'''jfk_locations.py

Use NextBus' public JSON feed to create an XML file of vehicle locations.

'''
import sys
import urllib, json

def get_json_parsed(url):
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    return data

def vehicle_json_to_xml(data, route_title):
    print(data)
    lat = "<geo:lat>" + data["lat"] + "</geo:lat>"
    lon = "<geo:long>" + data["lon"] + "</geo:long>"
    title = "<title>" + data["id"] + "</title>"
    description = "<description>" + route_title + "</description>"
    item = "<item>\n\t\t\t" + title + "\n\t\t\t" + description + "\n\t\t\t" + lat + "\n\t\t\t" + lon + "\n\t\t</item>"
    return item

def main():
    routes_url = ("http://webservices.nextbus.com/service/publicJSONFeed?command=routeList&a=jfk")
    json_routes = get_json_parsed(routes_url)
    #Create arrays of the route tags, given the agency name (jfk)
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
    vehicles = []
    for tag in tags:
        locations_url = "http://webservices.nextbus.com/service/publicJSONFeed?command=vehicleLocations&a=jfk&r=" + tag + "&t=0"
        locations_json = get_json_parsed(locations_url)
        if "vehicle" in locations_json:
            print(locations_json["vehicle"])
            #item title = locations_json["vehicle"]["id"]
            #item lat = lat
            #item long = lon
            #description = route title?
            #for vehicle in locations_json["vehicle"]:
            vehicles.append(vehicle_json_to_xml(locations_json["vehicle"], titles[title_counter]))
        title_counter = title_counter + 1
        print(vehicles)
    xml_header = "<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n<rss version=\"2.0\" xmlns:geo=\"http://www.w3.org/2003/01/geo/wgs84_pos#\">\n\t<channel>\n\t\t"
    xml_content = "<title></title>\n\t\t<link />\n\t\t<description />\n\t\t"
    xml_footer = "\n\t</channel>\n</rss>"
    with open("jfk_vehicle_locations.xml", "w+") as f:
        f.write(xml_header + xml_content + "\n\t\t".join(vehicles) + xml_footer)
    
if __name__== "__main__":
    main()
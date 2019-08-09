# nextbus_jfk

nextbus_jfk contains a Python program to do the following using [NextBus' public JSON feed](http://www.nextbus.com/xmlFeedDocs/NextBusXMLFeed.pdf):
* Given an agency tag (i.e. a short code representing an _agency_ using NextBus to track their buses), create geojson files displaying the path of each bus route the agency has.
* For each route for an agency, create a geojson file with a Point for each bus stop on the route. The geojson Point contains details of the stop, such as the stop name, route name, direction of the route (i.e. the route is a loop or not), and the predicted departure/arrival time of the next bus.

The code written is currently written for JFK airport's bus routes specifically, but to adapt the code for another agency, please do the following:
* Replace "jfk" in the urls with the new agency tag you wish to use.
* Alter the if-else statements for creating the geojson files. *Add* or *remove* if/elif statements to match the number of routes, altering the boolean comparison to match the agency's route tags.
* Also, I suggest that you alter the names of the files being created by the program to reflect the name of the new agency and the new names of routes. I use the format [agency tag]_[route name].geojson, but use any naing convention you like.

#To Do:
* Find a way to represent a stop that is on multiple routes (i.e. JFK's Federal Circle stop is both on the Service Route and the Cargo Route)
* Clean up code and document in comments (or somewhere else) how the JSON retrieved from NextBus' public JSON feed is structured
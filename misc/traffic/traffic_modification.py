import sys
import django
import os

import math
from django.db.transaction import atomic
import json

sys.path.extend(['D:/fyp/fypsite'])
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fypsite.settings")
django.setup()

from webapp.models import Traffic,TrafficLayer,TrafficeLayerPiece

"""
This utility is used to separate the road segments that overlap (i.e. two directions of the same road)
"""
@atomic
def modify_piece_data(traffic_name):

    LNG_MODIFICATION_AMOUNT = 1e-5
    MODIFICATION_DIST = 1.3700110095126535e-05

    def modify_line(line):
        "return a modified line (without line break)"
        start_lng,start_lat,end_lng,end_lat,speed = map(float,line.split(","))
        # get lat adjustment amount
        cosine = abs(start_lng-end_lng) / math.sqrt((start_lng-end_lng)**2 + (start_lat-end_lat)**2)
        if (cosine!=0):
            lat_adjustment = MODIFICATION_DIST * cosine
            lng_adjustment = MODIFICATION_DIST * math.sqrt(1 - cosine ** 2)
            if ((end_lat - start_lat)/(end_lng-start_lng) > 0): # if the segment is slanging upward, we should move it left
                lng_adjustment = - lng_adjustment
            if (start_lng < end_lng): # segment is towards east, move up
                start_lat += lat_adjustment
                start_lng += lng_adjustment
                end_lat += lat_adjustment
                end_lng += lng_adjustment
            elif (start_lng > end_lng): # towards west, move down
                start_lat -= lat_adjustment
                start_lng -= lng_adjustment
                end_lat -= lat_adjustment
                end_lng -= lng_adjustment
        # when cosine = 0, the segment is vertical, apply vertical adjustment
        elif (start_lng == end_lng and start_lat > end_lat): # towards south, move right
            start_lng += LNG_MODIFICATION_AMOUNT
            end_lng += LNG_MODIFICATION_AMOUNT
        elif(start_lng == end_lng and start_lat < end_lat): # towards north, move left
            start_lng -= LNG_MODIFICATION_AMOUNT
            end_lng -= LNG_MODIFICATION_AMOUNT
        return "{},{},{},{},{}".format(start_lng,start_lat,end_lng,end_lat,speed)

    layers = Traffic.objects.get(note=traffic_name).trafficlayer_set.all()
    for layer in layers:
        pieces = layer.trafficelayerpiece_set.all()
        for piece in pieces:
            raw_lines = piece.raw_data.splitlines()
            modified_lines = map(modify_line,raw_lines)
            piece.raw_data = "\n".join(modified_lines)
            piece.recalc_json_data()
            piece.save()
            print ("Finished processing piece {}".format(piece))


if __name__  == "__main__":
    tls = Traffic.objects.all()
    for t in tls:
        if (t.note != "Road-Segment"):
            modify_piece_data(t.note)
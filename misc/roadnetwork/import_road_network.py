"""
Utility for importing LTA roadnetwork into database
"""
import sys
import django
import os
from django.db.transaction import atomic
import json

sys.path.extend(['D:/fyp/fypsite'])
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fypsite.settings")
django.setup()

from webapp.models import RoadNetwork,RoadSegGrid,RoadSeg,Bounds

class RoadNetworkImporter():
    @atomic
    def import_road_network(self,network_name,filename):
        # preprocess content
        lines = open(filename).readlines()
        seg_ls = self.preprocess_file(lines)
        network_bounds = self.get_bounds_from_coords(
            map(lambda x:x["coords"][0],seg_ls) + map(lambda x:x["coords"][1],seg_ls)
        )
        network_obj = self.create_network_obj(bounds=network_bounds,name=network_name)
        network_obj.create_seg_grids()
        print ("Start to import segments")
        # put road segments into correct grids
        counter= 0
        for seg in seg_ls:
            network_obj.store_road_seg(seg)
            counter += 1
            if (counter % 10 == 0): print("Finish importing {}".format(counter))


    def preprocess_file(self,lines):
        "return list of {cat,id,name,coords}"
        ls = []
        for i in range(0,len(lines),4):
            coords = [map(float,lines[i+2].split("\t")),map(float,lines[i+3].split("\t"))]
            ls.append(
                {
                    "coords":coords,
                    "name":lines[i].split("\t")[4].strip(),
                    "id":int(lines[i].split("\t")[0]),
                    "cat":lines[i].split("\t")[1]
                }
            )
        return ls

    def get_bounds_from_coords(self,coordinates):
        "coordinates is list of [lng,lat]"
        min_lat = 100
        max_lat = 0
        min_lng = 200
        max_lng = 0
        for c in coordinates:
            lng, lat = c
            if (lng > max_lng):
                max_lng = lng
            if (lng < min_lng):
                min_lng = lng
            if (lat > max_lat):
                max_lat = lat
            if (lat < min_lat):
                min_lat = lat
        return {"t": max_lat, "b": min_lat, "l": min_lng, "r": max_lng}

    def create_network_obj(self,bounds,name):
        bound_obj = Bounds.objects.create(
            east = bounds["r"],
            west = bounds["l"],
            south = bounds["b"],
            north = bounds["t"]
        )
        return RoadNetwork.objects.create(
            name = name,
            bounds = bound_obj
        )


if __name__ == "__main__":
    importer = RoadNetworkImporter()
    importer.import_road_network(network_name="Singapore LTA",filename="D:/fyp/LTA.txt")
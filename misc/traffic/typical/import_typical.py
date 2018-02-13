"""
Utility for importing typical traffic into database
"""

import sys
import django
import os

sys.path.extend(['D:/fyp/fypsite'])
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fypsite.settings")
django.setup()

from webapp.models import Traffic,TrafficLayer,TrafficeLayerPiece,RoadSeg
from datetime import datetime
from misc.traffic.slice_by_region import TrafficDataSlicer

ROAD_SEG_CAT_DICT = {int(r.id): r for r in RoadSeg.objects.all()}

class TypicalTrafficDBImporter(object):
    #@atomic
    def import_traffic(self, data_by_cat, traffic_name,format_geojson=False,speed_records=None):
        "data_by_cat is a dict {'A':{...},'B':{...}}"
        # create Traffic
        traffic = Traffic.objects.create(
            note = traffic_name,
            recorded_time = datetime.now(),
            speed_records = speed_records,
            type="typical"
        )
        print("traffic obj {} created!".format(traffic_name))
        # create levels
        levels = self.create_levels(traffic)
        print ("Levels obj created!")
        for level in levels:
            cat = level["cat"]
            level_obj = level["obj"]
            feature_data = data_by_cat[cat] # a dict that contain feature pieces
            self.create_layer_pieces(layer=level_obj,feature_data=feature_data,format_geojson=format_geojson)
            print ("Pieces for level {} created!".format(cat))

    def create_layer_pieces(self,layer,feature_data,format_geojson=False):
        "set format_geojson if the feature_data is only txt data"
        for key,value in feature_data.items():
            # TODO: remove hard code
            y = int(key / 4)
            x = key % 4
            tlp = TrafficeLayerPiece.objects.create(
                traffic_layer=layer,
                num_records=0,
                piece_num= key,
                p_x = x,
                p_y = y,
                raw_data=self.format_feature_data(value),
                json_data= ""
            )
            #tlp.recalc_json_data(save=True)

    def format_feature_data(self,data):
        "data is a dict, each value is a list of object"
        lines = []
        for item in data:
            line = "{},{},{},{},{}".format(item["coord1"][0],item["coord1"][1],item["coord2"][0],item["coord2"][1],item["speed"])
            lines.append(line)
        return "\n".join(lines)

    def create_levels(self,traffic):
        "return list of {obj,cat}"
        layer_config = {
            12: ["A"],
            13: ["B"],
            14: ["C"],
            15: ["D"],
            16: ["E", "S","N"]
        }
        layers = []
        for key, value in layer_config.items():
            for cat in value:
                layers.append(
                    {
                        "obj":TrafficLayer.objects.create(
                            traffic=traffic,
                            disp_level=key,
                            category=cat
                        ),
                        "cat":cat
                    }
                )
        return layers



class AutoTrafficImporter(object):

    CAT_DICT = {
        "A": "CATA",
        "B": "CATB",
        "C": "CATC",
        "D": "CATD",
        "E": "CATE",
        "S": "SLIP",
        "N": "NCAT"
    }
    DEFAULT_X_SPLIT = 4
    DEFAULT_Y_SPLIT = 4

    def __init__(self,x_split=None,y_split=None):
        if (x_split and y_split):
            self.x_split = x_split
            self.y_split = y_split
        else:
            self.x_split = AutoTrafficImporter.DEFAULT_X_SPLIT
            self.y_split = AutoTrafficImporter.DEFAULT_Y_SPLIT

    def import_data(self,src_txt_name,traffic_name):
        "the source file should contain lines with format [coord1,coord2,cat,speed]"
        content = open(src_txt_name).read()
        processed_content = self.preprocess(content)
        speed_records = ["{},{}".format(value["id"],value["speed"]) for value in processed_content]
        print ("Finished preprocessing")
        data_bounds = self.get_bounds(processed_content)
        layers = self.split_layers(processed_content)
        pieced_layers = {key:self.split_pieces(value,data_bounds) for key,value in layers.items()}
        self.import_to_db(pieced_layers=pieced_layers,t_name=traffic_name,speed_records="\n".join(speed_records))

    def import_to_db(self,pieced_layers,t_name,speed_records):
        "pieced layer is {'A':{0:[],1:[]...}...}"
        importer = TypicalTrafficDBImporter()
        importer.import_traffic(data_by_cat=pieced_layers,traffic_name=t_name,format_geojson=True,speed_records=speed_records)

    def split_layers(self,content):
        "return a dict {'A':[],'B':[]...}, 'cat' are changed to single char"
        layers = {"A":[],"B":[],"C":[],"D":[],"E":[],"S":[],"N":[]}
        cat_lookup = {value:key for key,value in self.CAT_DICT.items()}
        for item in content:
            item["cat"] = cat_lookup[item["cat"]]
            l_key = item["cat"]
            layers[l_key].append(item)
        return layers

    def get_bounds(self,content):
        "return a dict {'l','r','t','b'}"
        coord1_ls = [c["coord1"] for c in content]
        coord2_ls = [c["coord2"] for c in content]
        slicer = TrafficDataSlicer()
        return slicer.get_bounds_from_coords(coord1_ls + coord2_ls)


    def split_pieces(self,layer,bounds):
        "takes in a list, return a dict {0:[],1:[],...}"
        slicer = TrafficDataSlicer()
        slices = slicer.create_slices_from_ls(layer,bounds=bounds,x_slice_in=self.x_split,y_slice_in=self.y_split,
                                     get_coords=lambda x:[x["coord1"],x["coord2"]])
        return slices

    def preprocess(self,txt):
        "return a list of dict {coord1,coord2,cat,speed}"
        lines = map(lambda x:x.split(","),txt.splitlines())
        return [
            {
                "coord1": [float(line[0]),float(line[1])],
                "coord2": [float(line[2]),float(line[3])],
                "cat":  line[4],
                "speed": int(line[5])
            }
            for line in lines
        ]


class AnotherAutoTrafficImporter(AutoTrafficImporter):
    def preprocess(self,txt):
        lines = map(lambda x: x.split(","), txt.splitlines())
        to_return = []
        for line in lines:
            id = int(line[1])
            speed = float(line[3])
            cat = line[2]
            seg = ROAD_SEG_CAT_DICT[id]
            to_return.append(
                {
                    "coord1":seg.get_start_coord(),
                    "coord2":seg.get_end_coord(),
                    "cat":cat,
                    "speed": speed,
                    "id": id
                }
            )
        return to_return

"example of using TrafficImporter"
def import_all():
    importer = AnotherAutoTrafficImporter()
    from os import listdir
    from os.path import isfile, join
    mypath = "D:/fyp/data_repo/typical"
    filenames = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    for filename in filenames:
        importer.import_data(src_txt_name=join(mypath, filename), traffic_name="[T]" + filename[:-4])
        print ("{} imported!".format(os.path.split(filename)[1][:-4]))

"example of using TrafficImporter"
def test_import():
    filename = "D:/fyp/data_repo/typical/imported/0T00-00.txt"
    importer = AnotherAutoTrafficImporter()
    importer.import_data(src_txt_name=filename, traffic_name="[T]0T00-00")


if __name__ == "__main__":
    # t = Traffic.objects.get(note="[T]0T00-00")
    # t.delete()
    test_import()
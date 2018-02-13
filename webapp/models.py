import json

from django.db import models
from misc.distance_calc import DistanceCalc

class Bounds(models.Model):
    """
    Used to describe the bounding box of a set of data points
    """
    north = models.FloatField()
    south = models.FloatField()
    east = models.FloatField()
    west = models.FloatField()

    def __unicode__(self):
        return "e:{},w:{},s:{},n:{}".format(self.east,self.west,self.south,self.north)

# models for traffic data
class RoadNetwork(models.Model):
    "One RoadNetwork is split into many RoadSegGrid"
    bounds = models.OneToOneField(Bounds)
    x_grid = models.IntegerField(default=10) # number of grids horizontally
    y_grid = models.IntegerField(default=10) # number of grids vertically
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

    def create_seg_grids(self):
        for x in range(self.x_grid):
            for y in range(self.y_grid):
                RoadSegGrid.objects.create(
                    x = x,
                    y = y,
                    road_network = self
                )

    def store_road_seg(self,seg):
        "seg is {coords,name,id,cat}"
        # check within bounds
        coords = seg["coords"]
        if (self._out_of_bound(coords[0]) or self._out_of_bound(coords[1])):
            raise Exception("segment[{}] coordinate is out of road network's bound".format(seg["id"]))
        # save seg
        road_seg_obj = RoadSeg.objects.create(
            id = seg["id"],
            category = RoadSeg.cat_long_to_short(seg["cat"]),
            name = seg["name"],
            start_lng = coords[0][0],
            start_lat = coords[0][1],
            end_lng = coords[1][0],
            end_lat = coords[1][1]
        )
        # locate grids
        grid_indexes = [self._get_grid_index(coords[0]),self._get_grid_index(coords[1])]
        # associate grids with segs
        for index in grid_indexes:
            road_seg_obj.road_seg_grid.add(self.roadseggrid_set.get(x=index[0],y=index[1]))
        road_seg_obj.save()

    def _get_grid_index(self,point):
        x_grid_size = (self.bounds.east - self.bounds.west) / self.x_grid
        y_grid_size = (self.bounds.north - self.bounds.south) / self.y_grid
        if (point[0]==self.bounds.east):
            x = self.x_grid - 1
        else:
            x = int((point[0]-self.bounds.west) / x_grid_size)
        if (point[1]==self.bounds.north):
            y = self.y_grid - 1
        else:
            y = int((point[1]-self.bounds.south) / y_grid_size)
        return (x,y)

    def _out_of_bound(self,point):
        return (point[0] < self.bounds.west or point[0] > self.bounds.east) or (point[1] < self.bounds.south or point[1] > self.bounds.north)

    def get_nearest_segs(self,lng,lat,cats):
        "return a [seg_obj,...],dist"
        grid_index = self._get_grid_index([lng,lat])
        candidates = self._get_candidate_segs(center_grid_index=grid_index,cats=cats)
        best_candidates = self._get_best_candidates(lng=lng,lat=lat,candidates=candidates)
        return best_candidates,DistanceCalc.minimum_distance(v=best_candidates[0].get_start_coord(),w=best_candidates[0].get_end_coord(),p=[lng,lat])

    def _get_best_candidates(self,lng,lat,candidates):
        "return a list of candidates with min dist"
        min_ls = []
        min_id_ls = [] # prevent the same segment being included twice
        min_dist = 1E6
        for candidate in candidates:
            dist = DistanceCalc.minimum_distance(
                v=candidate.get_start_coord(),
                w=candidate.get_end_coord(),
                p=[lng, lat]
            )
            if (dist < min_dist):
                min_dist = dist
                min_ls = [candidate]
                min_id_ls = [candidate.id]
            elif (DistanceCalc.isclose(dist,min_dist) and (candidate.id not in min_id_ls)):
                min_ls.append(candidate)
                min_id_ls.append(candidate.id)
        return min_ls


    def _get_candidate_segs(self,center_grid_index,cats):
        seg_ls = []
        # candidate segs are the segs in the center grid or the grids around the center grids
        ctr_x,ctr_y = center_grid_index
        x_ls = [ctr_x]; y_ls = [ctr_y]
        if (ctr_x>0): x_ls.append(ctr_x-1)
        if (ctr_x<self.x_grid-1): x_ls.append(ctr_x+1)
        if (ctr_y>0): y_ls.append(ctr_y-1)
        if (ctr_y < self.y_grid - 1): y_ls.append(ctr_y + 1)
        for x in x_ls:
            for y in y_ls:
                grid = self.roadseggrid_set.get(x=x,y=y)
                seg_ls.extend(grid.roadseg_set.filter(category__in = cats))

        return seg_ls


class RoadSegGrid(models.Model):
    x = models.IntegerField()  # grid index
    y = models.IntegerField()  # grid index
    road_network = models.ForeignKey(RoadNetwork)


class RoadSeg(models.Model):
    "information of a road segment"
    id = models.CharField(max_length=200, primary_key=True)
    road_seg_grid = models.ManyToManyField(RoadSegGrid) # one seg can belong to multiple grid
    category = models.CharField(max_length=200,choices=[
        ["A","A"],["B","B"],["C","C"],["D","D"],["E","E"],["N","N"],["S","S"]
    ])
    name = models.CharField(max_length=500)
    start_lng = models.FloatField()
    start_lat = models.FloatField()
    end_lng = models.FloatField()
    end_lat = models.FloatField()

    def __unicode__(self):
        return "Name:{},Id:{}".format(self.name,self.id)

    def get_full_desc(self):
        return "Name:{}, Id:{}, Start:[{},{}], End:[{},{}]".format(self.name,self.id,self.start_lng,self.start_lat,self.end_lng,self.end_lat)

    def get_start_coord(self): return [self.start_lng,self.start_lat]

    def get_end_coord(self): return [self.end_lng,self.end_lat]

    def get_coords(self): return [self.get_start_coord(),self.get_end_coord()]

    def get_orientation(self):
        v = "N" if self.start_lat < self.end_lat else "S"
        h = "E" if self.start_lng < self.end_lng else "W"
        return v+h

    @staticmethod
    def cat_long_to_short(catstr):
        "convert long category name(e.g. CATA) to short form(e.g. A)"
        if (catstr.find("CAT")!=-1 and catstr!="NCAT"): # CATA,CATB,CATC,CATD,CATE
            return catstr[3:]
        elif (catstr == "NCAT"):
            return "N"
        elif (catstr.find("SLIP")!=-1):
            return "S"
        else:
            raise Exception("{} is not a supported category".format(catstr))

class Traffic(models.Model):
    recorded_time = models.DateTimeField(null=True) # this is only used for "history" traffic
    note = models.CharField(max_length=50,unique=True)
    speed_records = models.TextField(default="") # in the format of roadSegId,speed
    type = models.CharField(max_length=50,choices=[
        ("typical","typical"),
        ("history","history")
    ],default="history")

    def __unicode__(self):
        return self.note

    def get_seg_speed(self,seg_id):
        "look up the speed of a particular road segment"
        record = filter(lambda x:x.split(",")[0]==seg_id,self.speed_records.splitlines())
        if (len(record) == 0):
            raise Exception("No speed record for seg {} in traffic {}".format(seg_id,self.note))
        return float(record[0].split(",")[1])

class TrafficLayer(models.Model):
    disp_level = models.IntegerField() # TODO: this is deprecated, can be removed
    traffic = models.ForeignKey(Traffic)
    category = models.CharField(
        choices=[
            ("A","A"),
            ("B", "B"),
            ("C", "C"),
            ("D", "D"),
            ("E", "E"),
            ("S", "S"),
            ("N", "N")
        ], max_length=5
    )

    def __unicode__(self):
        return "CAT{} Level {} for {}".format(self.category,self.disp_level,self.traffic)

class TrafficeLayerPiece(models.Model):
    "oontains the real traffic data"
    traffic_layer = models.ForeignKey(TrafficLayer)
    num_records = models.IntegerField(null=True) #TODO: this can be removed
    piece_num = models.IntegerField() #TODO: this is deprecated, can be removed
    p_x = models.IntegerField(default=0)
    p_y = models.IntegerField(default=0)
    bounds = models.OneToOneField(Bounds,null=True) #TODO: this is deprecated, can be removed
    raw_data = models.TextField() # should be in the format of start_coord,end_coord,speed
    raw_data_cutoff = models.CharField(max_length=200) # stores index that divides slow, medium, high speed traffic
    json_data = models.TextField()

    def __unicode__(self):
        return "Piece {} ({})".format(self.piece_num,self.traffic_layer)

    def recalc_json_data(self,width=2.5,opacity=0.7,speed_to_color=None,save=True):
        "recalculate and store json_data from raw_data"
        self.json_data = self.get_json_data(width=width,opacity=opacity,speed_to_color=speed_to_color)
        if save: self.save()

    def get_json_data(self,width=1.5,opacity=0.7,speed_to_color=None,include_property=True):
        if (self.json_data): return self.json_data
        # if json data is not saved yet, compute from raw data
        speed_to_color_func = speed_to_color if speed_to_color else TrafficeLayerPiece.default_speed_to_color
        lines = self.raw_data.splitlines()
        features = self._get_geojson(lines=lines,include_property=include_property,width=width,opacity=opacity,speed_to_color=speed_to_color_func)

        json_data = {
            "type": "FeatureCollection",
            "features": features
        }
        return json.dumps(json_data)

    # return a dict of geojson features: {0:[],1:[],2:[]}
    def get_grouped_features(self):
        lines = self.raw_data.splitlines()
        cutoffs = self.raw_data_cutoff[1:]
        datalines = lines[1:]
        cutoff20 = int(cutoffs.split(",")[0]); cutoff40 = int(cutoffs.split(",")[1])
        slow = datalines[:cutoff20]
        medium = datalines[cutoff20:cutoff40]
        fast = datalines[cutoff40:]
        return {
            0: self._get_geojson(slow,include_property=False),
            1: self._get_geojson(medium,include_property=False),
            2: self._get_geojson(fast,include_property=False)
        }

    # return list of features from data lines
    def _get_geojson(self,lines,include_property=True,width=1.5,opacity=0.7,speed_to_color=None):
        features = []  # list of json obj
        speed_to_color_func = speed_to_color if speed_to_color else TrafficeLayerPiece.default_speed_to_color
        for line in lines:
            coord1 = [float(line.split(",")[0]), float(line.split(",")[1])]
            coord2 = [float(line.split(",")[2]), float(line.split(",")[3])]
            speed = float(line.split(",")[4])
            if (include_property):
                feature = {"geometry": {"type": "LineString",
                                        "coordinates": [coord1, coord2]}, "type": "Feature",
                           "properties": {"stroke": speed_to_color_func(speed), "stroke-width": width,
                                          "stroke-opacity": opacity}}
            else:
                feature = {"geometry": {"type": "LineString",
                                        "coordinates": [coord1, coord2]}, "type": "Feature"}
            features.append(feature)
        return features

    @staticmethod
    def default_speed_to_color(speed):
        if (speed < 20): return "#ff0a0a" # red
        elif (speed < 40): return "#ffd60a" # yellow
        else: return "#1aff0a" # green


# models for message data
class Message(models.Model):
    recorded_time = models.DateTimeField()
    num_points = models.IntegerField(default=0) #TODO: this is deprecated, can be removed
    note = models.CharField(max_length=50,unique=True)

    def __unicode__(self):
        if (self.note):
            return self.note
        else:
            return "Recorded on {}".format(self.recorded_time)

class MessageLevel(models.Model):
    disp_level = models.IntegerField() #TODO: this is deprecated, can be removed
    category = models.CharField(
        choices=[
            ("A", "A"),
            ("B", "B"),
            ("C", "C"),
        ], max_length=2
    )
    message = models.ForeignKey(Message)

    class Meta:
        unique_together = (("category","message"),)

    def __unicode__(self):
        return "Level {} for {}".format(self.disp_level,self.message)

class MessageLevelPiece(models.Model):
    "contains the real message data"
    bounds = models.OneToOneField(Bounds,null=True) #TODO: this is deprecated, can be removed
    p_x = models.IntegerField(default=0)
    p_y = models.IntegerField(default=0)
    num_points = models.IntegerField(default=0) #TODO: this is deprecated, can be removed
    point_size = models.IntegerField(default=20) #TODO: this is deprecated, can be removed
    raw_data = models.TextField()
    json_data = models.TextField(null=True, blank=True)
    message_level = models.ForeignKey(MessageLevel)

    def __unicode__(self):
        return "Piece for {}".format(self.message_level)


class Heatmap(models.Model):
    recorded_time = models.DateTimeField(null=True)
    raw_data = models.TextField(null=True,blank=True)
    json_data = models.TextField(null=True, blank=True)
    note = models.CharField(max_length=50,unique=True)

    def __unicode__(self):
        return self.note
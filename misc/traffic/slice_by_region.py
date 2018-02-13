"""
Utility for slicing traffic into spatial grids, used in import_traffic
"""
import json
import _collections

class TrafficDataSlicer(object):
    "used for slicing traffic data by region"
    DEFAULT_X_SLICE_NO = 4
    DEFAULT_Y_SLICE_NO = 4

    def create_slices_from_file(self, filename):
        obj = json.loads(open(filename).read())
        return self.create_slices_from_ls(obj["features"])

    def create_slices_from_ls(self,ls,bounds=None,x_slice_in=None,y_slice_in=None,get_coords=None):
        "return {0:[],1:[]...}"
        file_bounds = bounds if bounds else self.get_bounds_from_json(ls)
        x_slice_no = x_slice_in if x_slice_in else self.DEFAULT_X_SLICE_NO
        y_slice_no = y_slice_in if y_slice_in else self.DEFAULT_Y_SLICE_NO
        x_slice_size = (file_bounds["r"] - file_bounds["l"]) / x_slice_no
        y_slice_size = (file_bounds["t"] - file_bounds["b"]) / y_slice_no
        # calculate slice bounds
        slice_bounds = {}
        for y in range(y_slice_no):
            for x in range(x_slice_no):
                slice_id = y * x_slice_no + x
                slice_bounds[slice_id] = {
                    "b": file_bounds["b"] + y * y_slice_size,
                    "t": file_bounds["b"] + (y + 1) * y_slice_size,
                    "l": file_bounds["l"] + x * x_slice_size,
                    "r": file_bounds["l"] + (x + 1) * x_slice_size
                }
        # slice the features into area of different bounds
        features = ls
        feature_slices = _collections.defaultdict(list)
        for feature in features:
            coordinates = get_coords(feature) if get_coords else feature["geometry"]["coordinates"]
            # see which slice this feature fits in
            for key, value in slice_bounds.items():  # key is the slice id
                if (self.is_in_bound(coord=coordinates, bound=value)):
                    feature_slices[key].append(feature)
                    break
        return feature_slices

    def is_in_bound(self, coord, bound):
        #TODO: check whether the coordinate fits in the bound
        start,end = coord[0],coord[1]
        if (self._is_pnt_in_bound(start,bound) or self._is_pnt_in_bound(end,bound)):
            return True
        return False

    def _is_pnt_in_bound(self,point,bound):
        return (point[0]<=bound['r'] and point[0]>=bound['l'] and point[1]>=bound['b'] and point[1]<=bound['t'])

    def get_bounds_from_json(self, features):
        coordinate_tuples = [f["geometry"]["coordinates"] for f in features]
        coordinates = [c[0] for c in coordinate_tuples]
        coordinates.extend([c[1] for c in coordinate_tuples])
        return self.get_bounds_from_coords(coordinates)

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



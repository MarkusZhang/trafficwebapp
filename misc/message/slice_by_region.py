"""
Utility for cutting message points into spatial grids, this is used in import_message
"""
import json
import _collections

class MessageDataSlicer(object):
    "used for slicing message data by region"
    DEFAULT_X_SLICE_NO = 4
    DEFAULT_Y_SLICE_NO = 4

    def create_slices_from_file(self, filename):
        lines = open(filename).readlines()
        return self.create_slices_from_ls(lines)

    def create_slices_from_ls(self, lines, bounds=None, in_x_slice=None, in_y_slice=None):
        file_bounds = bounds if bounds else self.get_bounds(lines)
        x_slice_no = in_x_slice if in_x_slice else self.DEFAULT_X_SLICE_NO
        y_slice_no = in_y_slice if in_y_slice else self.DEFAULT_Y_SLICE_NO
        x_slice_size = (file_bounds["r"] - file_bounds["l"]) / x_slice_no
        y_slice_size = (file_bounds["t"] - file_bounds["b"]) / y_slice_no
        # calculate slice bounds
        slice_bounds = {}
        for y in range(x_slice_no):
            for x in range(y_slice_no):
                slice_bounds["{},{}".format(x, y)] = {
                    "b": file_bounds["b"] + y * y_slice_size,
                    "t": file_bounds["b"] + (y + 1) * y_slice_size,
                    "l": file_bounds["l"] + x * x_slice_size,
                    "r": file_bounds["l"] + (x + 1) * x_slice_size
                }
        # slice the features into area of different bounds
        message_slices = _collections.defaultdict(list)
        for line in lines:
            if (len(line.split("\t")) >= 2):
                coordinate = [float(line.split("\t")[0]), float(line.split("\t")[1])]
                # see which slice this feature fits in
                for key, value in slice_bounds.items():  # key is the slice id
                    if (self.is_in_bound(point=coordinate, bound=value)):
                        message_slices[key].append(line)
                        print ("one message put in bound {}".format(key))
                        break
        return message_slices

    def is_in_bound(self, point, bound):
        return (point[0] <= bound['r'] and point[0] >= bound['l'] and point[1] >= bound['b'] and point[1] <= bound['t'])

    def get_bounds(self,lines):
        coordinates = [[float(line.split("\t")[0]),float(line.split("\t")[1])] for line in lines if len(line.split("\t"))>=2]
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




def test():
    slicer = MessageDataSlicer()
    slices = slicer.create_slices_from_file(filename="D:/fyp/data_repo/message/slotmsg_6-7-30.txt")
    print (slices)

if (__name__ == "__main__"):
    test()
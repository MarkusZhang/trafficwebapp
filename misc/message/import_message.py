"""
Utility for importing message files into database
, the message file should contain lines with the format "103.67835\t1.32451\t1"
"""
import sys
import django
import os
from django.db.transaction import atomic

"you might need to change the path here to your project directory"
sys.path.extend(['D:/fyp/fypsite'])
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fypsite.settings")
django.setup()

from slice_by_region import MessageDataSlicer
from webapp.models import Message,MessageLevelPiece,MessageLevel
from datetime import datetime


class MessageImporter(object):

    CAT_TO_DISPLEVEL = {
        "A":12,
        "B":14,
        "C":16
    }

    @atomic
    def import_message(self, source_name, msg_name):
        "data_by_cat is a dict {'A':{...},'B':{...}}"
        # create Message
        msg = Message.objects.create(
            recorded_time = datetime.now(),
            num_points = 0,
            note = msg_name
        )

        print("message obj {} created!".format(msg_name))
        # create levels
        for cat in ["A","B","C"]:
            # create level
            level = MessageLevel.objects.create(
                category = cat,
                message = msg,
                disp_level = self.CAT_TO_DISPLEVEL[cat]
            )
            # create pieces
            slicer = MessageDataSlicer()
            slices = slicer.create_slices_from_file(filename=self.get_msg_filename(cat=cat, source_name=source_name))
            for piece_num,points_data in slices.items():
                MessageLevelPiece.objects.create(
                    raw_data = "".join(points_data),
                    point_size =self.get_point_size(cat=cat),
                    p_x = piece_num.split(",")[0],
                    p_y = piece_num.split(",")[1],
                    num_points = len(points_data),
                    message_level = level
                )
            print ("created message level {}".format(cat))


    def get_bounds(self,points):
        coordinates = [
                        [float(p.split("\t")[0]),float(p.split("\t")[1])]
                       for p in points
                        ]
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

        return {"t": max_lat, "b": min_lat, "l": min_lng, "r": max_lng}\


    def get_point_size(self,cat):
        d = {
            "A": 160,
            "B": 50,
            "C": 20
        }
        return d[cat]

    def get_msg_filename(self,cat,source_name):
        base_dir = "D:/fyp/data_repo/message/"
        if (cat == "A"):
            return base_dir + "{}_clusters_16.txt".format(source_name)
        elif (cat=="B"):
            return base_dir + "{}_clusters_4.txt".format(source_name)
        else:
            return base_dir + "{}.txt".format(source_name)


if (__name__ == "__main__"):
    importer = MessageImporter()
    importer.import_message(source_name="slotmsg_6-8-30",msg_name="slotmsg_6-8-30")
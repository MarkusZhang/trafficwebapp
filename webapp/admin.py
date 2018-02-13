from django.contrib import admin
from webapp.models import *

admin.site.register(Traffic)
admin.site.register(RoadNetwork)
admin.site.register(RoadSegGrid)
admin.site.register(RoadSeg)
admin.site.register(TrafficLayer)
admin.site.register(TrafficeLayerPiece)

admin.site.register(Message)
admin.site.register(MessageLevel)
admin.site.register(MessageLevelPiece)

admin.site.register(Bounds)

admin.site.register(Heatmap)
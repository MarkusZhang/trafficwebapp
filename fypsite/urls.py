from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
    url(r'^$', 'webapp.views.index', name='index'),

    url(r'^data/traffic-time$', 'webapp.views.get_available_time_for_traffic'),

    url(r'^data/tp$', 'webapp.views.get_traffic_piece'),
    url(r'^data/tname$', 'webapp.views.get_traffic_names'),
    url(r'^data/roadseg$', 'webapp.views.get_road_seg_data'),

    url(r'^data/heatmap$', 'webapp.views.get_heatmap'),
    url(r'^data/hname$', 'webapp.views.get_heatmap_names'),
    url(r'^data/heatmap_chkname', 'webapp.views.heatmap_check_name'),

    url(r'^data/msg$', 'webapp.views.get_message_piece'),
    url(r'^data/mname$', 'webapp.views.get_message_names'),
    url(r'^data/msg_chkname$', 'webapp.views.message_check_name'),

    url(r'^admin/',admin.site.urls),

                       )

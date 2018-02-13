import signal
import time
from datetime import date

# Create your views here.
from django.http import HttpResponse,HttpResponseRedirect,QueryDict,JsonResponse
from django.shortcuts import render_to_response,render
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from webapp.models import *
from django.utils import timezone

ROAD_NETWORK_SYMBOL = "Road-Segment"
CACHE_DICT = {} # for caching

def index(request):
    return HttpResponseRedirect("/static/index.html")

def get_traffic_piece(request):
    cat = request.GET["cat"]
    p_x = request.GET["px"]
    p_y = request.GET["py"]
    t_name = request.GET["name"]
    # look up the data in cache
    cache_key = "name:{},px:{},py:{},cat:{}".format(t_name,p_x,p_y,cat)
    if (cache_key in CACHE_DICT.keys()):
        return CACHE_DICT.get(cache_key)
    else:
        # return data according to traffic type
        if (t_name != ROAD_NETWORK_SYMBOL):
            type,name =  t_name.split("/")
            if (type == "typical"): # typical traffic
                response =  _get_traffic_data(t_name=_convert_typical_traffic_name(name=name),cat=cat,p_x=p_x,p_y=p_y,type="typical")
            else: # history traffic
                response = _get_traffic_data(t_name=name,cat=cat,p_x=p_x,p_y=p_y,type="history")
        else:
            response = _get_traffic_data(t_name=t_name, cat=cat, p_x=p_x, p_y=p_y)

        # cache it and return
        CACHE_DICT[cache_key] = response
        return response

def _get_traffic_data(t_name,cat,p_x,p_y,type=None):
    "Returns a JSON response"
    # retrieve Traffic object
    if (type):
        traffic = Traffic.objects.get(note=t_name,type=type)
    else:
        traffic = Traffic.objects.get(note=t_name)

    try:
        # retrieve TrafficLayerPiece data
        layer = traffic.trafficlayer_set.filter(category=cat)[0]
        piece = layer.trafficelayerpiece_set.get(p_x=p_x, p_y=p_y)
        grouped_features = piece.get_grouped_features()
        return JsonResponse(data={"features":grouped_features})
    except Exception as e:
        print ("Error: {}".format(e.message))
        return JsonResponse(data={"features": {
            0:[],1:[],2:[]
        }})

def _convert_typical_traffic_name(name):
    "convert typical traffic name to the format used in database"
    DAY_DICT = {
        "sunday":0,"monday":1,"tuesday":2,"wednesday":3,"thursday":4,"friday":5,"saturday":6
    }
    day,time_index = name.split("T")
    day_str = DAY_DICT[day]
    hour = int(time_index) / 4
    minutes =  (int(time_index) % 4) * 15
    return "[T]{}T{:02d}-{:02d}".format(day_str,hour,minutes)

def get_traffic_names(request):
    names = [t.note for t in Traffic.objects.all()]
    json_obj = {
        "names":names
    }
    return JsonResponse(data=json_obj)


def get_heatmap(request):
    type,name = request.GET["name"].split("/")
    heatmap = Heatmap.objects.get(note=name)
    return HttpResponse(heatmap.raw_data)

def get_message_piece(request):
    # retrieve Message object
    cat = request.GET["cat"]
    p_x = request.GET["px"]
    p_y = request.GET["py"]
    t_name = request.GET["name"]
    type,name = t_name.split("/")
    message = Message.objects.get(note=name)
    try:
        # retrieve MessageLayerPiece data
        layer = message.messagelevel_set.get(category=cat)
        piece = layer.messagelevelpiece_set.get(p_x = p_x, p_y = p_y)
        return HttpResponse(piece.raw_data)
    except:
        return HttpResponse("")


def get_message_names(request):
    names = [t.note for t in Message.objects.all()]
    json_obj = {
        "names": names
    }
    return JsonResponse(data=json_obj)

def get_road_seg_data(request):
    "retrieve detailed traffic information of the road nearest to the request point"
    MAX_DIST = 100
    lng = float(request.GET["lng"])
    lat = float(request.GET["lat"])
    traffic_name = request.GET["name"]
    type, name = traffic_name.split("/")
    if (type=="typical"): name = _convert_typical_traffic_name(name)
    cats = request.GET["cats"].split(",") # cats concatenated using comma
    # find out the nearest road segment no farther than 100 m
    network = RoadNetwork.objects.all()[0]
    segs,dist = network.get_nearest_segs(lng=lng,lat=lat,cats=cats)
    traffic = Traffic.objects.get(note=name,type=type)

    if (dist > MAX_DIST):
        return JsonResponse(data={})
    else:
        # return the detailed road and traffic data
        seg_jsons = []
        for seg in segs:
            seg_jsons.append({
            "start_coord":seg.get_start_coord(),
            "end_coord":seg.get_end_coord(),
            "category":seg.category,
            "name": seg.name,
            "id": seg.id,
            "orientation": seg.get_orientation(),
            "speed":traffic.get_seg_speed(seg.id)
        })

        return JsonResponse(data={"segs":seg_jsons })


def get_available_time_for_traffic(request):
    "return the available history traffic time"
    traffic_ls = Traffic.objects.exclude(note="Road-Segment").exclude(type="typical")
    response_dict = {} # in the format of year:{ month: { day: [time1,time2...]
    for traffic in traffic_ls:
        t = traffic.recorded_time
        t = timezone.localtime(t)
        _add_time_to_dict(t=t, dict=response_dict)
    return JsonResponse(data=response_dict)

def _add_time_to_dict(t, dict):
    time_str = "{:02d}:{:02d}:{:02d}".format(t.hour, t.minute, t.second)

    if (t.year not in dict.keys()):
        dict[t.year] = {
            t.month: {
                t.day: [time_str]
            }
        }
    else:  # t.year is in dict
        year_dict = dict[t.year]
        if (t.month not in year_dict.keys()):
            dict[t.year][t.month] = {
                t.day: [time_str]
            }
        else:  # t.month is in dict
            month_dict = year_dict[t.month]
            if (t.day not in month_dict.keys()):
                dict[t.year][t.month][t.day] = [time_str]
            else:  # t.day is in dict
                dict[t.year][t.month][t.day] = sorted(dict[t.year][t.month][t.day] + [time_str])

# return error if message doesn't exist
def message_check_name(request):
    name = request.GET["name"]
    Message.objects.get(note=name)
    return JsonResponse(data={
        "exist":"yes"
    })

# return error if heatmap doesn't exist
def heatmap_check_name(request):
    name = request.GET["name"]
    Heatmap.objects.get(note=name)
    return JsonResponse(data={
        "exist": "yes"
    })

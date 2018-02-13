/*
    Service for drawing traffic conditions (color lines) on map
 */
app.factory('TrafficService', function ($rootScope,UrlService,SlicingService,$http,trafficServiceConfig) {

    var displayLayers = [];
    var hiddenLayers = []; //TODO: we may set an upper limit for this

    var service = {
        updateMap: updateMap,
        clearTraffic:clearTraffic,
        queryRoadSeg:queryRoadSeg
    };

    ////////////////////////////////////
    //  service static data
    var configs = trafficServiceConfig.categoryConfig;
    var SPEEDS = trafficServiceConfig.speeds;

    return service;

    ////////////////////////////////////////////
    // public function declarations
    /**
     * Redraw traffic on the map
     * @param map: map object
     * @param zoom: zoom level ,float
     * @param bounds: an object {e:..,w:..,n:..,s:..}
     * @param traffic_name
     */
    function updateMap(map, zoom, bounds,traffic_name) {
        // remove or add traffic data to map
        requiredCats = getRequiredCats(zoom,configs);
        requiredSlices = SlicingService.getRequiredSlices(bounds);
        requiredLayers = [];
        for (i = 0; i < requiredCats.length; i++) {
            cat = requiredCats[i];
            for (j = 0; j < requiredSlices.length; j++) {
                requiredLayers.push(traffic_name + "," + cat +"," + requiredSlices[j][0] + "," + requiredSlices[j][2]);
            }
        }
        addRequiredLayers(requiredLayers,map,traffic_name);
        hideNonRequiredLayers(requiredLayers,map);
    }

    // get information about the nearest road segment
    function queryRoadSeg(lng, lat,zoom,traffic_name,map) {
        requiredCats = getRequiredCats(zoom,configs);
        catsStr = requiredCats.join(",");
        var callback_func = function (data) {
            if (data && data.segs){
                // display the road segs on map
                var segs = data.segs;
                geometries = [];
                for (var i=0; i < segs.length;i++){
                    seg = segs[i];
                    geometries.push(
                        {"geometry": {"type": "LineString", "coordinates": [seg.start_coord, seg.end_coord]}, "type": "Feature"}
                    );
                }
                features = {"type": "FeatureCollection", "features": geometries};
                map.addLayer({
                    "id": "marker-line",
                    "type": "line",
                    "source": {
                        "type": "geojson",
                        "data": features
                    },
                    "paint":{
                        "line-color":trafficServiceConfig.markerPaint["color"],
                        "line-width": trafficServiceConfig.markerPaint["width"]
                    }
                });
                // show seg info
                return "The road seg:\nName: " + seg.name + "\nId:" + seg.id + "\nCategory:" + seg.category + "\nSpeed:" + seg.speed;
            }else{
                return "No nearby road segs found";
            }
        };

        // send http request
        return $http
        .get(UrlService.getRoadSegInfo(lng,lat,catsStr,traffic_name), {})
        .success(callback_func)
        .error(function (data) {
            alert("failed to load road seg info for " + lng + "," + lat);
        });
    }

    /**
     * Remove all traffic layers from map
     * @param map: map object
     */
    function clearTraffic(map) {
        for (var i = 0; i < displayLayers.length; i++) {
            _removeLayerSet(map,displayLayers[i]);
        }
        for (var j = 0; j < hiddenLayers.length; j++) {
            _removeLayerSet(map,hiddenLayers[j]);
        }
        displayLayers = [];
        hiddenLayers = [];
    }
    

    function _getLayerId(prefix, speed) {
        return prefix + "--" + speed;
    }

    /**
     * Generate a callback function that draws traffic after getting required data
     * @param basename: basename for naming the traffic layers
     * @param map: map object
     * @returns {Function}
     * @private
     */
    function _getSuccessCallback(basename,map) {
        // get mapping from speed to display color
        SPEED_TO_COLOR = trafficServiceConfig.speedToColor;

        return function (data) {
            var featuresDict = data.features;

            // draw one layer for each speed
            for (var i = 0; i < SPEEDS.length; i++) {
                // display different speed in different color
                var speed = SPEEDS[i];
                var features = featuresDict[speed];
                var layerId = _getLayerId(basename,speed);

                map.addLayer({
                    "id": layerId,
                    "type": "line",
                    "source": {
                        "type": "geojson",
                        "data": {
                            "type": "FeatureCollection",
                            "features": features
                        }
                    },
                    "paint": {
                        "line-color": SPEED_TO_COLOR[speed],
                        "line-width": trafficServiceConfig.trafficLinePaint["width"],
                        "line-opacity":trafficServiceConfig.trafficLinePaint["opacity"]
                    }
                });

            }

        }
    }

    /**
     *
     * @param requiredLayers: list of layer ids
     * @param map; map object
     * @param traffic_name
     */
    function addRequiredLayers(requiredLayers,map,traffic_name){
        for (var i = 0; i < requiredLayers.length; i++) {
            if (displayLayers.indexOf(requiredLayers[i])==-1){ // not in display yet, need to load
                thisLayer = requiredLayers[i];
                // check if the layer is hidden
                if (hiddenLayers.indexOf(thisLayer)!=-1){
                    // unhide it if it is hidden
                    _unhideLayerSet(map,thisLayer);
                    displayLayers.push(thisLayer);
                    hiddenLayers = _removeItemFromArray(hiddenLayers,thisLayer);
                }
                else{
                    // not in hidden layers, need to fetch from server
                    var successCallback = _getSuccessCallback(thisLayer,map);
                    $http
                        .get(_getRequestTrafficPieceUrl(thisLayer,traffic_name), {})
                        .success(successCallback)
                        .error(function (e) {
                            console.log(e);
                        });
                    // record mapping
                    displayLayers.push(thisLayer);
                }

            }
        }
    }

    function _getRequestTrafficPieceUrl(layer,traffic_name){
        values = layer.split(",");
        cat = values[1];
        px = values[2];
        py = values[3];
        return UrlService.getTrafficPiece(traffic_name,cat,px,py);
    }


    /**
     * @param requiredLayers: list of layer ids
     * @param map: map object
     */
    function hideNonRequiredLayers(requiredLayers,map){
        layersToHide = jQuery.grep(displayLayers, function(value) {
            return requiredLayers.indexOf(value)==-1;
        });

        // hide the non-required layers
        for(i=0; i<layersToHide.length; i++){
            layerToHide = layersToHide[i];
            _hideLayerSet(map,layerToHide);
            hiddenLayers.push(layerToHide);
        }

        // remove hidden layers from displayLayers
        displayLayers = jQuery.grep(displayLayers, function(value) {
            return layersToHide.indexOf(value)==-1;
        });
    }

    // given layer id, hide all layers for all speeds
    function _hideLayerSet(map,layerId)
    {
        for (var i = 0; i < SPEEDS.length; i++) {
            actualLayerId = _getLayerId(layerId,SPEEDS[i]);
            map.setLayoutProperty(actualLayerId, 'visibility', 'none');
        }
    }

    // given layer id, remove all layers for all speeds
    function _removeLayerSet(map, layerId) {
        for (var i = 0; i < SPEEDS.length; i++) {
            actualLayerId = _getLayerId(layerId,SPEEDS[i]);
            map.removeLayer(actualLayerId);
            map.removeSource(actualLayerId);
        }
    }

    // given layer id, show layers for all speeds
    function _unhideLayerSet(map, layerId) {
        for (var i = 0; i < SPEEDS.length; i++) {
            actualLayerId = _getLayerId(layerId,SPEEDS[i]);
            map.setLayoutProperty(actualLayerId, 'visibility', 'visible');
        }
    }

    // return list of categories (e.g. ["A","B"])
    function getRequiredCats(zoom,config){
        zoomLevel = Math.round(zoom);
        if (zoomLevel<=config.minZoom){
            return config.defaultCat;
        }
        else if (zoomLevel>=config.maxZoom){
            return config.LevelToCats[config.maxZoom];
        }
        else{
            return config.LevelToCats[zoomLevel];
        }
    }

    // return the array with `item` removed
    function _removeItemFromArray(arr, item) {
        return jQuery.grep(arr, function(value) {
            return value != item;
        });
    }

});

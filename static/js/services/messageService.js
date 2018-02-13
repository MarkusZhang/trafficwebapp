/*
Service for drawing message points on map
 */
app.factory('MessageService', function ($http,UrlService,$rootScope,MessageSlicingService,messageServiceConfig) {

    var service = {
        updateMessage: updateMessage,
        clearMessage:clearMessage,
        addMessagePoints: addMessagePoints // for displaying user input data
    };

    var stateData = getStateData(); //TODO: change the way of updating to be consistent with traffic

    var configs = messageServiceConfig.categoryConfig;

    return service;

    //////////////////////////////////////
    // declarations of public functions
        /**
         * Redraw message points
         * @param message: map object
         * @param zoom: zoom level, float
         * @param bounds: an object {e:..,w:..,n:..,s:..}
         * @param message_name
         */
    function updateMessage(message,zoom,bounds,message_name){
        // compute layers that need to be displayed
        requiredCats = getRequiredCats(zoom,configs);
        if (requiredCats.length > 0){
            requiredSlices = MessageSlicingService.getRequiredSlices(bounds,requiredCats[0]);
        }
        else{
            requiredSlices = [];
        }

        requiredLayers = [];
        for (i = 0; i < requiredCats.length; i++) {
            cat = requiredCats[i];
            for (j = 0; j < requiredSlices.length; j++) {
                requiredLayers.push(cat+"," + requiredSlices[j][0] + "," + requiredSlices[j][2]);
            }
        }

        // remove layers that do not need to be displayed, add layers that need to be displayed
        addRequiredLayers(requiredLayers,stateData,message,message_name);
        removeNonRequiredLayers(requiredLayers,stateData,message);
    }

        /**
         * Remove all message layers from map
         * @param map: map object
         */
    function clearMessage(map) {
        layers = stateData.layersInDisplay;
        for (i = 0; i < layers.length; i++) {
            layerToHide = layers[i];
            try{
                map.removeLayer(stateData.nameToLayer[layerToHide] + "-green");
                map.removeLayer(stateData.nameToLayer[layerToHide] + "-red");
                map.removeSource(stateData.nameToLayer[layerToHide] + "-green");
                map.removeSource(stateData.nameToLayer[layerToHide] + "-red");
            }catch (err){

            }
            stateData.nameToLayer[layerToHide] = null;
            stateData.layersInDisplay = jQuery.grep(stateData.layersInDisplay, function(value) {
                return value != layerToHide;
            });
        }
    }

        /**
         *
         * @param map : base layer object
         * @param data_text : a multi-line text with each line in the format "lng,lat,color", color is either 0 or 1
         */
    function addMessagePoints(map,data_text) {
        drawMessagePoints("testpoints",data_text,"C",map);
    }

    ////////////////////////////////////////////
    ///  declarations of internal functions
        /**
         *
         * @param layer: layer id
         * @param data: lines in the format of "103.67835\t1.32451\t1"
         * @param cat: category ("A" or "B" or "C")
         * @param map: map object
         */
    function drawMessagePoints(layer,data,cat,map){
        radius = configs.radiusConfig[cat];
        var allText = data;
        var lines = allText.split('\n');
        var greenFeatures = [];
        var redFeatures = [];
        // prepare geojson to draw points
        for (var i = 0; i < lines.length; i++) {
            if (lines[i].length!=0){ // skip empty lines
                var results = lines[i].split("\t");
                var feature = {
                        "type":"Feature",
                        "geometry":{
                            "type":"Point",
                            "coordinates": [parseFloat(results[0]), parseFloat(results[1])]
                        }
                    };

                // group message points
                if (results[2] === '0') { // available taxi
                    greenFeatures.push(feature);
                } else {
                    redFeatures.push(feature);
                }
            }
        }

        // draw the points on map
        map.addLayer({
            "id": layer + "-green",
            "type": "circle",
            "source": {
                "type": "geojson",
                "data": {
                    "type": "FeatureCollection",
                    "features": greenFeatures
                }
            },
            "paint": {
                "circle-radius": radius,
                "circle-color": "#10ff00",
                "circle-opacity": messageServiceConfig.messageCirclePaint["opacity"]
            }
        });

        map.addLayer({
            "id": layer + "-red",
            "type": "circle",
            "source": {
                "type": "geojson",
                "data": {
                    "type": "FeatureCollection",
                    "features": redFeatures
                }
            },
            "paint": {
                "circle-radius": radius,
                "circle-color": "#ff0000",
                "circle-opacity": messageServiceConfig.messageCirclePaint["opacity"]
            }
        });


    }

    function getRequiredCats(zoom,config){
        zoomLevel = Math.round(zoom);
        if (zoomLevel<config.minZoom){
            return config.defaultCat;
        }
        else if (zoomLevel>config.maxZoom){
            return config.LevelToCats[config.maxZoom];
        }
        else{
            return config.LevelToCats[zoomLevel];
        }
    }

        /**
         * @param requiredLayers: array of layer ids
         * @param state: object {layersInDisplay:[..],nameToLayer:{}}
         * @param map: map object
         */
    function removeNonRequiredLayers(requiredLayers,state,map){
        // compute which layers to remove
        layersToHide = jQuery.grep(state.layersInDisplay, function(value) {
            return requiredLayers.indexOf(value)==-1;
        });
        layersRemoved = [];

        // hide those layers
        for(i=0; i<layersToHide.length; i++){
            layerToHide = layersToHide[i];
            try{
                map.removeLayer(state.nameToLayer[layerToHide] + "-red");
                map.removeLayer(state.nameToLayer[layerToHide] + "-green");
                map.removeSource(state.nameToLayer[layerToHide] + "-red");
                map.removeSource(state.nameToLayer[layerToHide] + "-green");
                state.nameToLayer[layerToHide] = null;
                layersRemoved.push(layerToHide);
            }
            catch (err){
                alert("Error: " + err);
            }
        }

        // update the state
        state.layersInDisplay = jQuery.grep(state.layersInDisplay, function(value) {
            return layersRemoved.indexOf(value)==-1;
        });
    }

    function getStateData() {
        // add messageService data field in if not there in rootScope
        if (!$rootScope.messageService){
            $rootScope.messageService = {
                nameToLayer:{
                },
                layersInDisplay: []
            }
        }
        return $rootScope.messageService;
    }

        /**
         * @param requiredLayers: array of layer ids
         * @param state: object {layersInDisplay:[..],nameToLayer:{}}
         * @param map: map object
         * @param message_name
         */
    function addRequiredLayers(requiredLayers,state,map,message_name){
        /* parameter map here is a message layer */
        for (var i = 0; i < requiredLayers.length; i++) {
            if (state.layersInDisplay.indexOf(requiredLayers[i])==-1){ // not in display yet, need to load
                thisLayer = requiredLayers[i];
                // send request
                values = thisLayer.split(",");
                cat = values[0];
                px = values[1];
                py = values[2];
                addOneLayer(map,cat,px,py,message_name,state,thisLayer);
            }
        }
    }

    function _getMessageCallback(layer_name,cat,px,py,map){
        return function (data) {
            var newLayer = layer_name;
            drawMessagePoints(newLayer,data,cat,map);
        }
    }

        /**
         * Draw one layer of points
         * @param map; map object
         * @param cat: "A" or "B" or "C"
         * @param px: int
         * @param py: int
         * @param message_name
         * @param state: object {layersInDisplay:[..],nameToLayer:{}}
         * @param curLayer: layer id
         */
    function addOneLayer(map,cat,px,py,message_name,state,curLayer){

        var callback_func = _getMessageCallback(curLayer,cat,px,py,map);

        var error_callback = function (data) {
            alert("Fail to load message" + curLayer);
            index = state.layersInDisplay.indexOf(curLayer);
            state.layersInDisplay.splice(index,1);
        };

        $http
        .get(UrlService.getMessagePiece(message_name,cat,px,py), {})
        .success(callback_func)
        .error(error_callback);

        state.layersInDisplay.push(curLayer);
        state.nameToLayer[curLayer] = curLayer;
    }
}
);
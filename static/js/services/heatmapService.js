/*
Service for drawing heatmap on the map
 */
app.factory('HeatmapService', function ($http,UrlService) {

    var service;
    service = {
        loadHeatmap: loadHeatmap,
        clearHeatmap: clearHeatmap
    };

    return service;

    /////////////////////////////////////////////////////
    // public functions declarations
    /**
     * Draw heatmap on the map
     * @param heatmap: map object
     * @param heatmap_name: selected name
     */
    function loadHeatmap(heatmap,heatmap_name) {
        // send ajax request
        $http
            .get(UrlService.getHeatmap(heatmap_name), {})
            .success(function (data) {
                drawHeatmap(heatmap,data);
            })
            .error(function (data) {
                alert("fail to load heatmap");
            });
    }


    function clearHeatmap(map) {
        map.removeLayer("heatmap-red");
        map.removeLayer("heatmap-green");
        map.removeLayer("heatmap-yellow");
        map.removeSource("heatmap-red");
        map.removeSource("heatmap-green");
        map.removeSource("heatmap-yellow");
    }


    ///////////////////////////////////////////////
    // declarations of hidden functions
    /**
     * @param map: map object
     * @param data: lines in the format of "103.111\t1.02\t1"
     */
    function drawHeatmap(map,data){
        var GREEN_CUTOFF = 1;
        var YELLOW_CUTOFF = 3;

        var allText = data;
        var lines = allText.split('\n');
        // split data points according to heat value
        var redPoints = [];
        var yellowPoints = [];
        var greenPoints = [];
        for (var i = 0; i < lines.length - 1; i++) {
            var results = lines[i].split("\t");
            var midLat = (parseFloat(results[2]) + parseFloat(results[4])) / 2;
            var midLng = (parseFloat(results[1]) + parseFloat(results[3])) / 2;
            var heat = parseFloat(results[6]);
            var cat = parseInt(results[5]);
            if (heat<=GREEN_CUTOFF) greenPoints.push([midLng,midLat,cat]);
            else if (heat<=YELLOW_CUTOFF) yellowPoints.push([midLng,midLat,cat]);
            else redPoints.push([midLng,midLat,cat]);
        }

        // draw points of different heat value using different color
        drawSingleHeatmapLayer(map,greenPoints,"green");
        drawSingleHeatmapLayer(map,redPoints,"red");
        drawSingleHeatmapLayer(map,yellowPoints,"yellow");
    }

    /**
     * @param map: map object
     * @param points: list of [lng,lat]
     * @param color: color str
     */
    function drawSingleHeatmapLayer(map, points,color) {
        // prepare the geojson
        features = [];
        for (var i = 0; i < points.length; i++) {
            var point = points[i];
            features.push({"type":"Feature","geometry": { "type": "Point", "coordinates": [point[0],point[1]] } });
        }

        // add to map
        map.addLayer({
            "id": "heatmap-" + color,
            "type": "circle",
            "source": {
				"type":"geojson",
				"data":{
					"type": "FeatureCollection",
					"features":features
				}
			},
            "paint": {
                "circle-color": color,
                "circle-radius": 25, //TODO: further split according to cat
                "circle-blur": 5,
                "circle-opacity": 0.9
            }
        });

    }

});
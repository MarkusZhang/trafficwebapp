var app = angular.module("mapApp",[]);

/*
    Main controller for the index page
 */
app.controller("mapCtrl",function ($scope,TrafficService,HeatmapService,MessageService,UrlService,$http,CtrlMsgService) {
    var vm = this;
    // state variables
    vm.isTesting = true; // Load Data option will be shown if this is true
    vm.isLoading = false; // loading icon will be shown if this is true
    vm.loadingMsg = "";
    vm.map = null;  // map GL object
    vm.mapStyle = "dark";

    vm.selected_item = {
        type: "typical",
        name: "sundayT0"
    };

    // vars for displaying detailed traffic information
    vm.cur_location_name = "";
    vm.road_seg_info = "";
    vm.pre_marker = null;

    // event handlers
    vm.loadInputMessage = loadInputMessage;
    vm.setMapStyle = setMapStyle;
    vm.resetMap = resetMap;

    // scope vars
    $scope.showTraffic = false;
    $scope.showHeatmap = false;
    $scope.showMessage = false;

    // init
    init();

    // scope event listeners for receiving broadcast
    $scope.$on("trafficSelected",function () {
        selected_time = CtrlMsgService.getMsg();
        if (selected_time.type != vm.selected_item.type || selected_time.name != vm.selected_item.name){
            _handleSelectionChange(selected_time);
        }
    });

    $scope.$on("loading",function () {
        loadingMsg = CtrlMsgService.getMsg();
        vm.isLoading = true;
        vm.loadingMsg = loadingMsg;
    }
    );

    $scope.$on("endloading",function () {
        vm.isLoading = false;
        vm.loadingMsg = "";
    });

    // scope event listeners for variable change
    $scope.$watch("showTraffic",function (newVal, oldVal) {
        if (newVal == true){
            success = _loadTrafficDisplay();
            if (!success) $scope.showTraffic = false;
        }else{ // remove traffic
            _removeTrafficDisplay();
        }
    });

    $scope.$watch("showMessage",function (newVal, oldVal) {
        if (newVal == true){
            _loadMessageDisplay();
        }else{ // remove
            _removeMessageDisplay();
        }
    });

    $scope.$watch("showHeatmap",function (newVal, oldVal) {
        if (newVal == true){
            _loadHeatmapDisplay();
        }else{ // remove
            _removeHeatmapDisplay();
        }
    });

    /**
     * Update map when time selection is changed
     * @param new_selection: an object {name:"",type:""}
     * @private
     */
    function _handleSelectionChange(new_selection) {
        vm.selected_item.name = new_selection.name;
        vm.selected_item.type = new_selection.type;
        vm.road_seg_info = "";
        _removeMarker();
        if($scope.showTraffic){
            _loadTrafficDisplay();
        }
        if($scope.showMessage){
            _removeMessageDisplay();
            _loadMessageDisplay();
        }
        if($scope.showHeatmap){
            _removeHeatmapDisplay();
            _loadHeatmapDisplay();
        }
    }


    // map object event listeners
    vm.map.on("zoomend",function(e){
       if ($scope.showTraffic) _loadTrafficDisplay();
        if ($scope.showMessage) _loadMessageDisplay();
    });

    vm.map.on("moveend",function (e) {
       if ($scope.showTraffic) _loadTrafficDisplay();
        if ($scope.showMessage) _loadMessageDisplay();
    });

    vm.map.on("click",function (e) {
        lat = e.lngLat['lat'];
        lng = e.lngLat['lng'];

        // remove old marker and place new marker
        _removeMarker();

        vm.map.addLayer({
            "id": "marker",
            "source": {
                "type": "geojson",
                "data":{
                    "type":"Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lng,lat]
                    }
                }

            },
            "type": "circle",
            "paint": {
                "circle-radius": 10,
                "circle-color": "#007cbf"
            }
        });

        // retrieve location information
        var callback_func = function (data) {
            if (data.features && data.features.length > 0){
                vm.cur_location_name = data.features[0]["place_name"];
            }else{
                vm.cur_location_name = "Unknown place";
            }
        };

        $http
        .get(UrlService.getLocationInfo(lng,lat), {})
        .success(callback_func)
        .error(function (data) {
            alert("failed to load location info for " + lng + "," + lat);
        });

        // retrieve road segment information
        if ($scope.showTraffic){
            TrafficService.queryRoadSeg(lng,lat,vm.map.getZoom(),_getCombinedSelectedItemName(),vm.map).success(
                function (data) {
                    segs = data.segs;
                    vm.road_seg_info = segs;
                }
            );
        }

    });

    ////////////////////////////////
    // function function declarations
    function loadInputMessage() {
        $text = $('textarea#inputData').val();
        MessageService.addMessagePoints(vm.map,$text);
    }

    // return true if loading is successful
    function _loadTrafficDisplay() {
        if (vm.selected_item.name == "" || vm.selected_item.name == null){
            alert("Time not selected");
            return false;
        }
        else{ // traffic name already selected
            zoom = vm.map.getZoom();
            name = _getCombinedSelectedItemName();
            TrafficService.updateMap(vm.map,zoom,_getMapBounds(vm.map),name);
            return true;
        }
    }

    function setMapStyle(style) {
        if (style != vm.mapStyle){
            vm.map.setStyle('mapbox://styles/mapbox/' + style + '-v9');
            vm.mapStyle = style;
        }
    }

    // remove all layers
    function resetMap() {
        TrafficService.clearTraffic(vm.map);
        MessageService.clearMessage(vm.map);
        HeatmapService.clearHeatmap(vm.map);
        vm.showTraffic = false;
        vm.showMessage = false;
        vm.showHeatmap = false;
        $("#showTrafficCheckbox").prop("checked",false);
        $("#showMessageCheckbox").prop("checked",false);
    }

    function init(){
        _initMap();
        // bind resize listener
        $( window ).resize(function() {
          _resizeMap();
        });

        _resizeMap();
    }


    ///////////////////////////////////////////////
    // private function declarations
    function _loadMessageDisplay() {
        if (vm.selected_item.name=="" || vm.selected_item.name==null){
            alert("Please select a time first");
            $scope.showMessage = false;
        }
        else{
            $http // check message availability
            .get(UrlService.getCheckMessageName(vm.selected_item.name), {})
            .success(function (data) {
                // message available, display it
                MessageService.updateMessage(vm.map,vm.map.getZoom(),_getMapBounds(vm.map),_getCombinedSelectedItemName());
            })
            .error(function (e) {
                alert("No message available for the selected time");
                $scope.showMessage = false;
            });
        }
        return true;
    }

    function _loadHeatmapDisplay() {
        if (vm.selected_item.name=="" || vm.selected_item.name==null){
            alert("Please select a time first");
            $scope.showHeatmap = false;
        }
        else{
            $http // check heatmap availability
                .get(UrlService.getCheckHeatmapName(vm.selected_item.name), {})
                .success(function (e) {
                    // heatmap available, display it
                    HeatmapService.loadHeatmap(vm.map,_getCombinedSelectedItemName());
                })
                .error(function (e) {
                    alert("No heatmap available for the selected time");
                    $scope.showHeatmap = false;
                });
        }
        return true;
    }

    // return true
    function _removeTrafficDisplay() {
        TrafficService.clearTraffic(vm.map);
        return true;
    }

    function _removeMessageDisplay() {
        MessageService.clearMessage(vm.map);
        return true;
    }

    function _removeHeatmapDisplay() {
        HeatmapService.clearHeatmap(vm.map);
        return true;
    }

    function _resizeMap(){
        var size = {
            width: window.innerWidth || document.body.clientWidth,
            height: window.innerHeight || document.body.clientHeight
        };
        $("#map").css("width",size.width - 220 + "px");
        $("#map").css("height",size.height - 150 + "px");
        vm.map.resize();
    }

    function _initMap(){
        var sgCenter = [103.82161,1.35433]; //TODO: put into a constant file
        mapboxgl.accessToken = 'pk.eyJ1IjoiZTEzMDAxNSIsImEiOiJjaXc3NWF1cmowMDFhMnRtaGZ6c2JjMTNtIn0.IJOewTUVt2aKE1oGyOKH3Q';
        vm.map = new mapboxgl.Map({
            container: 'map',
            style: 'mapbox://styles/mapbox/dark-v9',
            center: sgCenter,
            zoom: 11
        });

        vm.map.addControl(new mapboxgl.NavigationControl());
    }



    function _getMapBounds(map) {
        return {
                "n": map.getBounds().getNorth(),
                "s": map.getBounds().getSouth(),
                "e": map.getBounds().getEast(),
                "w": map.getBounds().getWest()
            }
    }

    function _getCombinedSelectedItemName() {
        if(vm.selected_item.type == null || vm.selected_item.name == null){
            alert("No item selected!");
        }
        else{
            return vm.selected_item.type + "/" + vm.selected_item.name;
        }
    }

    function _padZero(num) {
        if (Number(num)<10){
            return "0" + num;
        }
        else{
            return "" + num;
        }
    }

    function _removeMarker() {
        try{
            vm.map.removeLayer("marker");
            vm.map.removeLayer("marker-line");
            vm.map.removeSource("marker");
            vm.map.removeSource("marker-line");
        }catch (err){
        }
    }

    // convert the selected time to a name that can be used in http request
    function _formatSelectedTime(name) {
        if (vm.selected_item.type == "typical"){
            splitted = vm.selected_item.name.split("T");
            day = splitted[0];
            timeIndex = splitted[1];
            hour = Math.round(Number(timeIndex) / 4);
            minutes = Number(timeIndex) % 4 * 15;
            return day + " " + _padZero(hour) + ":" + _padZero(minutes);
        }else{
            splitted = vm.selected_item.name.split("T");
            return splitted[0] + " " + splitted[1];
        }
    }
});
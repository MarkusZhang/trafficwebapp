/**
 * Service for keeping urls
 */
app.factory('UrlService', function () {

    var urls = {};

    //var base = "http://localhost:8100/api/";
    var base = "/";
    //var base = "http://172.21.148.164/";

    urls.getHeatmap = getHeatmap;
    urls.getHeatmapNames = base + "data/hname";
    urls.getTrafficNames = base + "data/tname";
    urls.getMessageNames = base + "data/mname";
    urls.getCheckMessageName = getCheckMessageName;
    urls.getCheckHeatmapName = getCheckHeatmapName;
    urls.getTrafficAvailableTime = base + "data/traffic-time"; // get available time slots for traffic data
    urls.getTrafficPiece = getTrafficPieceUrl;
    urls.getTrafficWholeUrl = getTrafficWholeUrl;
    urls.getMessagePiece = getMessagePiece;
    urls.getLocationInfo = getLocationInfo;
    urls.getRoadSegInfo = getRoadSegInfo;

    return urls;

    ////////////////////////////////////////////
    /// public functions declarations
    function getTrafficPieceUrl(name,cat,p_x,p_y) {
        return '/data/tp?cat=' + cat + "&px=" + p_x + "&py=" + p_y + "&name=" + name;
    }

    function getTrafficWholeUrl(name) {
        return '/data/tpwhole?name=' + name;
    }

    function getHeatmap(name){
        return base + "data/heatmap" + "?name=" + name;
    }

    function getMessagePiece(name,cat,px,py){
        return base + "data/msg" + "?name=" + name + "&px=" + px + "&py=" + py + "&cat=" + cat;
    }

    function getLocationInfo(lng, lat) {
        return "https://api.mapbox.com/v4/geocode/mapbox.places/"+ lng +"," + lat + ".json?access_token=pk.eyJ1IjoibmVveWVvd3lhbmciLCJhIjoiY2luMTYxNjR0MGF3c3V3bTRxaXl4Nmo2eCJ9.ruf9gRvPvou5bsi6LaD_Ww"
    }

    function getRoadSegInfo(lng, lat, cats,traffic_name) {
        return '/data/roadseg?cats=' + cats + "&lng=" + lng + "&lat=" + lat + "&name=" + traffic_name;
    }

    function getCheckMessageName(name) {
        return "/data/msg_chkname?name=" + name;
    }

    function getCheckHeatmapName(name) {
        return "/data/heatmap_chkname?name=" + name;
    }
});

/**
 * Utility service for computing required traffic slices, used in TrafficService.updateTraffic
 */
app.factory('SlicingService', function () {

    var service = {
        getRequiredSlices:getRequiredSlices
    };

    var defaultConfigs = {
        mapBound:{
            "e":104.026112,
            "w":103.614324,
            "n":1.469661,
            "s":1.23057
        },

        xSeg: 4,
        ySeg: 4,
        slices: {} // to be computed by computeSlices
    };
    _computeSlices(defaultConfigs);

    return service;

    ////////////////////////////////////////////
    /// public functions declarations
    /**
     * @param bounds: {n:..,s:..,e:..,w:..}
     * @param specific_config: config object, optional
     * @returns {Array}
     */
    function getRequiredSlices(bounds,specific_config) {
        config = defaultConfigs;
        if (specific_config){
            config = specific_config;
        }
        // return the slices that overlap with the current map bound
        slices = config.slices;
        requiredSlices = [];
        for (var key in slices) {
            if (slices.hasOwnProperty(key)) {
                sliceBound = slices[key];
                if (isBoundsOverlap(sliceBound,bounds)){
                    requiredSlices.push(key);
                }
            }
        }
        return requiredSlices;
    }


    ///////////////////////////////////////////
    // inner function declarations
    function isBoundsOverlap(bound, otherBound) {
        return isXOverlap(bound,otherBound) && isYOverlap(bound,otherBound);
    }

    function isXOverlap(r1,r2){
        return (r2["w"] <= r1["w"] && r1["w"] < r2["e"])
        || ( r1["w"] <= r2["w"] && r2["w"] < r1["e"]);
    }

    function isYOverlap(r1,r2){
        return (r2["s"] < r1["n"] && r1["n"] <= r2["n"]) ||
        (r1["s"] < r2["n"] && r2["n"] <= r1["n"]);
    }

    function _computeSlices(configs){
        mapBound = configs.mapBound;
        for (x = 0; x < configs.xSeg; x++) {
            for (y = 0; y < configs.ySeg; y++) {
                configs["slices"][[x,y]] = {
                    "w": mapBound["w"] + x * (mapBound["e"] - mapBound["w"]) / configs.xSeg,
                    "e": mapBound["w"] + (x+1) * (mapBound["e"] - mapBound["w"]) / configs.xSeg,
                    "s": mapBound["s"] + y * (mapBound["n"] - mapBound["s"]) / configs.ySeg,
                    "n": mapBound["s"] + (y+1) * (mapBound["n"] - mapBound["s"]) / configs.ySeg
                };
            }
        }
    }

});
/**
 * Created by zhangjie on 12/6/2016.
 */

app.constant('trafficServiceConfig', {
    // this determines when to display what categories of roads
    categoryConfig:{
        LevelToCats : {
            11: ["A","B","C","D"],
            12: ["A","B","C","D","E"],
            13: ["A","B","C","D","E","S","N"]
        },
        defaultCat: ["A","B","C"],
        minZoom: 11,
        maxZoom: 13
    },
    // speed labels for traffic
    speeds:[0,1,2],
    speedToColor:{
            0:"#f44242",
            1:"#ffd60a",
            2:"#1aff0a"
        },
    // config for marker line when user clicks on map
    markerPaint:{
        "color": "#f442b3",
        "width": 6
    },
    // config for normal traffic lines
    trafficLinePaint:{
        "width": 2,
        "opacity":0.7
    }
});


app.constant('messageServiceConfig', {
    // defines how messages of each category are displayed
    categoryConfig:{
        LevelToCats : {
            12: ["A"], 13: ["B"],
            14: ["B"], 15: ["C"],
            16: ["C"]
        },
        radiusConfig:{
            "A": 6,
            "B": 4,
            "C": 3
        },
        defaultCat: ["A"],
        minZoom:12,
        maxZoom: 16
    },
    // config for message circles
    messageCirclePaint:{
        opacity: 0.8
    }

});

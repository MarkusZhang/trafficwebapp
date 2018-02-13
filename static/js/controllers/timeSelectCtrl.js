// controller for selecting traffic time (typical or history)

app.controller("timeSelectCtrl",function ($rootScope,UrlService,$http,CtrlMsgService,$scope) {
    var tsCtrl = this;
    tsCtrl.select_mode = "typical"; // either 'typical' or 'history'
    // below is used when mode = history
    tsCtrl.history_selected_traffic = {
        "name": null, // identifier
        "year": null,
        "month": null,
        "day": null,
        "time": null
    };
    tsCtrl.history_traffic_time = {
        years: null, // years in select box
        months: null, // months in select box
        days: null,  // days in select box
        times: null,  // time slots in bar
        selected_time:null,
        selected_day: null,
        selected_month: null,
        selected_year: null
    };
    tsCtrl.trafficYearChanged = historyTrafficYearChanged;
    tsCtrl.trafficMonthChanged = historyTrafficMonthChanged;
    tsCtrl.trafficDayChanged = historyTrafficDayChanged;
    tsCtrl.selectHistoryTraffic = selectNewHistoryTraffic;
    // below is used when mode = typical
    tsCtrl.typical_selected_traffic = {
        "name": "sunday 00:00", // identifier
        "day": "sunday", // e.g. "sunday"
        "time_index": 0 // 0-95
    };
    tsCtrl.typicalDayChanged = typicalDayChanged;
    tsCtrl.switchMode = switchMode;
    tsCtrl.init = init;

    // run init only when included content is loaded
    $scope.$on('$includeContentLoaded', function(event) {
        init();
    });

    function init() {
        $(document).ready(
            function () {
                // init typical traffic slider
                labels = [];
                for (var i = 0; i < 96; i++) {
                    if (i % 8 ==0 && i!=0){
                        labels.push(i/4 + ":00");
                    }
                    else{
                        labels.push("");
                    }
                }
                angular.element("#slider").slider({
                  change: function( event, ui ) {
                      _typicalTimeChanged(ui.value);
                      $("#timeindex").text(tsCtrl.typical_selected_traffic.name);
                  },
                  max: 95
                }).slider("pips",{
                    labels:labels,
                    rest:"label"
                });

                // style radio boxes
                angular.element( ".controlgroup" ).controlgroup();
            }
        );

        // init history traffic time
        $("#timeindex").text(tsCtrl.typical_selected_traffic.name);
    }


    function switchMode(mode) {
        if (mode == "history"){
            tsCtrl.select_mode = "history";
            if (tsCtrl.history_traffic_time.years == null){
                // init traffic time
                CtrlMsgService.broadcastMsg("loading available history","loading");
                load_history_traffic_time();

            }
        }
        else if (mode == "typical") tsCtrl.select_mode = "typical";
    }

    //////////////////////////////////////////////////////////
    // functions for history traffic selection
    function load_history_traffic_time() {
    $http
        .get(UrlService.getTrafficAvailableTime, {})
        .success(function (data) {
            tsCtrl.history_traffic_time.source = data;
            tsCtrl.history_traffic_time.years = _getKeys(data);
            first_year = tsCtrl.history_traffic_time.years[0];
            tsCtrl.history_traffic_time.months = _getKeys(data[first_year]);
            first_month = tsCtrl.history_traffic_time.months[0];
            tsCtrl.history_traffic_time.days = _getKeys(data[first_year][first_month]);
            first_day = tsCtrl.history_traffic_time.days[0];
            tsCtrl.history_traffic_time.times = data[first_year][first_month][first_day];
            CtrlMsgService.broadcastMsg("","endloading");
        })
        .error(function (data) {
            alert("failed to load history traffic time");
        });
    }

    function historyTrafficYearChanged() {
        // reset month and day select box
        selected_year = $('#traffic_year').val();
        source_months = tsCtrl.history_traffic_time.source[selected_year];
        months = _getKeys(source_months);
        // reset month
        tsCtrl.history_traffic_time.months = months;
        // reset day
        tsCtrl.history_traffic_time.days = _getKeys(source_months[months[0]]);
        tsCtrl.history_traffic_time.selected_time = null;
        tsCtrl.history_traffic_time.selected_day = null;
        tsCtrl.history_traffic_time.selected_month = null;
        tsCtrl.history_traffic_time.selected_time = null;
        updateHistoryTrafficTimeBar();
    }

    function historyTrafficMonthChanged() {
        // reset day select box
        selected_month = $('#traffic_month').val();
        selected_year = $('#traffic_year').val();
        source_months = tsCtrl.history_traffic_time.source[selected_year][selected_month];
        days = _getKeys(tsCtrl.history_traffic_time.source[selected_year][selected_month]);
        tsCtrl.history_traffic_time.days = days;
        tsCtrl.history_traffic_time.selected_time = null;
        updateHistoryTrafficTimeBar();
    }

    function historyTrafficDayChanged() {
        tsCtrl.history_traffic_time.selected_time = null;
        updateHistoryTrafficTimeBar();
    }

    function updateHistoryTrafficTimeBar() {
        selected_month = $('#traffic_month').val();
        selected_year = $('#traffic_year').val();
        selected_day = $('#traffic_day').val();
        tsCtrl.history_traffic_time.times = tsCtrl.history_traffic_time.source[selected_year][selected_month][selected_day];
    }

    // handle events when user selects a new time
    function selectNewHistoryTraffic(time) {
        tsCtrl.history_traffic_time.selected_time = time;
        // set cur traffic name
        selected_month = $('#traffic_month').val();
        selected_year = $('#traffic_year').val();
        selected_day = $('#traffic_day').val();
        traffic_name = selected_year + "-" + selected_month + "-" + selected_day + "T" + time;
        // update the map controller
        _broadcastHistoryTrafficName(traffic_name);
    }

    //////////////////////////////////////////////////
    // functions for typical traffic
    function typicalDayChanged() {
        var days = ["sunday","monday","tuesday","wednesday","thursday","friday","saturday"];
        var selected_day = "";
        for (var i = 0; i < days.length; i++) {
            if ($("#" + days[i]).prop("checked")){
                selected_day = days[i];
                break;
            }
        }
        tsCtrl.typical_selected_traffic["day"] = selected_day;
        tsCtrl.typical_selected_traffic.name = _formatTypicalTime(tsCtrl.typical_selected_traffic.day,tsCtrl.typical_selected_traffic.time_index);
        $("#timeindex").text(tsCtrl.typical_selected_traffic.name);
        _broadcastTypicalTrafficName(tsCtrl.typical_selected_traffic["day"],tsCtrl.typical_selected_traffic["time_index"]);
    }

    function _typicalTimeChanged(value) {
        tsCtrl.typical_selected_traffic.time_index = value;
        tsCtrl.typical_selected_traffic.name = _formatTypicalTime(tsCtrl.typical_selected_traffic.day,tsCtrl.typical_selected_traffic.time_index);
        //console.log("slide value: " + value);
        _broadcastTypicalTrafficName(tsCtrl.typical_selected_traffic["day"],tsCtrl.typical_selected_traffic["time_index"]);
    }

    // get keys of a key-value object
    function _getKeys(obj) {
        keys = [];
        for (var k in obj){
            keys.push(k);
        }
        return keys
    }

    function _broadcastHistoryTrafficName(name) {
        CtrlMsgService.broadcastMsg({
            type:"history",
            name: name
        },"trafficSelected");
    }

    function _broadcastTypicalTrafficName(day,timeIndex) {
        CtrlMsgService.broadcastMsg({
            type:"typical",
            name: day + "T" + timeIndex
        },"trafficSelected");
    }

    function _formatTypicalTime(day,timeIndex) {
        hour = Math.round(Number(timeIndex) / 4);
        minutes = Number(timeIndex) % 4 * 15;
        return day + " " + _padZero(hour) + ":" + _padZero(minutes);
    }

    function _padZero(num) {
        if (Number(num)<10)
            return "0" + num;
        else
            return "" + num;
    }
});
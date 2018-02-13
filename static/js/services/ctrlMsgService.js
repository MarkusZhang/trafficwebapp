// service for inter-controller communication

app.factory('CtrlMsgService', function ($rootScope) {
    var service = {
        broadcastMsg:broadcastMsg,
        getMsg: getMsg
    };

    var message = ""; // stored var

    return service;

    function broadcastMsg(msg, eventName) {
        message = msg;
        $rootScope.$broadcast(eventName);
    }

    function getMsg() {
        toReturn = message;
        message = "";
        return toReturn;
    }
}
);
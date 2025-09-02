function toLog() {
    if( typeof window.console != 'undefined' && typeof window.console.log != 'undefined') {
        var debug_mode = eval("window.debug_mode");
        if(true == debug_mode) {
            return true;
        }
    }
    return false;
}

jQuery.console = {
    log : function(message) {
        if(toLog()) {
            console.log(message);
        }
    },
    error : function(message) {
        if(toLog()) {
            console.error(message);
        }
    },
    info : function(message) {
        if(toLog()) {
            console.info(message);
        }
    },
    warn : function(message) {
        if(toLog()) {
            console.warn(message);
        }
    },
    debug : function(message) {
        if(toLog()) {
            console.debug(message);
        }
    }
}
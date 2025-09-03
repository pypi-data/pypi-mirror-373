
function getOneMonthAgo(){
    var today = new Date();
    var year = today.getUTCFullYear();
    var month = today.getUTCMonth() - 1;
    var day = today.getUTCDate();
    return new Date(year, month, day);
}

function parseDate(isoDate){
    /*
     * Returns a js Date object from an iso formatted string
     */
    var splitted = isoDate.split('-');
    var year = parseInt(splitted[0], 10);
    var month = parseInt(splitted[1], 10) - 1;
    var day = parseInt(splitted[2], 10);
    return new Date(year, month, day);
}
var getDateFromIso = parseDate;
function formatPaymentDate(isoDate){
    /*
     *  format a date from iso to display format
     */
    if ((isoDate !== '') && (isoDate !== null) && (!_.isUndefined(isoDate))){
        var dateObject = parseDate(isoDate);
        return dateToLocaleFormat(dateObject);
    }else{
        return "";
    }
}
var formatDate = formatPaymentDate;

function dateToIso(dateObject){
    var year = dateObject.getFullYear();
    var month = dateObject.getMonth()+1;
    var dt = dateObject.getDate();

    if (dt < 10) {
        dt = '0' + dt;
    }
    if (month < 10) {
        month = '0' + month;
    }
    return year + "-" + month + "-" + dt;
}
function dateToLocaleFormat(dateObject){
    var year = dateObject.getFullYear();
    var month = dateObject.getMonth()+1;
    var dt = dateObject.getDate();

    if (dt < 10) {
        dt = '0' + dt;
    }
    if (month < 10) {
        month = '0' + month;
    }
    return dt + '/' + month + '/' + year;
}

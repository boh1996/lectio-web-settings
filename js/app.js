api_url = "https://illution.dk/lectio/web/api/";
base_url = "http://127.0.0.1/lectio-web/";

/**
 * This function returns the current "page",
 * ready to use with the URL Routing system
 * @return {string}
 */
function getPage () {
	return History.getState().url.replace(base_url,"").replace(/\?.*/g,"");
}

/**
 * Retrieves the selected URL parameter
 * @param  {string} name Parameter name
 * @return {string}      Parameter value
 */
function getURLParameter( name ) {
    return decodeURI(
        (RegExp(name + '=' + '(.+?)(&|$)').exec(location.search)||[,null])[1]
    );
}

var History = window.History;

$(window).ready(function () {
	crossroads.parse(getPage());
	crossroads.resetState();

	History.Adapter.bind(window,'statechange',function(){
		crossroads.parse(getPage());
		crossroads.resetState();
    });
});

crossroads.bypassed.add(function () {
    $("#home").addClass("active-page").removeClass("disabled-page");
});

crossroads.addRoute("callback", function () {
	if ( getURLParameter("code") !== null ) {
		$.get(api_url + "callback?state=" + getURLParameter("state") +"&code=" + getURLParameter("code")).success( function (data) {
			data = $.parseJSON(data);
			window.user = data;
		});
	}
});

// When the sign in button is clicked, request the Authentication URL and Redirect
$(document).on("click", "#signin", function () {
	$.ajax(api_url + "auth").success(function (data) {
		data = $.parseJSON(data);
		console.log(data);
		if ( data.status == "ok" ) {
			console.log(data.url);
			window.location = data.url;
		} else {
			// Show Error
		}
	});
});
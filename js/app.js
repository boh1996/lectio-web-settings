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

	History.Adapter.bind(window,'statechange',function () {
		$(".active-page").addClass("disabled-page").removeClass("active-page");
		crossroads.parse(getPage());
		crossroads.resetState();
    });
});

$(document).on("click", "#signup_create_calendar", function () {
	$("#signup_create_calendar_group").toggleClass("disabled");
	if ( ! $("#signup_calendars_group").hasClass("disabled") ) {
		$("#signup_calendars_group").addClass("disabled");
	}
});

function getById ( list, id) {
	for( var key in list ) {

        if( key === id ){
            return list[key];
        }
	}

	return false;
}

$(document).on("click", "#skip-timetable", function () {
	History.pushState(null,null, base_url+"signup-asssignments");
});

$(document).on("click","#signup_calendars_table a", function () {
	$("#signup_calendars_table a.active").removeClass("active");
	$(this).addClass("active");
});

$(document).on("click", "#save-timetable", function () {
	if ( ( $("#signup_calendars_table a.active").length > 0 && ! $("#signup_calendars_group").hasClass("disabled") )  || $("#signup_create_calendar_name").val().length > 0 ) {
		var change = {
			"simplify" : $("#signup_simplify").attr("data-checked"),
			"notifications" : $("#signup_notifications").attr("data-checked"),
		};

		var save = false;

		if ( ! $("#signup_create_calendar_group").hasClass("disabled") && $("#signup_create_calendar_name").val().length > 0) {
			change.calendar = {
				"type" : "create",
				"name" : $("#signup_create_calendar_name").val(),
			};
			save = true;
		} else if ( ( $("#signup_calendars_table a.active").length > 0 && ! $("#signup_calendars_group").hasClass("disabled") ) ) {
			change.calendar = {
				"type" : "existing",
				"id" : $("#signup_calendars_table a.active").attr("data-calendar-id"),
			};
			save = true;
		}

		if ( save ) {
			session = $.parseJSON(localStorage.getItem("session"));
			$.ajax({
				type : "post",
				url : api_url + "save/calendar?token=" + session.token,
				data : JSON.stringify(change)
			}).success(function () {
				//History.pushState(null,null, base_url+"signup-asssignments");
			}).fail(function () {
				// Error
			});
		} else {
			// Error
		}
	}
});

$(document).on("click", "#signup_calendars", function () {
	if ( $("#signup_calendars_group").hasClass("disabled") ) {
		session = $.parseJSON(localStorage.getItem("session"));

		$.get(api_url + "fetch/calendars?token=" + session.token).success(function (json) {
			data = $.parseJSON(json);
			$("#signup_calendars_table").html("");
			for ( var key in data.calendars.items ) {
				var calendar = data.calendars.items[key];
				var color = getById(data.colors.calendar, calendar.colorId);
				calendar.colors = {"foreground" : color.foreground};
				calendar.colors = {"background" : color.background};
				if ( calendar.accessRole == "owner" ) {
					$("#signup_calendars_table").append('<a class="btn btn-default" data-calendar-id="'+calendar.id+'" style="background-color:'+color.background+'; color:'+color.foreground+';"><td>'+calendar.summary+'</a>');
				}
			}
		});
	}

	$("#signup_calendars_group").toggleClass("disabled");
	if ( ! $("#signup_create_calendar_group").hasClass("disabled") ) {
		$("#signup_create_calendar_group").addClass("disabled");
	}
});

$(document).on("click", "#save-school", function () {
	if ( typeof $("#school").attr("data-school") == "undefined" ) return;
	changes = {
		school_id : $("#school").attr("data-school"),
		branch_id : $("#school").attr("data-branch")
	};

	session = $.parseJSON(localStorage.getItem("session"));

	$.post(api_url + "save/school?token=" + session.token, changes).success(function (json) {
		History.pushState(null,null, base_url+"signup-timetable");
	}).fail(function () {
		// Error
	});
});

crossroads.addRoute("signup-asssignments", function () {
	$("#signup_assignments").addClass("active-page").removeClass("disabled-page");
});

crossroads.addRoute("signup-timetable", function () {
	$("#signup_timetable").addClass("active-page").removeClass("disabled-page");
	$('input[type="checkbox"]').checkbox();
});

crossroads.bypassed.add(function () {
    $("#home").addClass("active-page").removeClass("disabled-page");
});

crossroads.addRoute("signup-school", function () {
	$("#signup_school").addClass("active-page").removeClass("disabled-page");
	$("input.schools").typeahead({
		name : "schools",
		engine : Hogan,
		valueKey : "name",
		prefetch : api_url + "schools",
		remote : api_url + "schools?suggest=%QUERY",
		limit : 5,
		ttl: 0,
		template : '<p data-branch="{{branch_id}}" data-school="{{school_id}}" data-id="{{id}}">{{name}}</p>',
	});
	$("input.schools").on("typeahead:selected typeahead:autocompleted", function(e,datum) {
		$("#school").attr("data-branch", datum.branch_id).attr("data-school", datum.school_id);
	});
});

crossroads.addRoute("update", function () {
	$("#update_front").addClass("active-page").removeClass("disabled-page");
});

crossroads.addRoute("callback", function () {
	if ( getURLParameter("code") !== null ) {
		$.get(api_url + "callback?state=" + getURLParameter("state") +"&code=" + getURLParameter("code")).success( function (json) {
			data = $.parseJSON(json);
			if ( data.status == "ok" ) {
				window.session = data;
				localStorage.setItem("session", json);
				if ( data.created == false ) {
					History.pushState(null,null, base_url+"update");
				} else {
					History.pushState(null,null, base_url+"signup-school");
				}
			} else {
				// Error
			}
		}).fail( function () {
			// Error
		});
	} else {
		// Error
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
	}).fail( function () {
		// Error
	});
});
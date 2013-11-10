import urls
import urllib
import variables
import json
import urllib2
import requests
import urlbuilder

class GoogleCalendar:
    access_token = ""

    def __init__(self):
        pass

    # Fetches the events from the selected calendar
    # @param calendar_id The ID of the Google Calendar to fetch events from
    def events (self, calendar_id, params = "NULL"):
        url = "%scalendars/%s/events?%s=%s" % (urls.google_api_base_url, calendar_id ,variables.access_token_parameter, self.access_token)

        if params != "NULL":
            url = url + urlbuilder.get(params)

        f = urllib.urlopen(url)
        response = f.read()

        return json.loads(response)

    # Fetches the users color settings for the calendars
    def colors (self):
        url = "%scolors?%s=%s" % (urls.google_api_base_url, variables.access_token_parameter, self.access_token)
        f = urllib.urlopen(url)

        response = f.read()

        return json.loads(response)

    # Insert an event to the selected calendar
    def insertEvent (self, calendar_id, params):
        url = "%scalendars/%s/events?%s=%s" % (urls.google_api_base_url, calendar_id, variables.access_token_parameter, self.access_token)

        f = requests.post(url, data=json.dumps(params), headers={'content-type': 'application/json'})
        response = f.json()

        return response

    # Deletes an event from the selected calendar
    def deleteEvent (self, calendar_id, event_id):
        url = "%scalendars/%s/events/%s?%s=%s" % (urls.google_api_base_url, calendar_id , event_id,variables.access_token_parameter, self.access_token)

        response = requests.delete(url)

    # Creates a new Calendar
    def createCalendar (self, name, timeZone = "Europe/Copenhagen"):
        url = "%susers/me/calendarList?%s=%s" % (urls.google_api_base_url, variables.access_token_parameter, self.access_token)

        f = requests.post(url, data=json.dumps({"summary" : name, "timeZone" : timeZone}), headers={'content-type': 'application/json'})
        response = f.json()

        return response

    # Retrieve the list of Google calendars for a user
    def calendars (self):
        url = "%susers/me/calendarList?%s=%s" % (urls.google_api_base_url, variables.access_token_parameter, self.access_token)

        f = urllib.urlopen(url)
        response = f.read()

        return json.loads(response)

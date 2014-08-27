import creator
import database_api
from twilio.rest import TwilioRestClient

account_sid = ""
auth_token = ""
from_number = "+16265138988"

class WebApi:

    def __init__(self, db_name):
        self.api = database_api.DatabaseApi(db_name)
        self.create = creator.ObjectCreator()
        self.client = TwilioRestClient(account_sid, auth_token)

    def change_event_status(self, event_title):
        event = self.api.get_event(event_title)
        limit = int(event['limit'])
        going = int(event['going'])
        not_going = int(event['not_going'])
        total = event['total']
        if limit <= going:
            self.event_on(event_title)
        elif total - limit < not_going:
            self.event_off(event_title)

    def check_event_status(self, event_title):
        return self.api.get_event_status(event_title)

    def get_event_by_code(self, event_code):
        return self.api.get_event_by_code(event_code)

    def get_event_by_name(self, event_title):
        return self.api.get_event(event_title)

    def inc_count(self, event_title, count_name):
        count = self.api.get_count(event_title, count_name)
        self.api.update_count(event_title, count_name, count + 1)

    def dec_count(self, event_title, count_name):
        count = self.api.get_count(event_title, count_name)
        self.api.update_count(event_title, count_name, count - 1)

    def create_event(self, host_name = '', host_number = '', title = '', time = '', location = '', details = '', limit = 0, guests = {}):
        event = self.create.create_event(host_name, host_number, title, time, location, details, limit, guests)
        self.api.add_event(event)
        self.change_event_status(title)

    def event_on(self, event_title):
        self.api.update_event_status(event_title, 1)

    def event_off(self, event_title):
        self.api.update_event_status(event_title, -1)

    def guest_on(self, event_title, guest_number):
        current_status = self.api.get_guest_status(event_title, guest_number)
        if current_status is -1:
            self.dec_count(event_title, 'not_going')
        self.api.update_guest_status(event_title, guest_number, 1)
        self.inc_count(event_title, 'going')
        self.change_event_status(event_title)

    def guest_off(self, event_title, guest_number):
        current_status = self.api.get_guest_status(event_title, guest_number)
        if current_status is 1:
            self.dec_count(event_title, 'going')
        self.api.update_guest_status(event_title, guest_number, -1)
        self.inc_count(event_title, 'not_going')
        self.change_event_status(event_title)

    def text_host_init_event(self, event):

        host_name = event['host_name']
        title = event['title']
        time = event['time']
        host_number = event['host_number']

        event_host_message = 'Hey {}! You\'ve created the event "{}" at {}.  You\'ll get a text if the event is ON (or OFF)!'.format(host_name, title, time)
        message = self.client.sms.messages.create(to=host_number, from_= from_number, body=event_host_message)
        print "texted host"

    def text_guests_init_event(self, event, responses):

        host_name = event['host_name']
        title = event['title']
        time = event['time']
        code = event['code']

        for guest in responses.keys():
            event_guest_message = 'Hey you! {} has invited you to "{}" at {}. Reply "{} YES" if you are going, or "{} NO" if you can\'t make it.'.format(host_name, title, time, code, code)
            message = self.client.sms.messages.create(to=guest, from_= from_number, body=event_guest_message)
        print "texted guests"

    def text_response_guest(self, event, guest_number, response):

        event_title = event['title']
        event_time = event['time']

        acknowledge = ""

        if response == 1:
            acknowledge = "Thanks for your response! If enough people accept their invitations, you are going to " + event_title + " at " + event_time + "."
        else:
            resp.sms("Thanks for your response! You declined the invite to " + event_title + ".")
        message = self.client.sms.messages.create(to=guest_number, from_= from_number, body=acknowledge)


    def text_host_event_on(self, event):

        responses = event['responses']
        host_number = event['host_number']
        host_name = event['host_name']
        title = event['title']
        time = event['time']
        location = event['location']

        if responses[host_number] == 1:
            event_on_host_message = 'Hey {}! Your event : "{}" at {} is ON! Location : {}'.format(host_name, title, time, location)
            message = self.client.sms.messages.create(to=host_number, from_= from_number, body=event_on_host_message)
            self.api.update_guest_status(title, host_number, 2)
            print "texted host event ON"

    def text_guests_event_on(self, event):

        responses = event['responses']
        host_name = event['host_name']
        host_number = event['host_number']
        title = event['title']
        time = event['time']
        location = event['location']

        for guest in responses.keys():
            if responses[guest] == 1 and guest != host_number:
                event_on_guest_message = 'Hey you! {}\'s event : "{}" at {} is ON! Location : {}'.format(host_name, title, time, location)
                message = self.client.sms.messages.create(to=guest, from_ = from_number, body=event_on_guest_message)
                self.api.update_guest_status(title, guest, 2)
                print "texting guest : " + guest
        print "texted guests event ON"

    def text_host_event_off(self, event):

        responses = event['responses']
        host_number = event['host_number']
        host_name = event['host_name']
        title = event['title']

        if responses[host_number] == 1:
            event_off_host_message = 'Aw shucks, {}! Your event : "{}" is OFF :('.format(host_name, title)
            message = self.client.sms.messages.create(to=host_number, from_= from_number, body=event_off_host_message)
            self.api.update_guest_status(title, guest, -2)
            print "texted host event OFF"

    def text_guests_event_off(self, event):
        responses = event['responses']
        host_name = event['host_name']
        host_number = event['host_number']
        title = event['title']
        time = event['time']

        for guest in responses.keys():
            print "CHECKING : " + guest + ", " + str(responses[guest])
            if responses[guest] >= 0 and guest != host_number:
                event_off_guest_message = 'Aw shucks! {}\'s event : "{}" is OFF :('.format(host_name, title)
                message = self.client.sms.messages.create(to=guest, from_ = from_number, body=event_off_guest_message)
                self.api.update_guest_status(title, guest, -2)
                print "texting guest : " + guest
        print "texted guests event ON"

    def clear_db(self):
        self.api.clear_db()  

    def get_all_events(self):
        return self.api.get_all_events()

    def get_event(self, event_title):
        return self.api.get_event(event_title)

from flask import render_template, flash, redirect, request
from app import app
from sets import Set
import api.web_api
import api.db_test
import twilio.twiml
from twilio.rest import TwilioRestClient

# change to actual db
web_api = api.web_api.WebApi('heroku_app15987323')
account_sid = ""
auth_token = ""
#web_api = api.web_api.WebApi('test')

def demo_names():
    names = {}
    return names

@app.route('/')
@app.route('/index')
def index():
    return redirect('/init')

@app.route('/init', methods = ['GET', 'POST'])
def init_event():
    return render_template('init_event.html',
        title = 'Create an Event')

@app.route('/create', methods=['POST'])
def create():
    names = demo_names()

    # get fields
    host_name = request.form['host_name']
    host_number = request.form['host_number']
    title = request.form['title']
    time = request.form['time']
    location = request.form['location']
    details = request.form['details']
    limit = int(request.form['limit'])

    host_number = filter(lambda x: x not in '()- ', host_number)
    if "+1" not in host_number:
        host_number = "+1" + host_number

    guests = {}

    for key in request.form.keys():
        value = request.form[key]
        if "guest" in key and value:

            # check if name or number
            if value.lower() in names:
                guests[names[value.lower()]] = 0

            # filter out characters
            else:
                value = filter(lambda x: x not in '()- ', value)
                if "+1" not in value:
                    value = "+1" + value
                guests[value] = 0

    print guests

    if limit > len(guests) + 1:
        limit = len(guests) + 1


    # create event
    web_api.create_event(host_name, host_number, title, time, location, details, limit, guests)

    all_events = web_api.get_all_events()

    for event in all_events:
        api.db_test.print_event(event)

    event = web_api.get_event_by_name(title)

    web_api.text_host_init_event(event)
    web_api.text_guests_init_event(event, guests)

    event_status = web_api.check_event_status(title)

    if event_status == 1:
        web_api.text_host_event_on(event)
        web_api.text_guests_event_on(event)

    return render_template('created_event.html', title='Create an Event')

@app.route('/cleardb')
def clear_db():

    web_api.clear_db()

    all_events = web_api.get_all_events()

    if not all_events:
        print "DATABASE CLEARED!"

    for event in all_events:
        api.db_test.print_event(event)

    return render_template('clear_db.html',
        title = 'Database Cleared')

@app.route('/sms', methods=['GET', 'POST'])
def sms():
    guest_number = request.values.get('From', None)
    to_number = request.values.get('To', None)
    body = request.values.get('Body', None).encode('ascii', 'ignore')

    body = str.strip(body)
    contents = body.split(" ")
    code = int(contents[0])
    response = contents[1]

    resp = twilio.twiml.Response()

    event = web_api.get_event_by_code(code)
    if not event:
        resp.sms("I'm sorry, that code is incorrect.  Please try again.")
        return str(resp)

    event_title = event['title']
    event_time = event['time']
    responses = event['responses']
    host_name = event['host_name']
    host_number = event['host_number']


    if response and response.lower() == "yes":
        web_api.guest_on(event_title, guest_number)
        web_api.text_response_guest(event, guest_number, 1)
        # resp.sms("Thanks for your response! If enough people accept their invitations, you are going to " + event_title + " at " + event_time + ".")
    else:
        web_api.guest_off(event_title, guest_number)
        web_api.text_response_guest(event, guest_number, -1)
        # resp.sms("Thanks for your response! You declined the invite to " + event_title + ".")

    event_status = web_api.check_event_status(event_title)

    # refresh event
    event = web_api.get_event_by_code(code)

    if event_status == 1:
        web_api.text_host_event_on(event)
        web_api.text_guests_event_on(event)

    elif event_status == -1:
        web_api.text_host_event_off(event)
        web_api.text_guests_event_off(event)

    all_events = web_api.get_all_events()

    for event in all_events:
        api.db_test.print_event(event)

    flash ('Sent something')
    return redirect('\init')






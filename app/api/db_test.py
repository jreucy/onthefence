### Various Tests ###

import database_api
import web_api
import creator



def print_event(event):
    status = event['status']
    host_name = event['host_name']
    host_number = event['host_number']
    title = event['title']
    time = event['time']
    location = event['location']
    details = event['details']
    limit = event['limit']
    going = event['going']
    not_going = event['not_going']
    total = event['total']
    responses = event['responses']
    code = event['code']

    print 'status: ' + str(status)
    print 'host name : ' + host_name
    print 'host_number : ' + host_number
    print 'title : ' + title
    print 'time : ' + time
    print 'location : ' + location
    print 'details : ' + details
    print 'limit : ' + str(limit)
    print 'going : ' + str(going)
    print 'not going : ' + str(not_going)
    print 'total : ' + str(total)
    print 'code : ' + str(code)

    numbers = ''
    for number in responses:
        numbers = numbers + '[' + number + ' : ' + str(responses[number]) + ']' + ', '
    print 'guest numbers: ' + numbers


## Fake Data ##

def insert_some_events(wapi, c):
    guests = {}
    guests['+16262241193'] = 'Jon'
    guests['+12345678910'] = 'Smith'
    wapi.create_event(host_name="Jonathan Hsu", host_number='+12223334444', title="Dinner", time="7:00pm", location = "Super Duper Burger", limit = 2, guests = guests)

def reset_db(webApi):
    c = creator.ObjectCreator()
    # Clear previous test data
    webApi.clear_db()
    insert_some_events(webApi, c)

def test():
    # Create fake testing db
    w = web_api.WebApi('test')

    reset_db(w)

    all_events = w.get_all_events()

    print_event(w.get_event("Dinner"))

    print "\n"

    print w.get_event_by_code(1)

    print "\n"

    w.guest_on("Dinner","+16262241193")
    w.guest_off("Dinner","+12345678910")

    all_events = w.get_all_events()

    for event in all_events:
        print_event(event)


if __name__ == "__main__":
    print test()






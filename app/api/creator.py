import random

## Class for creating JSON objects (dictionaries) to place in data table ##
class ObjectCreator:

    def random_code(self, title):
        random.seed(title)
        random_number = random.randint(1000, 9999)

        return random_number

    def create_event(self, 
        host_name = '',
        host_number = '',
        title = '',
        time = '',
        location = '',
        details = '',
        limit = 1,
        guests = {}):

        event = {}
        event['status'] = 0
        event['host_name'] = host_name
        event['host_number'] = host_number
        event['title'] = title
        event['time'] = time
        event['location'] = location
        event['details'] = details
        event['limit'] = limit
        event['going'] = 1
        event['not_going'] = 0
        event['total'] = len(guests) + 1

        responses = {}
        for number in guests:
            responses[number] = 0
        responses[host_number] = 1

        event['responses'] = responses

        event['code'] = self.random_code(title)
        return event

## Directly accesses and performs operations on the MongoDB database ##

import pymongo
import creator
# import time
import os

class DatabaseApi:

    # Administrative Database Functions

    # def __init__(self, db = ''):
    #     self.creator = creator.ObjectCreator()
    #     self.connection = pymongo.Connection('localhost', 27017)
    #     self.db = self.connection[db]

    def __init__(self, db = 'heroku_app15987323'):
        self.creator = creator.ObjectCreator()
        if db == 'test':
            self.connection = pymongo.Connection('localhost', 27017)
        else:
            self.connection = pymongo.Connection(os.environ.get('MONGOLAB_URI', None))

        self.db = self.connection[db]

    def add_event(self, event):
        events = self.db.events
        events.insert(event)

    def get_all_events(self):
        events = self.db.events
        return list(events.find())

    def get_event(self, event_title):
        events = self.db.events
        event = events.find_one({'title' : event_title})
        return event

    def get_event_by_code(self, event_code):
        events = self.db.events
        event = events.find_one({'code' : event_code})
        return event

    def update_event_status(self, event_title, new_status):
        events = self.db.events
        events.update({'title' : event_title}, {'$set' : {'status' : new_status}})

    def get_event_status(self, event_title):
        event = self.get_event(event_title)
        return event['status']

    def get_guest_status(self, event_title, guest_number):
        events = self.db.events
        event = self.get_event(event_title)
        responses = event['responses']
        return responses[guest_number]

    def update_guest_status(self, event_title, guest_number, new_status):
        events = self.db.events
        event = self.get_event(event_title)
        responses = event['responses']
        responses[guest_number] = new_status
        events.update({'title' : event_title}, {'$set' : {'responses' : responses}})

    def get_count(self, event_title, count_name):
        event = self.get_event(event_title)
        return event[count_name]

    def update_count(self, event_title, count_name, new_count):
        events = self.db.events
        events.update({'title' : event_title}, {'$set' : {count_name : new_count}})

    # Functions used for Testing

    def clear_db(self):
        """ Deletes all data in the database"""
        for col in self.db.collection_names():
            try:
                self.db.drop_collection(col)
            except Exception:
                pass
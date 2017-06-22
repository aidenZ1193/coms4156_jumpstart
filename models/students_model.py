from model import Model
from datetime import datetime, date
from google.cloud import datastore

import json                     # for getting coordinates
from urllib2 import urlopen     # for open url to get address
import pdb

class Students(Model):

    def __init__(self, sid):
        self.sid = sid
        self.ds = self.get_client()

        # time and location:
        self.timestamp = datetime.time(datetime.now())
        self.lat = 0.0
        self.lon = 0.0

    ### getters

    def set_timestamp(self):
        self.timestamp = datetime.now()
        return self.timestamp

    def set_coordinates(self):
        url = "http://ip-api.com/json"
        data = json.load(urlopen(url))

        self.lat = data['lat']
        self.lon = data['lon']

        return [self.lat, self.lon]

    def get_timestamp(self):
        return self.timestamp

    def get_coordinates(self):
        return [self.lat, self.lon]

    ###

    def get_uni(self):
        query = self.ds.query(kind='student')
        query.add_filter('sid', '=', self.sid)
        result = list(query.fetch())
        return result[0]['uni']

    def get_courses(self):
        query = self.ds.query(kind='enrolled_in')
        query.add_filter('sid', '=', self.sid)
        enrolledCourses = list(query.fetch())
        result = list()
        for enrolledCourse in enrolledCourses:
            query = self.ds.query(kind='courses')
            query.add_filter('cid', '=', enrolledCourse['cid'])
            result = result + list(query.fetch())

        return result

    def get_secret_and_seid(self):
        query = self.ds.query(kind='enrolled_in')
        enrolled_in = list(query.fetch())
        results = list()
        #pdb.set_trace()
        for enrolled in enrolled_in:
            query = self.ds.query(kind='sessions')
            query.add_filter('cid', '=', enrolled['cid'])
            sessions = list(query.fetch())
            for session in sessions:
                #pdb.set_trace()
                if session['expires'].replace(tzinfo=None) > datetime.now():
                    results.append(session)
            # results = results + list(query.fetch())
        if len(results) == 1:
            secret = results[0]['secret']
            seid = results[0]['seid']
            setimestamp = results[0]['timestamp']
            secoordinate = resutls[0]['coordinate']
            ###
            cid = results[0]['cid']
        else:
            secret, seid, setimestamp, secoordinate, cid = 999, -1, datetime.now(), [40.8584, -73.0996], -1
        return secret, seid, setimestamp, secoordinate, cid

    def has_signed_in(self):
        ### _, seid = self.get_secret_and_seid()
        _, seid,timestamp, coordinate, cid = self.get_secret_and_seid()

        if seid == -1:
            return False
        else:
            query = self.ds.query(kind='sessions')
            query.add_filter('seid', '=', int(seid))
            sessions = list(query.fetch())
            results = list()
            for session in sessions:
                query = self.ds.query(kind='attendance_records')
                query.add_filter('seid', '=', int(session['seid']))
                query.add_filter('sid', '=', self.sid)
                results = results + list(query.fetch())
            return True if len(results) == 1 else False

    def insert_attendance_record(self, seid):
        key = self.ds.key('attendance_records')
        entity = datastore.Entity(
            key=key)
        entity.update({
            'sid': self.sid,
            'seid': int(seid)
        })
        self.ds.put(entity)

    def get_num_attendance_records(self, cid):
        query = self.ds.query(kind='sessions')
        query.add_filter('cid', '=', int(cid))
        sessions = list(query.fetch())
        results = list()
        for session in sessions:
            query = self.ds.query(kind='attendance_records')
            query.add_filter('seid', '=', session['seid'])
            query.add_filter('sid', '=', self.sid)
            results = results + list(query.fetch())
        return len(results)

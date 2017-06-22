from model import Model
from datetime import datetime, date, timedelta
from random import randint
from google.cloud import datastore

import json                     # for getting coordinates
from urllib2 import urlopen     # for open url to get address
import pdb                      # debug only

class Courses(Model):

    def __init__(self, cid=-1):
        self.cid = cid
        self.now = datetime.time(datetime.now())
        self.today = date.today()
        self.ds = self.get_client()

        ## adding coordinates and sign-in time
        self.timestamp = datetime.time(datetime.now())
        self.lat = 0.0
        self.lon = 0.0              # will modify it when get ip address in imhere view_class

    ### getters
    def get_coordinates(self):
        #pdb.set_trace()
        return [self.lat, self.lon]

    def get_timestamp(self):
        return self.timestamp
    ###

    def get_course_name(self):
        query = self.ds.query(kind='courses')
        query.add_filter('cid', '=', int(self.cid))
        result = list(query.fetch())
        return result[0]['name']

    def get_students(self):
        query = self.ds.query(kind='enrolled_in')
        query.add_filter('cid', '=', int(self.cid))
        enrolled_in = list(query.fetch())
        results = list()
        for enrolled in enrolled_in:
            query = self.ds.query(kind='user')
            query.add_filter('id', '=', enrolled['sid'])
            results = results + list(query.fetch())
        return results

    def add_student(self, uni):
        query = self.ds.query(kind='student')
        query.add_filter('uni', '=', uni)
        result = list(query.fetch())

        if len(result) == 1:
            # found a student with uni, attempt to add to enrolled_in
            sid = result[0]['sid']
            query = self.ds.query(kind='enrolled_in')
            query.add_filter('sid', '=', sid)
            query.add_filter('cid', '=', int(self.cid))
            result = list(query.fetch())
            if len(result) > 0:
                # failed because already in enrolled_in
                return -2

            key = self.ds.key('enrolled_in')
            entity = datastore.Entity(
                key=key)
            entity.update({
                'sid': sid,
                'cid': int(self.cid)
            })
            self.ds.put(entity)
            return 0

        else:
            # invalid uni
            return -1

    def remove_student(self, uni):
        query = self.ds.query(kind='student')
        query.add_filter('uni', '=', uni)
        result = list(query.fetch())

        if len(result) == 1:
            # found a student with uni, attempt to remove from enrolled_in
            sid = result[0]['sid']

            query = self.ds.query(kind='enrolled_in')
            query.add_filter('sid', '=', sid)
            query.add_filter('cid', '=', int(self.cid))
            result = list(query.fetch())

            if len(result) > 0:

                self.ds.delete(result[0].key)

                query = self.ds.query(kind='sessions')
                query.add_filter('cid', '=', int(self.cid))
                sessions = list(query.fetch())
                attendanceRecords = list()
                for session in sessions:
                    query = self.ds.query(kind='attendance_records')
                    query.add_filter('seid', '=', int(session['seid']))
                    attendanceRecords = attendanceRecords + list(query.fetch())
                for attendanceRecord in attendanceRecords:
                    self.ds.delete(attendanceRecord.key)
                return 0
            else:
                # failed because it was not in enrolled_in to begin with
                return -3
        else:
            # invalid uni
            return -1

    def get_active_session(self):
        '''Return the seid of an active session if it exists,
        otherwise return -1.
        '''
        query = self.ds.query(kind='sessions')
        query.add_filter('cid', '=', int(self.cid))
        sessions = list(query.fetch())
        results = list()
        for session in sessions:
            if session['expires'].replace(tzinfo=None) > datetime.now():
                results.append(session)

        return results[0]['seid'] if len(results) == 1 else -1

    def close_session(self, seid):
        if seid == -1:
            return

        query = self.ds.query(kind='sessions')
        query.add_filter('seid', '=', int(seid))
        entity = list(query.fetch())[0]
        entity.update({
            'expires': datetime.now()
        })
        self.ds.put(entity)

        query = self.ds.query(kind='courses')
        query.add_filter('cid', '=', int(self.cid))
        entity = list(query.fetch())[0]
        entity.update({
            'active': 0
        })
        self.ds.put(entity)


    def open_session(self):
        '''Opens a session for this course
        and returns the secret code for that session.
        '''
        # auto-generated secret code for now
        randsecret = randint(1000, 9999)

        ### get coordinate
        url = "http://ip-api.com/json"
        data = json.load(urlopen(url))

        self.lat = data['lat']
        self.lon = data['lon']
        pdb.set_trace()


        key = self.ds.key('sessions')
        entity = datastore.Entity(
            key=key)
        entity.update({
            'cid': int(self.cid),
            'secret': int(randsecret),      
            'coordinate': (self.lat, self.lon),           ### adding value here
            'timestamp': datatime.now(),
            'expires': datetime.now() + timedelta(days=1)
        })
        self.ds.put(entity)
        seid = entity.key.id
        entity.update({
            'seid': seid
        })
        self.ds.put(entity)

        key = self.ds.key('courses', int(self.cid))
        results = self.ds.get(key)
        entity = datastore.Entity(
            key=key)
        entity.update({
            'name': results['name'],
            'active': 1,
            'cid': results['cid']
        })
        self.ds.put(entity)

        return randsecret

    def get_secret_code(self):
        query = self.ds.query(kind='courses')
        query.add_filter('cid', '=', int(self.cid))
        courses = list(query.fetch())
        results = list()
        for course in courses:
            query = self.ds.query(kind='sessions')
            query.add_filter('cid', '=', course['cid'])
            sessions = list(query.fetch())
            for session in sessions:
                if session['expires'].replace(tzinfo=None) > datetime.now():
                    results.append(session)
        return results[0]['secret'] if len(results) == 1 else None

    def get_num_sessions(self):
        query = self.ds.query(kind='sessions')
        query.add_filter('cid', '=', int(self.cid))
        results = list(query.fetch())
        return len(results)

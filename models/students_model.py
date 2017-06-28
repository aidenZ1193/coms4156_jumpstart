from model import Model
from datetime import datetime, date
from google.cloud import datastore
import pdb
import pytz
from pytz import timezone
class Students(Model):

    def __init__(self, sid):
        self.sid = sid
        self.ds = self.get_client()

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
        #pdb.set_trace()
        for enrolledCourse in enrolledCourses:
            query = self.ds.query(kind='courses')
            query.add_filter('cid', '=', enrolledCourse['cid'])
            result = result + list(query.fetch())

        return result

    # Also have to change the function name as well.
    def get_secret_and_seid(self):
        query = self.ds.query(kind='enrolled_in')
        enrolled_in = list(query.fetch())
        results = list()
        eastern = timezone('US/Eastern')
        # tz = pytz.timezone('America/New_York')
        current_time = datetime.now()
        # tz = pytz.timezone('America/New_York')
        for enrolled in enrolled_in:
            query = self.ds.query(kind='sessions')
            query.add_filter('cid', '=', enrolled['cid'])
            sessions = list(query.fetch())
            for session in sessions:
                if session['expires'] > eastern.localize(current_time):
                    results.append(session)
            # results = results + list(query.fetch())
        if len(results) == 1:
            secret = results[0]['secret']
            seid = results[0]['seid']

            # get course sign in timestamp
            if 'timestamp' not in results[0] or 'coordinate' not in results[0]:
                
                # time = datetime.now()
                # pytz.utc.localize(time, is_dst=None).astimezone(tz)
                course_timestamp = eastern.localize(current_time)
                course_coordinate = [0, 0]
            else:
                course_timestamp = results[0]['timestamp']
                course_coordinate = results[0]['coordinate']
        else:
            # if nothing happend, let timestamp to be now
            secret, seid, course_timestamp, course_coordinate = 999, -1, eastern.localize(current_time), (0,0)

        # Return student_timestamp as well
        return secret, seid, course_timestamp, course_coordinate

    def has_signed_in(self):

        # Return _st (student_timestamp) as well. But there is no use for us to use it inside this function
        # Also return _sc (student_coordiante) although it is not being used inside this function.
        _, seid, _st, _sc = self.get_secret_and_seid()

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

    def get_attendance_record(self):
        _, seid, _st, _sc = self.get_secret_and_seid()
        eastern = timezone('US/Eastern')

        current_time = datetime.now()
        if seid == -1:
            return datetime.now(), [0, 0]
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
            if len(results) == 1:
                return results[0]['timestamp'], results[0]['coordinate']
            else:
                return eastern.localize(current_time), [0, 0]


    def insert_attendance_record(self, seid, timestamp, coordinate):
        key = self.ds.key('attendance_records')
        entity = datastore.Entity(
            key=key)
        entity.update({
            'sid': self.sid,
            'seid': int(seid),
            # Add timestamp and coordinate related with student id and session id
            'timestamp': timestamp,
            'coordinate':coordinate,
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



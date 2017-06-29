from model import Model
from datetime import datetime, date, timedelta
from google.cloud import datastore
import pdb

class Teachers(Model):

    def __init__(self, tid):
        self.tid = tid
        self.now = datetime.now()
        self.today = date.today()
        self.ds = self.get_client()

    def get_courses(self):
        query = self.ds.query(kind='teaches')
        query.add_filter('tid', '=', self.tid)
        teaches = list(query.fetch())
        results = list()
        for teach in teaches:
            query = self.ds.query(kind='courses')
            query.add_filter('cid', '=', teach['cid'])
            results = results + list(query.fetch())
        return results

    def get_courses_with_session(self):

        query = self.ds.query(kind='teaches')
        query.add_filter('tid', '=', self.tid)
        teaches = list(query.fetch())
        courses = list()
        for teach in teaches:
            query = self.ds.query(kind='courses')
            query.add_filter('cid', '=', teach['cid'])
            courses = courses + list(query.fetch())
        results = list()
        for course in courses:
            query = self.ds.query(kind='sessions')
            query.add_filter('cid', '=', course['cid'])
            sessions = list(query.fetch())

            for session in sessions:
                if session['expires'].replace(tzinfo=None) > datetime.now():
                    results.append(session)
            if len(results) == 1:
                course['secret'] = results[0]['secret']

                # We get the timestamp of sessions and let store it to course timestamp as well. 
                # for later use
                if 'timestamp' not in results[0] or 'coordinate' not in results[0]:

                    # tz = pytz.timezone('America/New_York')
                    # time = datetime.now()
                    # pytz.utc.localize(time, is_dst=None).astimezone(tz)
                    course['timestamp'] = datetime.now()  + timedelta(hours=-4)                   
                    course['coordinate'] = [0, 0]
                else:
                    course['timestamp'] = results[0]['timestamp'] + timedelta(hours=-4)
                    course['coordinate'] = results[0]['coordinate']
        # result = courses + sessions
        return courses


    def add_course(self, course_name):
        key = self.ds.key('courses')
        entity = datastore.Entity(
            key=key)
        entity.update({
            'name': course_name,
            'active': 0
        })
        self.ds.put(entity)
        cid = entity.key.id
        entity.update({
            'cid': cid
        })
        self.ds.put(entity)

        key = self.ds.key('teaches')
        entity = datastore.Entity(
            key=key)
        entity.update({
            'tid': self.tid,
            'cid': cid
        })
        self.ds.put(entity)
        return cid

    def remove_course(self, cid):
        key = self.ds.key('courses', int(cid))
        self.ds.delete(key)

        # remove course from students' enrolled list
        query = self.ds.query(kind='enrolled_in')
        query.add_filter('cid', '=', int(cid))
        results = list(query.fetch())
        for result in results:
            self.ds.delete(result.key)

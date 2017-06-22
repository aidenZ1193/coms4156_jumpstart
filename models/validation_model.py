from model import Model
from models import courses_model
from datetime import datetime, date, timedelta

import json                     # for getting coordinates
from urllib2 import urlopen     # for open url to get address
from geopy.distance import great_circle		# calculate distance
import pdb                      # debug only

class ValidationCheck(Model):
	def __init__(self, setimestamp, secoordinate, sm):
		#self.sid = sid
		#self.cid = cid

		# cm = courses_model.Courses(self.cid)
		# sm = students_model.Students(self.sid)

		self.student_timestamp = sm.get_timestamp()
		#self.teacher_timestamp = cm.get_timestamp()
		self.student_coordinates = sm.get_coordinates()
		#self.teacher_coordinates = cm.get_coordinates()
		self.teacher_timestamp = setimestamp
		self.teacher_coordinates = secoordinate

		self.time_pass = False
		self.location_pass = False

	def timestamp_check(self):
		### convert to minutes
		#pdb.set_trace()
		if (self.student_timestamp - self.teacher_timestamp).total_seconds() / 60  <= 15:
			self.time_pass = True
		
		return self.time_pass

	def coordinates_check(self):
		student_location = (self.student_coordinates[0], self.student_coordinates[1])
		teacher_location = (self.teacher_coordinates[0], self.teacher_coordinates[1])

		distance = great_circle(student_location, teacher_location).meters

		if distance <= 25:
			self.location_pass = True

		return self.location_pass

	def validate(self):
		pdb.set_trace()
		if self.timestamp_check() and self.coordinates_check():
			return True
		return False


## adding these just trying to push





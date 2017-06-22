from models import model, users_model
import unittest 
from google.cloud import datastore

import imhere
import uuif



TID = 1

TEACHER = {
	'family_name': "Ao",
	'name': "Oscar Ao",
	'email': "aoxiao@cs.columbia.edu",
	'given_name': "Oscar",
	'locale':'en',
	'id':'1',
	'hd':'columbia.edu',
	'verified_email':True
}

SID_1 = 101

STUDENT_1 = {
	'family_name': "Shen",
	'name': "Dailin Shen",
	'email': "ds3420@columbia.edu",
	'given_name': "Dailin",
	'locale':'en',
	'id': '101',
	'hd': 'columbia.edu',
	'verified_email': True
}

SID_2 = 102

STUDENT_2 = {
	'family_name': "Zhang",
	'name': "Xiao Zhang",
	'email': "xz2627@columbia.edu",
	'given_name': "Xiao",
	'locale':'en',
	'id': '102',
	'hd': 'columbia.edu',
	'verified_email': True
}


class teacher_tests(unittest.TestCase):

	## setting up in here, including teacher's account login, and connection to datastore
	## need to set up all attributes: course name, session, etc
	
	def setUp(self):
		imhere.app.secret_key = str(uuid.uuid4())

		self.user_instance = users_model.Users()
		self.user_instance.get_or_create_user(TEACHER)
		self.user_instance.get_or_create_user(STUDENT_1)

		self.model_instance = model.Model()
		self.ds = self.model_instance.get_client()

		key = self.ds.key('student')
		entity = datastore.Entity(key = key)
		entity.update({
			'sid': int(STUDENT_1['id']),
			'uni': 'ds3420'
		})
		self.ds.put(entity)

		key = self.ds.key('teacher')
		entity = datastore.Entity(key=key)
		entity.update({
			'tid': int(TEACHER['id'])
		})
		self.ds.put(entity)

		with imhere.app.test_client() as t_client:
			with t_client.session_transaction() as t_client_session:
				t_client_session['credentials'] = 'o93ir8ds23j'
				t_client_session['google_user'] = TEACHER
				t_client_session['id'] = TID
				t_client_session['is_student'] = False
				t_client_session['is_teacher'] = True
			# add 4 courses
			self.prof = teachers_model.Teachers(t_client.session['id'])
			self.stu1 = students_model.Students
			self.test_teacher()
			self.test_courses_with_student()

	## tearing dowm here, including log out and clear
	def teardown(self):
		pass

	## pass a teacher account to both is_student and is_teacher
	def test_index(self):
		pass


	## add 4 courses, one by one, and remove in reverse order
	def test_teacher(self):

		self.prof.add_course("COMS1111")
		self.prof.add_course("COMS2222")
		self.prof.add_course("COMS3333")
		self.prof.add_course("COMS4444")

		# get courses list
		courses = self.prof.get_courses()
		# check each course name
		assertIn("COMS1111", courses)
		assertIn("COMS2222", courses)
		assertIn("COMS3333", courses)
		assertIn("COMS4444", courses)

		# remove three of them
		self.prof.remove_course("COMS2222")
		self.prof.remove_course("COMS3333")
		self.prof.remove_course("COMS4444")

		# check again
		courses = self.prof.get_courses()
		assertNotIn("COMS2222", courses)
		assertNotIn("COMS3333", courses)
		assertNotIn("COMS4444", courses)

		# remove last one
		self.prof.remove_course("COMS1111")
		courses = self.prof.get_courses()

		# now courses list should be none
		assertIsNone(courses)

	def test_courses_with_student(self):
		# add two course to prof
		cid1 = self.prof.add_course("COMS4156")		
		cid2 = self.prof.add_course("COMS1111")
		course1 = courses_model.Courses(cid1)
		course2 = courses_model.Courses(cid2)

		# add 2 students to it
		assertEqual(course1.add_student("xz2627"), 0)
		assertEqual(course2.add_student("ds3420"), 0)

		# get student list and check it's elements
		students1 = course1.get_students()
		students2 = course2.get_students()
		assertIn("xz2627", students1)
		assertIn("ds3420", students2)

		# testing with interaction of web




	def test_validation(self):
		# create instance of validationCheck for both course & student
		check1 = validation_model.ValidationCheck(cid1, STUDENT_1['id'])
		check2 = validation_model.ValidationCheck(cid2, STUDENT_2['id'])

		assertTrue(check1.timestamp_check())



if __name__ == '__main__':
	unittest.main()



import unittest
from google.cloud import datastore
import uuid
import flask

import imhere
from models import model, users_model, index_model, teachers_model, students_model, courses_model


class unit_tests(unittest.TestCase):
	TEACHER_ACCOUNT = {
		'family_name': 'Shen',
	    'name': 'Dailin Shen',
	    'email': 'ds3420@columbia.edu',
	    'given_name': 'Dailin',
	}
	TEACHER_ACCOUNT_ID = 1

	STUDENT_ACCOUNT = {
		'family_name': 'Shen',
	    'name': 'Dailin Shen',
	    'email': 'dailinshen@gmail.com',
	    'given_name': 'Dailin',
	}
	STUDENT_ACCOUNT_ID = 100

	def setUp(self):
		imhere.app.testing = True
		imhere.app.secret_key = str(uuid.uuid4())
		self.app = imhere.app.test_client()

		teacher_instance = teachers_model.Teachers(TEACHER_ACCOUNT_ID)
		classname_1 = "COMS 4111"
		self.cid_1 = teacher_instance.add_course(classname_1)
		course_instance_1 = courses_model.Courses(self.cid_1)
		course_instance_1.add_student('ds3420')

		classname_2 = "COMS 4112"
		self.cid_2 = teacher_instance.add_course(classname_2)
		course_instance_2 = courses_model.Courses(self.cid_2)
		course_instance_2.add_student('xz2627')
	
	def test_teacher(self):
		with imhere.app.test_client() as t_t:
			# log in with teacher account
			with t_t.seesion_transaction() as session_teacher:
				self.login(session_teacher, TEACHER_ACCOUNT, TEACHER_ACCOUNT_ID)
				session_teacher['is_teacher'] = True
			rv = t_t.get('/teacher/')
			assertEqual(200, res.status_code)

	def login(self, sess, username, user_id):
	    sess['credentials'] = 'blah'
	    sess['google_user'] = user
	    sess['id'] = userid
	    sess['is_student'] = False
	    sess['is_teacher'] = False

	# Add two classes and students
	def test_teacher_add_class(self):
		with imhere.app.test_client() as t_t:
			rv = t_t.get("/teacher/add_class")
			assertEqual(302, rv.status_code)
			with t_t.seesion_transaction() as session_teacher:
				self.login(session_teacher, TEACHER_ACCOUNT, TEACHER_ACCOUNT_ID)
				session_teacher['is_teacher'] = True
			rv = t_t.get("/teacher/add_class")
			assertEqual(200, rv.status_code)
			
			# No UNIS
			data = {
				'unis': '',
				'classname':'COMS 2738'
			}	
			rv = t_t.post("/teacher/add_class", data=data, follow_redirects=True)
			assertIn("COMS 2738", rv.data)
			assertEqual(200, rv.status_code)

			data = {
				'unis': 'ko0987',
				'classname':'COMS 2732'
			}	
			rv = t_t.post("/teacher/add_class", data=data, follow_redirects=True)
			assertIn("COMS 2732", rv.data)
			assertIn("COMS 2738", rv.data)
			assertEqual(200, rv.status_code)

			# INVALID UNIS
			data = {
				'unis': '9ils9',
				'classname':'COMS 2738'
			}	
			rv = t_t.post("/teacher/add_class", data=data)
			assertIn("Invalid UNI's entered, please recreate the class", rv.data)
			
	def test_teacher_session(self):
		with imhere.app.test_client() as t_t:
			rv = t_t.get("/teacher/")
			assertEqual(302, rv.status_code)
			with t_t.seesion_transaction() as session_teacher:
				self.login(session_teacher, TEACHER_ACCOUNT, TEACHER_ACCOUNT_ID)
				session_teacher['is_teacher'] = True
			rv = t_t.get("/teacher/")
			assertIn("COMS 4111", rv.status_code)
			assertIn('Open Attendance Window', rv.data)
       		assertIn('Secret Code', rv.data)
			assertEqual(200, rv.status_code)

			data = {"open": self.cid_2}
			rv = t_t.post("/teacher/", data=data)
			assertIn("Close Attendance Window", rv.data)
			assertIn("Secret Code", rv.data)

			data = {"close": self.cid_2}
			rv = t_t.post("/teacher/", data=data)
			assertIn("Open Attendance Window", rv.data)
			assertIn("Secret Code", rv.data)

	def test_teacher_remove_class(self):
		with imhere.app.test_client() as t_t:
			rv = t_t.get("/teacher/remove_class")
			assertEqual(302, rv.status_code)
			with t_t.seesion_transaction() as session_teacher:
				self.login(session_teacher, TEACHER_ACCOUNT, TEACHER_ACCOUNT_ID)
				session_teacher['is_teacher'] = True
			rv = t_t.get("/teacher/remove_class")
			assertin("Class List", rv.data)
			assertIn("Remove Class", rv.data)
			assertIn("COMS 4111", rv.data)
			assertIn("COMS 4112", rv.data)
			assertEqual(200, rv.status_code)

			data = {'cid': self.cid_2}
			rv = t_t.post("/teacher/remove_class", data=payload, follow_redirects=True)
			assertIn("Class List", rv.data)
			assertIn("Add Class", rv.data)
			assertIn("Remove Class", rv.data)
			assertIn("COMS 4111", rv.data)
			assertNotIn("COMS 4112", rv.data)
			assertEqual(200, rv.status_code)

	def test_students(self):
		with imhere.app.test_client() as t_s:
			rv = t_s.get("/student/")
			assert(302 == rv.status_code)
			with t_s.seesion_transaction() as session_student:
				self.login(session_student, STUDENT_ACCOUNT, STUDENT_ACCOUNT_ID)
				session_student['is_teacher'] = False
				session_student['is_student'] = True
			# add student, nto yet open window
			rv = t_s.get('/student/')
			assertIn("Student View", rv.data)

			course_1 = courses_model.Courses(self.cid_1)
			course_1.add_student("uu0000")

			rv = t_s.get("/student/")
			assertIn("COMS 4111", rv.data)
			assertIn("No sign-in window", rv.data)

			# Open Sign-in & get secret code
			real_secret_code = course_1.open_session()
			rv = t_s.get('/student/')
			assertIn("Sign in now!", rv.data)
			assertIn("Student View", rv.data)

			data = {'secret_code':0000}
			rv = t_s.post("/student/", data=data, follow_redirects=True)
			assertIn("Invalid Secret Code!", rv.data)
			
			data = {'secret_code':real_secret_code}
			rv = t_s.post("/student/", data=data, follow_redirects=True)
			assertIn("Successfully signed-in!", rv.data)

			# Check timstamp & coordiantes
			assertIn("Valid Timestamp!", rv.data)
			assertIn("Valid Coordinate!", rv.data)
			assertEqual(202, rv.status_code)


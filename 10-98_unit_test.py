import unittest
from google.cloud import datastore
import uuid
import flask

#from google.appengine.ext import db
import imhere
from models import model, users_model, index_model, teachers_model, students_model, courses_model
import pdb


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

STUDENT_ACCOUNT_2 = {
	'family_name': 'Zhang',
	'name': 'Xiao Zhang',
	'email': 'xz2627@columbia.edu',
	'id': 101,
	'given_name': 'Xiao',
}
STUDENT_ACCOUNT_2_ID = 101


class unit_tests(unittest.TestCase):

	cid_1 = 0
	cid_2 = 0

	sid_2 = 0
	

	# def setUp(self):
	# 	imhere.app.testing = True
	# 	imhere.app.secret_key = str(uuid.uuid4())
	# 	self.app = imhere.app.test_client()

	# 	teacher_instance = teachers_model.Teachers(TEACHER_ACCOUNT_ID)
	# 	classname_1 = "COMS 4111"
	# 	cid_1 = teacher_instance.add_course(classname_1)
	# 	course_instance_1 = courses_model.Courses(cid_1)
	# 	course_instance_1.add_student('ds3420')

	# 	classname_2 = "COMS 4112"
	# 	cid_2 = teacher_instance.add_course(classname_2)
	# 	course_instance_2 = courses_model.Courses(cid_2)
	# 	course_instance_2.add_student('ds3420')

	def db(self):
		imhere.app.secret_key = str(uuid.uuid4())

	
	def test_a_teacher(self):


		imhere.app.testing = True
		imhere.app.secret_key = str(uuid.uuid4())
		self.app = imhere.app.test_client()

		teacher_instance = teachers_model.Teachers(TEACHER_ACCOUNT_ID)
		classname_1 = "COMS 4111"
		self.__class__.cid_1 = teacher_instance.add_course(classname_1)
		course_instance_1 = courses_model.Courses(self.__class__.cid_1)
		#course_instance_1.add_student('xz2222')

		classname_2 = "COMS 4112"
		self.__class__.cid_2 = teacher_instance.add_course(classname_2)

		course_instance_2 = courses_model.Courses(self.__class__.cid_2)
		self.__class__.sid_2 = course_instance_2.add_student('xz2222')



		with imhere.app.test_client() as t_t:
			# log in with teacher account
			with t_t.session_transaction() as session_teacher:
				self.login(session_teacher, TEACHER_ACCOUNT, TEACHER_ACCOUNT_ID)
				session_teacher['is_teacher'] = True
			rv = t_t.get('/teacher/')
			self.assertEqual(200, rv.status_code)

	def login(self, sess, username, user_id):
	    sess['credentials'] = 'blah'
	    sess['google_user'] = username
	    sess['id'] = user_id
	    sess['is_student'] = False
	    sess['is_teacher'] = False

	# Add two classes and students
	def test_b_teacher_add_and_remove_class(self):
		def db():

			imhere.app.secret_key = str(uuid.uuid4())
		with imhere.app.test_client() as t_t:
			rv = t_t.get("/teacher/add_class")
			self.assertEqual(302, rv.status_code)
			with t_t.session_transaction() as session_teacher:
				self.login(session_teacher, TEACHER_ACCOUNT, TEACHER_ACCOUNT_ID)
				session_teacher['is_teacher'] = True

			rv = t_t.get("/teacher/add_class")
			self.assertEqual(200, rv.status_code)
			
			# No UNIS
			data = {
				'unis': '',
				'classname':'COMS 2738'
			}	
			rv = t_t.post("/teacher/add_class", data=data, follow_redirects=True)
			self.assertIn("COMS 2738", rv.data)
			self.assertIn("Add a Class", rv.data)
			self.assertEqual(200, rv.status_code)

			#pdb.set_trace()

			data = {
				'unis': 'xz2627',
				'classname':'COMS 2732'
			}	
			rv = t_t.post("/teacher/add_class", data=data, follow_redirects=True)
			self.assertIn("COMS 2738", rv.data)
			self.assertIn("COMS 2732", rv.data)
			self.assertEqual(200, rv.status_code)

			#pdb.set_trace()

			# INVALID UNIS
			data = {
				'unis': '9ils9',
				'classname':'COMS 2738'
			}	
			rv = t_t.post("/teacher/add_class", data=data)
			self.assertIn("Invalid UNI's entered, please recreate the class", rv.data)


			# Remove class starts from here
			coursename_2remove = "COMS 2738"

			## get cid


			# query = "select cid from courses where name = 'COMS 2738'"
   #      	cursor = db.execute(query)
   #      	for item in cursor:
   #      		cid = item[0]
   #      	data = {'cid': cid}
   			datastore_client = datastore.Client()
	        query = datastore_client.query(kind='courses')
	        query.add_filter('name', '=', coursename_2remove)
	        courses_2remove = list(query.fetch())
	        #pdb.set_trace()
	        self.assertEqual(len(courses_2remove), 1)
	        data = {'cid':courses_2remove[0]['cid']}

	        rv = t_t.post("/teacher/remove_class", data=data, follow_redirects=True)
	        # Remove a Class is the title.
	        self.assertIn("Remove a Class", rv.data)
	        self.assertNotIn("COMS 2738",rv.data)

	        
	    	
	      	#coursename_2remove = "COMS 2732"

	        # query = "select cid from courses where name = 'COMS 2732'"
        	# cursor = db.execute(query)
        	# for item in cursor:
        	# 	cid = item[0]
        	# data = {'cid': cid}

	        # query = t_t.session.query(kind='courses')
	        # query.add_filter('name', '=', coursename_2remove)
	        # courses_2remove = list(query.fetch())
	        # self.assertEqual(len(courses_2remove), 1)
	        # data = {'cid':courses_2remove[0]['cid']}\
	        self.assertIn("COMS 2732", rv.data)
	        coursename_2remove = "COMS 2732"

	        query = datastore_client.query(kind='courses')
	        query.add_filter('name', '=', coursename_2remove)
	        courses_2remove = list(query.fetch())
	        data = {'cid':courses_2remove[0]['cid']}

	        rv = t_t.post("/teacher/remove_class", data=data, follow_redirects=True)
	        self.assertIn("Remove a Class", rv.data)
	        self.assertNotIn("COMS 2732", rv.data)	 

	        t_t.get('/oauth/logout')            
        	rv = t_t.get('/teacher/')
        	self.assertEqual(302, rv.status_code)

						
	def test_c_teacher_session(self):
		with imhere.app.test_client() as t_t:
			rv = t_t.get("/teacher/")
			self.assertEqual(302, rv.status_code)
			with t_t.session_transaction() as session_teacher:
				self.login(session_teacher, TEACHER_ACCOUNT, TEACHER_ACCOUNT_ID)
				session_teacher['is_teacher'] = True
			rv = t_t.get("/teacher/")
			#pdb.set_trace()
			self.assertIn("COMS 4111", rv.data)
			self.assertIn('Open Attendance Window', rv.data)
       		self.assertEqual(200, rv.status_code)

       		#pdb.set_trace()


	       	data = {"open" : self.cid_2}
	       	rv = t_t.post("/teacher/", data = data)
	       	self.assertIn("Close Attendance Window", rv.data)
	       	self.assertIn("Secret Code", rv.data)

	       	## check for validation information
	       	self.assertIn("Timestamp:", rv.data)
	       	self.assertIn("Coordinate:", rv.data)
	       		
	       	data = {"close": self.cid_2}
	       	rv = t_t.post("/teacher/", data=data)
	       	#pdb.set_trace()
	       	self.assertIn("Open Attendance Window", rv.data)	
	       	self.assertNotIn("Secret Code", rv.data)	

	       	t_t.get('/oauth/logout')            
	        rv = t_t.get('/teacher/')
	        self.assertEqual(302, rv.status_code)       		

			
	def test_d_teacher_remove_class(self):
		with imhere.app.test_client() as t_t:
			rv = t_t.get("/teacher/remove_class")
			self.assertEqual(302, rv.status_code)
			with t_t.session_transaction() as session_teacher:
				self.login(session_teacher, TEACHER_ACCOUNT, TEACHER_ACCOUNT_ID)
				session_teacher['is_teacher'] = True
			rv = t_t.get("/teacher/remove_class")
			#self.assertIn("Class List", rv.data)
			self.assertIn("Remove Class", rv.data)
			self.assertIn("COMS 4111", rv.data)
			self.assertIn("COMS 4112", rv.data)
			self.assertEqual(200, rv.status_code)

			#pdb.set_trace()

			data = {'cid': self.cid_2}
			#pdb.set_trace()
			rv = t_t.post("/teacher/remove_class", data=data, follow_redirects=True)
			#self.assertIn("Class List", rv.data)
			self.assertIn("Add a Class", rv.data)
			self.assertIn("Remove a Class", rv.data)
			self.assertIn("COMS 4111", rv.data)

			#pdb.set_trace()
			self.assertNotIn("COMS 4112", rv.data)
			self.assertEqual(200, rv.status_code)

			t_t.get('/oauth/logout')            
        	rv = t_t.get('/teacher/')
        	self.assertEqual(302, rv.status_code)

	def test_e_students_signin(self):
		with imhere.app.test_client() as t_s:
			rv = t_s.get("/student/")
			self.assertEqual(302, rv.status_code)

			with t_s.session_transaction() as session_student:

				self.login(session_student, STUDENT_ACCOUNT_2,self.sid_2)	# STUDENT_ACCOUNT_2_ID
				session_student['is_teacher'] = False
				session_student['is_student'] = True

				# add student, nto yet open window
			rv = t_s.get('/student/')
			#pdb.set_trace()
			self.assertIn("Switch To Teacher View", rv.data)

			course_1 = courses_model.Courses(self.cid_1)
			course_1.add_student("xz2222")

			rv = t_s.get("/student/")
			self.assertIn("COMS 4111", rv.data)
			self.assertIn("No Sign-in Window Available!", rv.data)

			# Open Sign-in & get secret code
			real_secret_code = course_1.open_session()
			#pdb.set_trace()
			rv = t_s.get('/student/')
			self.assertIn("Sign in now!", rv.data)
			self.assertIn("Student View", rv.data)
			data = {'secret_code':0000}
			rv = t_s.post("/student/", data=data, follow_redirects=True)
			self.assertIn("Invalid Secret Code", rv.data)
				
			data = {'secret_code':real_secret_code}
			rv = t_s.post("/student/", data=data, follow_redirects=True)

			self.assertEqual(200, rv.status_code)
			self.assertIn("Successful sign-in!", rv.data)

			# Check timstamp & coordiantes
			self.assertIn("Time", rv.data)
			self.assertIn("Coordinate", rv.data)

			t_s.get('/oauth/logout')            
        	rv = t_s.get('/student/')
        	self.assertEqual(302, rv.status_code)
			


	def test_f_clear_classes(self):
		with imhere.app.test_client() as t_t:
			rv = t_t.get("/teacher/remove_class")
			self.assertEqual(302, rv.status_code)
			with t_t.session_transaction() as session_teacher:
				self.login(session_teacher, TEACHER_ACCOUNT, TEACHER_ACCOUNT_ID)
				session_teacher['is_teacher'] = True
			rv = t_t.get("/teacher/remove_class")
			#self.assertIn("Class List", rv.data)
			self.assertIn("Remove Class", rv.data)
			self.assertIn("COMS 4111", rv.data)
			self.assertEqual(200, rv.status_code)

			data = {'cid': self.cid_1}
			#pdb.set_trace()
			rv = t_t.post("/teacher/remove_class", data=data, follow_redirects=True)
			#self.assertIn("Class List", rv.data)
			self.assertIn("Add a Class", rv.data)
			self.assertNotIn("Remove Class", rv.data)
			self.assertNotIn("COMS 4112", rv.data)
			self.assertNotIn("COMS 4111", rv.data)
			self.assertEqual(200, rv.status_code)

			t_t.get('/oauth/logout')            
        	rv = t_t.get('/teacher/')
        	self.assertEqual(302, rv.status_code)



if __name__ == '__main__':
    unittest.main()

import mechanize
from bs4 import BeautifulSoup
import getpass, os, base64, re

class MMLSDownloader:
	#br = mechanize browser
	#subjects = dictionary of subject name as key with subject code as the data.
	def __init__(self):
		print "\tMMLS downloader - Keep your notes up to date!\n"
		self.br = mechanize.Browser()
		mechanize.HTTPSHandler()
		try:
			response = self.br.open("http://mmls.mmu.edu.my/")
		except:
			print "Offline!"
			raise SystemExit(0)

	def login(self):
		response = self.br.open("http://mmls.mmu.edu.my/")
		while True:
			userinfo = []
			if os.path.isfile("pwd.txt"):
				with open("pwd.txt") as f:
					userinfo = f.read().splitlines()
				try:
					userinfo[1] = base64.b64decode(userinfo[1])
				except:
					pass
			else:
				userinfo.append(raw_input("Student ID : "))
				userinfo.append(getpass.getpass("MMLS Password (Password will be hidden): "))
			self.br.select_form(nr=0)         
			self.br.form["stud_id"] = userinfo[0]
			self.br.form["stud_pswrd"] = userinfo[1]
			self.br.method = "POST"
			response = self.br.submit()

			soup = BeautifulSoup(self.br.response().read(), "html.parser")
			if soup.find("div", {"id" : "alert"}) == None:
				print "Logged in as " + userinfo[0]
				open("pwd.txt",'w').write(userinfo[0]+"\n"+base64.b64encode(userinfo[1]))
				break
			else:
				if os.path.isfile("pwd.txt"):
					os.remove("pwd.txt")
				print "Wrong username/password"

	def getSubject(self):
		#Get subject name and it's respective subject code and store it in a dict named subjects.
		response = self.br.open("http://mmls.mmu.edu.my/home")
		soup = BeautifulSoup(self.br.response().read(), "html.parser")
		soup = soup.find("div", {"class": "list-group "})
		self.subjects = {}
		for subject in soup.find_all('a'):
			if subject.get('href').split('/')[-1] in self.subjects.values():
				continue
			self.subjects[subject.string] = subject.get('href').split('/')[-1]

	def createSubjFolder(self):
		#Prints subject names and creates each respective directory if not created
		print "\nSubjects you are taking this trimester"
		for SubjName in self.subjects:
			print "\t"+SubjName
			#Make directories in current directory for each subject
			try:
				os.makedirs('./'+SubjName)
			except OSError:
				pass
			try:
				os.makedirs('./'+SubjName+'/Lecture Notes')
			except OSError:
				pass
			try:
				os.makedirs('./'+SubjName+'/Tutorial and Labs')
			except OSError:
				pass
		#Newline
		print
		
	def download_handler(self):
		for subject in self.subjects:
			print "Checking files to download for " + subject
			self.download_notes(subject)
			self.download_outline(subject)
			self.download_announcement(subject)

	def download_outline(self,subject):	
		courseOutline = "https://mmls.mmu.edu.my/courseOutline:"
		response = self.br.open(courseOutline+self.subjects[subject])
		soup = BeautifulSoup(self.br.response().read(),"html.parser")
		response.set_data(self.fixParseError(soup))
		self.br.set_response(response)

		for objects in soup.find_all('object'):
			if objects['type'] == 'application/pdf':
				file_name = "[Course Outline] "+objects['data'].split('/')[-1]
				modifiedURL = re.sub(' ','%20',objects['data']) #Spaces in URL are causing HTTP 404 error, so here's a fix.
				fpath = subject+"/"+file_name
				if os.path.isfile(fpath) == False:
					print "...Downloading " + file_name
					response = self.br.open(modifiedURL)
					open(fpath,'wb').write(response.read())

	def download_announcement(self,subject):
		response = self.br.open("https://mmls.mmu.edu.my/"+self.subjects[subject])
		soup = BeautifulSoup(self.br.response().read(),"html.parser")
		response.set_data(self.fixParseError(soup))
		self.br.set_response(response)
		for forms in self.br.forms():
			if forms.attrs.get('action') == "https://mmls.mmu.edu.my/form-download-content":
				if re.search(r'announcement',str(forms)):
					file_name = forms['file_name']
					fpath = str(subject+"/[Announcement] "+file_name)
					if os.path.isfile(fpath) == False:
						print "...Downloading " + file_name
						self.br.form = forms
						self.br.method = "POST"
						response = self.br.submit()
						open(fpath, 'wb').write(response.read())
						response = self.br.open("https://mmls.mmu.edu.my/"+self.subjects[subject])
						soup = BeautifulSoup(self.br.response().read(),"html.parser")
						response.set_data(self.fixParseError(soup))
						self.br.set_response(response)

	def download_notes(self,subject):
		fastDL = "https://mmls.mmu.edu.my/fast-download:"
		response = self.br.open(fastDL+self.subjects[subject])
		soup = BeautifulSoup(self.br.response().read(),"html.parser")
		response.set_data(self.fixParseError(soup))
		self.br.set_response(response)
		count = 0
		#Handles download
		for forms in self.br.forms():
			if forms.attrs.get('action') == "https://mmls.mmu.edu.my/form-download-content":
				noteType = forms['file_path'].split('/')[-1]
				if noteType == 'notes':
					directory = 'Lecture Notes/'
				elif noteType == 'tutorial':
					directory = 'Tutorial and Labs/'
				elif noteType == 'assignment':
					directory = '[Assignment] '
				else:
					break
				fpath = str(subject+"/"+directory+forms['file_name'])
				if os.path.isfile(fpath) == False:
					print "...Downloading " + forms['file_name']
					self.br.form = forms
					self.br.method = "POST"
					response = self.br.submit()
					open(fpath, 'wb').write(response.read())
					response = self.br.open(fastDL+self.subjects[subject])
					soup = BeautifulSoup(self.br.response().read(),"html.parser")
					response.set_data(self.fixParseError(soup))
					self.br.set_response(response)

	def fixParseError(self,soup):
		#To avoid Parsing error: OPTION outside of select 
		for div in soup.findAll('select'):
		    div.extract()
		for div in soup.findAll('script'):
		    div.extract()
		return str(soup)


downloader = MMLSDownloader()
downloader.login()
downloader.getSubject()
downloader.createSubjFolder()
downloader.download_handler()
print "Updated."
raw_input('Press <ENTER> to continue')
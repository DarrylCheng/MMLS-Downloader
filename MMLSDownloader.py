import mechanize
from bs4 import BeautifulSoup
import getpass, os, base64

br = mechanize.Browser()
mechanize.HTTPSHandler()
print "\tMMLS downloader - Keep your notes up to date!\n"

try:
	response = br.open("http://mmls.mmu.edu.my/")
except:
	print "Offline!"
	raise SystemExit(0)

#HANDLES LOGIN
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

	br.select_form(nr=0)         
	br.form["stud_id"] = userinfo[0]
	br.form["stud_pswrd"] = userinfo[1]
	br.method = "POST"
	response = br.submit()

	soup = BeautifulSoup(br.response().read(), "html.parser")
	if soup.find("div", {"id" : "alert"}) == None:
		print "Logged in as " + userinfo[0]
		open("pwd.txt",'w').write(userinfo[0]+"\n"+base64.b64encode(userinfo[1]))
		break
	else:
		if os.path.isfile("pwd.txt"):
			os.remove("pwd.txt")
		print "Wrong username/password"

#Get subject name and code and store them in a list
soup = soup.find("div", {"class": "list-group "})
subjects = {}
for subject in soup.find_all('a'):
	if subject.get('href').split('/')[-1] in subjects.values():
		continue
	subjects[subject.string] = subject.get('href').split('/')[-1]

#Prints subject names and creates each respective directory if not created
print "\nSubjects you are taking this trimester"
for subjName in subjects:
	print "\t"+subjName
	#Make directories in current directory for each subject
	try:
		os.makedirs('./'+subjName)
	except OSError:
		pass
	try:
		os.makedirs('./'+subjName+'/Lecture notes')
	except OSError:
		pass
	try:
		os.makedirs('./'+subjName+'/Tutorial and labs')
	except OSError:
		pass
print #newline


#Initialize
fastDLLink = "https://mmls.mmu.edu.my/fast-download:"
# formAction = ["https://mmls.mmu.edu.my/download-note-all","https://mmls.mmu.edu.my/download-tutorial-all"]
# identifier = ["[Lecture] ","[Tutorial] "]

for subject in subjects: 
	#Get fast download page
	response = br.open(fastDLLink+subjects[subject])
	soup = BeautifulSoup(br.response().read(),"html.parser")

	#To avoid Parsing error: OPTION outside of select 
	for div in soup.findAll('select'):
	    div.extract()

	for div in soup.findAll('script'):
	    div.extract()

	response.set_data(str(soup))
	br.set_response(response)

	#Get lecture, tutorial and assignment file names
	soup2 = BeautifulSoup(br.response().read(),"html.parser")
	fileName = []
	def getFileList(types,fileName):
		soup2 = soup.find('div', {"id" : types})
		for div in soup2.findAll("form"):
			name = div.find("input", {"name" : "file_name"})
			if(name == None):
				continue
			fileName.append(name['value'])
		return len(fileName)

	noteSize = getFileList("notes", fileName)
	tutSize = getFileList("tutorial", fileName)
	assignmentSize = getFileList("assignment", fileName)

	print "Checking files to download for " + subject
	count = 0
	#Handles download
	for forms in br.forms():
		if forms.attrs.get('action') == "https://mmls.mmu.edu.my/form-download-content":
			if count == len(fileName):
				break
			if count < noteSize:
				directory = "Lecture notes/"
			elif count < tutSize:
				directory = "Tutorial and labs/"
			else:
				directory = ""
			filename = fileName[count]
			fpath = str(subject+"/"+directory+filename)
			if os.path.isfile(fpath) == False:
				print "...Downloading " + filename
				br.form = forms
				br.method = "POST"
				response = br.submit()
				open(fpath, 'wb').write(response.read())
				response = br.open(fastDLLink+subjects[subject])
				soup = BeautifulSoup(br.response().read(),"html.parser")

				#To avoid Parsing error: OPTION outside of select 
				for div in soup.findAll('select'):
				    div.extract()

				for div in soup.findAll('script'):
				    div.extract()

				response.set_data(str(soup))
				br.set_response(response)
			count += 1

print "Updated."
raw_input('Press <ENTER> to continue')
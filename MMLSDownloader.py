import mechanize
from bs4 import BeautifulSoup
import getpass, os

br = mechanize.Browser()
mechanize.HTTPSHandler()
print "\tMMLS - Downloads your lecture and tutorial notes~\n"

#HANDLES LOGIN
while True:
	response = br.open("http://mmls.mmu.edu.my/")
	br.select_form(nr=0)         
	br.form["stud_id"] = raw_input("Student ID : ")
	br.form["stud_pswrd"] = getpass.getpass("MMLS Password (Password will be hidden): ")
	br.method = "POST"
	response = br.submit()

	soup = BeautifulSoup(br.response().read(), "html.parser")
	if soup.find("div", {"id" : "alert"}) == None:
		break
	else:
		print "Wrong username/password"


#Get subject name and code and store them in a list
soup = soup.find("div", {"class": "list-group "})
subjects = {}
subjectCode = []
skipSecond = True #To filter the repetition

for subject in soup.find_all('a'):
	if skipSecond:
		subjects[subject.string] = subject.get('href').split('/')[-1]
		skipSecond = False
	else:
		skipSecond = True

#Prints subject names and creates each respective directory if not created
print "Subjects you are taking this semester"
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
formAction = ["https://mmls.mmu.edu.my/download-note-all","https://mmls.mmu.edu.my/download-tutorial-all"]
identifier = ["[Lecture] ","[Tutorial] "]
subjIndex = 0

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

	#Get lecture and tutorial file names
	soup2 = BeautifulSoup(br.response().read(),"html.parser")
	soup2 = soup.find('div', {"id" : "notes"})
	fileName = []
	for div in soup2.findAll("form"):
		name = div.find("input", {"name" : "file_name"})
		if(name == None):
			continue
		fileName.append(name['value'])

	noteSize = len(fileName)
	soup2 = soup.find('div', {"id" : "tutorial"})
	for div in soup2.findAll("form"):
		name = div.find("input", {"name" : "file_name"})
		if(name == None):
			continue
		fileName.append(name['value'])

	print "Checking files to download for " + subject
	count = 0
	#Handles download
	for forms in br.forms():
		if forms.attrs.get('action') == "https://mmls.mmu.edu.my/form-download-content":
			if count == len(fileName):
				break
			if count < noteSize:
				directory = "Lecture notes/"
			else:
				directory = "Tutorial and labs/"
			filename = fileName[count]
			fpath = str(subject+"/"+directory+filename)
			if os.path.isfile(fpath) == False:
				print "..Downloading " + filename
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
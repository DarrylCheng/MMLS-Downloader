import mechanize
from bs4 import BeautifulSoup
import getpass

br = mechanize.Browser()
mechanize.HTTPSHandler()

print "\tMMLS - Downloads your lecture and tutorial notes~\n"
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

soup = soup.find("div", {"class": "list-group "})

subjects = {}
subjectCode = []
skipSecond = True
for subject in soup.find_all('a'):
	if skipSecond:
		subjects[subject.string] = subject.get('href').split('/')[-1]
		skipSecond = False
	else:
		skipSecond = True

print "Subjects you are taking this semester"
for subjName in subjects:
	print "\t"+subjName
print

fastDLLink = "https://mmls.mmu.edu.my/fast-download:"
formAction = ["https://mmls.mmu.edu.my/download-note-all","https://mmls.mmu.edu.my/download-tutorial-all"]
identifier = ["[Lecture] ","[Tutorial] "]
i = 0
index = 0
for subject in subjects:
	for actions in formAction:
		response = br.open(fastDLLink+subjects[subject])
		soup = BeautifulSoup(br.response().read(),"html.parser")

		#To avoid Parsing error: OPTION outside of select 
		for div in soup.findAll('select'):
		    div.extract()

		for div in soup.findAll('script'):
		    div.extract()

		response.set_data(str(soup))
		br.set_response(response)

		for form in br.forms():
		    if form.attrs.get('action') == actions:
		        br.form = form #select_form
		        break

		br.method = "POST"
		response = br.submit()
		if i==0:
			print "Downloading notes for " + subject
		filename = identifier[i]+subject+'.zip'
		open(str(filename), 'wb').write(response.read())
		i = (i+1)%2
	index += 1
print "Completed"
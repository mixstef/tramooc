import os, json, subprocess, time, zipfile, csv, os.path, sys

#Automatically monitors each contributor scores and suggests to forgive untrusted contributors based on statistics
#It creates a report with 'job_id,trusted and clean jud,flagged jud,untrusted jud,failed contrib. total,failed contrib. in work mode,failed contrib. in quiz mode,flagged contrib'

def download_report(report_type, job_id, api_key):
	#request a regeneration of the contributors report
	proc = subprocess.Popen(['curl -X POST "https://api.crowdflower.com/v1/jobs/'+job_id+'/regenerate?type='+report_type+'&key=' + api_key + '"'], stdout=subprocess.PIPE, shell=True)
	(out, err) = proc.communicate()

	time.sleep(1)

	#wait until the report is generated
	response = "202"
	while response != "302":
		proc = subprocess.Popen(['curl -s -o /dev/null -w "%{http_code}" "https://api.crowdflower.com/v1/jobs/'+job_id+'.csv?type=json&key=' + api_key +'"'], stdout=subprocess.PIPE, shell=True)
		(response, err) = proc.communicate()
		time.sleep(5)

	time.sleep(1)	
	
	#download the contributors report in zipped format
	proc = subprocess.Popen(['curl -o "'+job_id+'" -L "https://api.crowdflower.com/v1/jobs/'+job_id+'.csv?type='+report_type+'&key=' + api_key +'"'], stdout=subprocess.PIPE, shell=True)
	(out, err) = proc.communicate()

	#wait until the report is downloaded locally
	while not os.path.exists(job_id):
    		time.sleep(5)

	time.sleep(2)

	#read the report file inside the downloaded zip file
	report = ""
	try:
    		archive = zipfile.ZipFile(job_id, 'r')
		if(report_type == 'workset'):
			report = archive.read('workset'+job_id+'.csv').strip()
		else:
			report = archive.read('f'+job_id+'.csv').strip()
	except:
	 	print "couldn't read " + job_id + " report"
		return "error"
	return report

job_ids = []
if sys.argv[1] == "all":
	job_id_test = {}
	for pair in sys.argv[2:]:
		pairSplit = pair.split("-")
		job_id_test[pairSplit[0]] = pairSplit[1].split(",")
	wiki_job_ids = []
	#wiki_job_ids = ['987770','987763','987758','987741','987738','987586','987583','987551','987547','987537','987528']
	tran_job_ids = ['1002454','986070','986069','986067','986066','986064','986063','986062','986060','986057','986056','986049','986047','986045','986040','986036','986030','986025','985919','985918','984580','984574']

	job_ids = wiki_job_ids + tran_job_ids
elif sys.argv[1] == "specific":
	job_id_test = {}
	for pair in sys.argv[2:]:
		pairSplit = pair.split("-")
		if(len(pairSplit) == 2):
			job_id_test[pairSplit[0]] = pairSplit[1].split(",")
			job_ids.append(pairSplit[0])
		else:
			job_ids.append(pairSplit[0])
else:
	print "wrong parameters"
	sys.exit(1)
	
#your api key
api_key = '<your api key>'

full_report = 'full'
contributors_report = 'workset'

#url to get the job's settings
job_info_url = "https://api.crowdflower.com/v1/jobs/%s.json?key=" + api_key 

#csv file with the contributors id which can be forgiven
ofile_forgive = open("forgive.csv","w")
ofile_forgive.write("job_id,worker_id,reason,accuracy\n")

#csv file with the job statistics
ofile = open("reports.csv","w")
ofile.write("job_id,trusted and clean jud,flagged jud,untrusted jud,failed contrib. total,failed contrib. in work mode,failed contrib. in quiz mode,flagged contrib.\n")

for job_id in job_ids:
	print job_id		
	#get job settings to find the given accuracy threshold
	url = job_info_url % (job_id)
	proc = subprocess.Popen(["curl " + url], stdout=subprocess.PIPE, shell=True)
	(out, err) = proc.communicate()
	j_d = json.loads(out)
	#get the jobs accuracy threshold in [0,1]
	percentage = float(j_d["options"]["reject_at"])/100.0
	
	report = download_report("workset",job_id,api_key)
	if(report == "error"):
		continue
	#store in a list every row of the report
	reportSplit = report.split("\n")
	
	#statistics about the judgments and the contributors
	trusted_jud = 0
	untrusted_jud = 0
	false_jub = 0
	trusted_contrib = 0
	untrusted_quiz = 0
	untrusted_work = 0
	flagged_contrib = 0

	i = 0
	contrib_jud_dict = {}
	for line in reportSplit:
		for row in csv.reader([line]):
			#the first row is the header, skip it
			if i == 0:
				i += 1
				continue
			contr_id = row[0]
			total_jud = int(row[2])
			golden_jud = int(row[4])
			missed_golden = int(row[3])
			flagged = row[11]
			trust = float(row[15])
			#if the contributor is flagged
			if(flagged != ""):
				flagged_contrib += 1
				false_jub += (total_jud-golden_jud)
			#if the contributor is untrusted
			elif(trust < percentage):
				untrusted_jud += (total_jud-golden_jud)
				#if there are less or equal to the rows per page test questions we are in the quiz mode
				if(golden_jud <= int(j_d["units_per_assignment"])):
					untrusted_quiz += 1
				else:
					untrusted_work += 1
					#if the contributor is untrusted with just 10% below the threshold, store his id and the number of judgments he made in a dict
					if(trust < percentage and trust > percentage-0.1):
						contrib_jud_dict[contr_id] = (total_jud-golden_jud)
			#if the contributor is trusted
			else:
				trusted_jud += (total_jud-golden_jud)
				trusted_contrib += 1
		i += 1
	#If there are trusted contributors, calculate their average number of trusted judgments
	if(trusted_contrib > 0):
		meanJud = trusted_jud/trusted_contrib
	
		#Every stored contributor with number of judgments higher than the average trusted judgments should be checked for forgiveness
		for contrib in contrib_jud_dict.keys():
			if contrib_jud_dict[contrib] >= meanJud:
				print contrib
				ofile_forgive.write(job_id+","+contrib+"\n")

	ofile.write(str(job_id)+","+str(trusted_jud)+","+str(false_jub)+","+str(untrusted_jud)+","+str(untrusted_work+untrusted_quiz)+","+str(untrusted_work)+","+str(untrusted_quiz)+","+str(flagged_contrib)+"\n")
ofile.close()



if len(job_id_test) > 0:
	for job_id in job_id_test:
		report = download_report("full",job_id,api_key)
		if(report == "error"):
			continue
		#store in a list every row of the report
		reportSplit = report.split("\n")
		i = 0
		for line in reportSplit:
			for row in csv.reader([line]):
				#the first row is the header, skip it
				if i == 0:
					i += 1
					continue
				if len(row) <= 0:
					continue
				if row[0] in job_id_test[job_id]:
					ofile_forgive.write(job_id+","+row[9]+",bad_test,"+row[8]+","+row[4]+"\n")
ofile_forgive.close()
					

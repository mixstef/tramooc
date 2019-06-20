import csv,sys
import collections, random

#creates a report of "id","source","translated","Question 3 (grammar)","Question 4 (meaning)" 

def findError(first):
	error = ""
	if(("meaning" in first or "omission" in first or "addition" in first) and ("spelling" not in first and "grammar" not in first and "typo" not in first and "transliteration" not in first)):
		error = "meaning"
	elif(("meaning" in first or "omission" in first or "addition" in first) and ("spelling" in first or "grammar" in first or "typo" in first or "transliteration")):
		error = "correct"
	elif("punctuation" in first or "mistranslat" in first or "mistranlat" in first or "transliteration" in first  or "typo" in first  or "currecy" in first   or "numbers" in first ):
		error = "correct"
	else:
		error = "grammar"
	return error
	

f = open(sys.argv[1], 'rb')
o = open("out_"+sys.argv[1], "w")
writer = csv.writer(o)
reader = csv.reader(f)
headers = reader.next()
a = ["id","source","translated","Question 3 (grammar)","Question 4 (meaning)"]
i = 1	
writer.writerow(a)
for row in reader:
	first = ""
	second = ""
	if(row[2] in ["24","25","37","38","39","40","47","63","69","84","87","89"]):
		continue
	if(len(row[11].split("/")) > 2 or len(row[11].split(" or ")) > 2 or len(row[11].split(" and ")) > 2 or "lower" in row[11]  or "upper" in row[11]):
		first = "correct"
		second = "correct"
	else:
		if("/" in row[11]):
			rowSplit = row[11].split("/")
			first = rowSplit[0]
			second = rowSplit[1]
		elif(" or " in row[11]):
			rowSplit = row[11].split(" or ")
			first = rowSplit[0]
			second = rowSplit[1]
		else:
			first = row[11] 
			second = row[11]
		
		first = findError(first)
		second = findError(second)
		
	choice = random.choice([True, False])
	
	if(choice):
		if(first == "correct"):
			a = [str(i),row[6],row[7],"correct","correct"]
		elif(first == "meaning"):
			a = [str(i),row[6],row[8],"correct","meaning"]
		elif(first == "grammar"):
			a = [str(i),row[6],row[8],"grammar","correct"]	
	else:
		if(second == "correct"):
			a = [str(i),row[6],row[7],"correct","correct"]
		elif(second == "meaning"):
			a = [str(i),row[6],row[9],"correct","meaning"]
		elif(second == "grammar"):
			a = [str(i),row[6],row[9],"grammar","correct"]	
	i += 1		
	#a = [row[2],row[6],row[7],row[8],row[9],row[11],first,second]
    	writer.writerow(a)	
#o.write(row[2]+",'"+row[6]+"',"+row[7]+"','"+row[8]+"',"+first+",'"+row[9]+"',"+second+','+row[11]+"'\n")

writer.writerow(["89","My genotype is exactly what alleles I have,  the versions of the gene."])
writer.writerow(["90","What is the course's aim?"])
writer.writerow(["91","This is sine qua non."])
writer.writerow(["92","None explains succinctly what he wants."])
writer.writerow(["93","In the meantime, the algorithm was wrong."])
writer.writerow(["94","The usual medication stopped working."])
writer.writerow(["95","I should give them a little bit of justice."])
writer.writerow(["96","The library was built using local materials and labour."])
writer.writerow(["97","This raises a very interesting question."])
writer.writerow(["98","And you know who likes carbon monoxide?"])
writer.writerow(["99","And this company right here has 500,000 shares."])
writer.writerow(["100","The next step is to set the initial position and velocity of the particle."])

o.close()
f.close()

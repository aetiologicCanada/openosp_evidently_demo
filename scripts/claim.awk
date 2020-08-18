# see Chapter 2 for record layouts.
BEGIN{

system("mkdir -p "output_directory)
}

# need a function to extract basename from filepath
# this exercise in parsimony works fine
function basename(file) {
    sub(".*/", "", file)
    return file
}

{

#some vars.  
rec_code = substr($0,1,3)
first_letter = substr(rec_code,1,1)
first_two = substr(rec_code,1,2)

# This gets the data centre name for the output file. 

if(index(FILENAME, "html")|| index(FILENAME, "HTML")) NEXTFILE

if(FNR ==1) data_centre = substr($0,4,5)
if(FNR ==1) close(outputfile)
if(FNR ==1) outputfile = output_directory data_centre "_" basename(FILENAME)

#C02
#removes 26-35 PHN
# remvoes 36-39 ?
# removes 40-41 Dependent $
# removes 67-82 ICD9x3
# substitutes static birthdate col 132-141
#  then takes another 140 bytes from 151 to 291
# it excludes all the oin data elements

if(rec_code =="C02")
    record = (substr($0,1,25)"----------____--"substr($0,42, 34 )"---------------"substr($0,92,39)"19991231"substr($0,140));
  else record=""
  
print record > outputfile
}

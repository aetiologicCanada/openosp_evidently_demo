# this awk file parses the remittance advice file, using v 4.4 of the Teleplan guide
# see Chapter 2 for record layouts.

system("mkdir  -p /tmp/evidently_data")

# need a function to extract basename from filepath
# this exercise in parsimony works fine
function basename(file) {
    sub(".*/", "", file)
    return file
  }

#some vars.  
rec_code = substr($0,1,3) {}

{

# This gets the data centre name for the output file. 

if(NR ==1) data_centre = substr($0,4,5)
# now we parse the various input record types
#print(data_centre > clinic_id)


#S01

if(rec_code =="C02") 
     record = substr($0,1,25)"----------____--"substr($0,42, 34 )"---------------"substr($0,92)

}

outputfile = "/tmp/evidently_data/intermediate/"data_centre"_"basename(FILENAME){}
{print record > outputfile}






# this awk file parses the remittance advice file, using v 4.4 of the Teleplan guide
# see Chapter 3 for record layouts.
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
first_letter = substr($0,1,1)
first_two = substr($0,1,2)

# This gets the data centre name for the output file. 

if(FNR ==1) data_centre = substr($0,4,5)
#if(FNR ==1) outputfile = /dev/null
if(FNR ==1) close(outputfile)
if(FNR ==1) outputfile = output_directory "/" data_centre "_" basename(FILENAME)

#close outputfile
# now we parse the various input record types
#print(data_centre > clinic_id)

if(index(first_letter,"V") || index(first_letter, "M")  || index(rec_code, "C12")  || index(first_two, "S2")   || index(first_letter, "#") ) record = $0;

#S01

else if(index(rec_code, "S01")) 
     record = substr($0,1,127) "--------" substr($0,136);

# S00 S02 S03 mods

# removed #TI for testing
else if (index(rec_code, "S03")|| index(rec_code, "S02") || index(rec_code, "S00") ||index(rec_code, "#TI")) record = substr($0,1,48) "AAabcdefghijklmnopqr00aaaaaaaaaa" substr($0,81,228);
                  

# S04 mods

else if(index(rec_code, "S04")) 
      record = substr($0,1,69) "--------" substr($0,78);

else record = "";
}
{

print record > outputfile
if(EOF) close(outputfile)
}

# Looks this is going to be a 5 line shell script
# parse the remittance files using remittance_awk.awk
# parse the claims files claims_awk.awk
# generate a compressed tar ball if(EOF) {system("tar -cvzf "remittance_directory/output/data_centre"* remittance_directory/output/"datacentre".tar.gz")
# encrypt tar.gz with public key

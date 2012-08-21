'''
Created on Aug 21, 2012

@author: kandrus
trans-id unit test
This python script reads in a series a notification files
that are generated from the consoleone.exe and searches the
files for duplicates. If there are duplicates, the user is 
notified and the duplicate is shown
'''
import os 
import re 

def trans_id_match(not_log_dir):
    '''This method takes the location of notification files as an argument,
    parses out any trans-id's and spit out a list of trans-ids that are duplicates
    Returns a dictionary containing the trans-id as the key, the number of duplicates 
    and the location of the duplicate'''
    
    #Populate the not_files list with the absolute paths of all the notification files
    #in the directory
    not_files = []
    for not_file in os.listdir(not_log_dir):
        not_files.append(os.path.join(not_log_dir, not_file))

    #Will contain the transaction IDs along with the notification file they originated from
    trans_ids = {}
    #Dictionary to keep track of the number of duplicates for a given transaction id
    duplicate_count = {}

    for not_file in not_files:
        FILE = open(not_file, 'rb')
        file_data = FILE.read()
        temp_id_matches = re.findall(r'\S+TransID:([0-9A-Fa-f]+-[0-9A-Fa-f]+-[0-9A-Fa-f]+-[0-9A-Fa-f]+-[0-9A-Fa-f]+)', file_data)
        
                #Assign the notification file that the t-id comes from to the trans_ids dict for matching later if a duplicate is found
        for match in temp_id_matches:
            if not trans_ids.has_key(match):
                trans_ids[match] = not_file
                duplicate_count[match] = 0
            if duplicate_count[match] >= 0:
                duplicate_count[match] +=1
                trans_ids[match + " duplicate-" + str(duplicate_count[match]) ] = not_file 
        
    #Outputs to the user the Transaction ID of a duplicate transaction as well as the 
    #number of duplicates and the location of the Transaction ID in the notification file
    #If the log generator is functioning properly, you should see nothing from the code below
    duplicate_dict = {}
    print "Transaction IDS:"
    count = 0
    for t_id in trans_ids:
        if not 'duplicate' in t_id and duplicate_count[t_id] > 2:
            print "%d duplicate(s) for %s, located in %s" %(duplicate_count[t_id] -2, t_id, trans_ids[t_id])
            duplicate_dict[t_id] = [duplicate_count[t_id], trans_ids[t_id]]
            count +=1
    if count == 0:
        print "No Duplicate ID's found. Success!"
    del count
    return duplicate_dict
            
trans_id_match(r'C:\Log\Processor-KylesPyMatchTest\Notification')

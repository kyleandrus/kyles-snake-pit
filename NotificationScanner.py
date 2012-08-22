'''
Created on Aug 21, 2012

@author: kandrus
trans-id unit test
This python script reads in a series a notification files
that are generated from the consoleone.exe and searches the
files for duplicates. If there are duplicates, the user is 
notified, the duplicate is shown, and a log file is generated
in the same directory as the notification logs
'''
import os 
import re 
import sys
import logging
import time

def trans_id_match(not_log_dir):
    '''This method takes the location of notification files as an argument,
    parses out any trans-id's and spit out a list of trans-ids that are duplicates
    Returns a dictionary containing the trans-id as the key, the number of duplicates 
    and the location of the duplicate'''
    
    #Set logger variables etc...
    logger = logging.getLogger('NotificationScanner')
    hdlr = logging.FileHandler(os.path.join(not_log_dir, "Scanner_Results.log"))
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.DEBUG)

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
        FILE.close()
    #Outputs to the user and the log file the Transaction ID of a duplicate transaction as well as the 
    #number of duplicates and the location of the Transaction ID in the notification file
    duplicate_dict = {}
    print "Transaction IDS:"
    count = 0   
    for t_id in trans_ids:
        if not 'duplicate' in t_id and duplicate_count[t_id] > 2:
            duplicate_string = "%d duplicate(s) for %s, located in %s" %(duplicate_count[t_id] -2, t_id, trans_ids[t_id])
            print duplicate_string
            logger.error(duplicate_string)
            duplicate_dict[t_id] = [duplicate_count[t_id], trans_ids[t_id]]
            count +=1
    if count == 0:
        success_string = "No Duplicate ID(s) found, Success!"
        print success_string
        print len(trans_ids), ' unique Transaction ID(s)'
        logger.info(success_string)
    del count
#    FILE.close()
    return duplicate_dict
            
trans_id_match(r'C:\Log\Processor-KylesPyMatchTest\Notification')


def main():
    '''This function is used to call the rest of the methods from the command line'''
        
    # Make a list of command line arguments, omitting the [0] element which is the script itself.
    args = sys.argv[1:]
    
    #If no argruments are given, print proper usage and call the search method
    if not args:
        print "\nProper usage: \n\t[NotificationScanner.py \"c:\Log\AppName\Notifications\"]"
    
    #Default values passed to the method when called through a command line argument
    not_log_dir = ''
    if len(args) == 0:
        print "\n\nYou must use a directory to proceed!"
    elif args[0] != '':
        not_log_dir = args[0]
        trans_id_match(not_log_dir)
        del args[0:0]
        
##uncomment to run the main method from the console        
if __name__ == "__main__":
    '''If the scripts initiates itself, run the main method
    this prevent the main from being called if this module is 
    imported into another script'''
    main()


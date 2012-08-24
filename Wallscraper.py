'''
Created on Aug 1, 2012

@author: kandrus
The purpose of this script is to allow a user to automatically download
all wallpapers that match a user specified query, or wallpapers that are 
contained within their custom favorites collections from the website http://wallbase.cc
The downloading of favorites, or nsfw images is restricted to registered users.
'''

import os 
from time import sleep
import re 
import sys 
import urllib 
import urllib2
import cookielib
import ConfigParser
import shutil

#Installing the CookieJar - This will make the urlopener bound to the CookieJar.
#This way, any urls that are opened will handle cookies appropriately 
#Has to be at a global level so I can save the cookie from different methods
#There's probably a cleaner way to do this.
COOKIEFILE = 'cookies.lwp'
urlopen = urllib2.urlopen
Request = urllib2.Request
cj = cookielib.LWPCookieJar()
cj.save(COOKIEFILE)
if cj is not None:
    if os.path.isfile(COOKIEFILE):
        
        #If there is already a cookoie file, load from it
        cj.load(COOKIEFILE)
    if cookielib is not None:
        
        #This installs the cookie Jar into the opener for fetching URLs
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)

#Global dictionary used to store the name of a wallpaper file
#as well as the url of that file. Global so that it can be accessed
#by any methods in the script.
img_names_dict = {}
#Used in multiple methods for purity list checks
purity_list = ('NSFW','SKETCHY', 'SFW')
purity_bits = ('001', '011', '111')

def dir_check(directory):
    '''This method checks whether a directory exists or not, if it doesn't, it creates it for you'''
    
    #Essentially do nothing if the path exists
    if os.path.exists(os.path.abspath(directory)):
        return directory
    else: #create the path for the user and tell the user the name of the path
        print '%s | didn\'t exist, creating...' %(os.path.abspath(directory))
        os.makedirs(os.path.join(directory))
def search_config(dest_dir, search_query, query_name = '', new_ini = False):

    query_name = search_query['query_name']
    #Removes any spaces or non alnum characters from the directory and creates the directory
    #(Windows doesn't like special characters or spaces in directory names)
    if query_name.isalnum() == False:
        new_query_dir = ''.join(e for e in query_name if e.isalnum())
        dir_check(os.path.join(dest_dir, new_query_dir))   
        dest_dir = os.path.join(dest_dir, new_query_dir)
        query_file = new_query_dir + '.ini'
    else:
        dir_check(os.path.join(dest_dir, query_name)) 
        dest_dir = os.path.join(dest_dir, query_name)
        query_file = query_name + '.ini'

    #Populate a list with the names of files and directories in the dest_dir
    list_files = os.listdir(dest_dir)
    
    #Delete the ini file before creating a new one 
    if query_file in list_files and new_ini == True:
        print os.path.join(dest_dir, query_file), " deleted!"
        os.unlink(os.path.join(dest_dir, query_file))
        
    #instantiate c as a configparser class
    c = ConfigParser.ConfigParser()

    #Code to read the configuration file and set variables to match what's in the config
    #Check if an ini file exists in the dest_dir, if yes, ask to load the config and re-do the search
    if query_file in list_files and new_ini == False:
        print 'Loading settings from %s' %(query_file)
        FILE = open(os.path.abspath(os.path.join(dest_dir, query_file)), "rb")
        c.readfp(FILE)
        print '#'*40 + '\nQuery file contents\n' + '#' *40
        for section in c.sections():
            print section
#            query_name = section
            for option in c.options(section):
                search_query[option] = c.get(section, option)
                print "\t", option, "=", c.get(section, option)
        print '#'*40
        #Return the variables set from the config file to the dl_search method
        FILE.close()   
        return search_query, dest_dir, c.get("Search Query", 'dl_to_diff_folders')
        
    #use this code to create the file if it doesn't already exist
    if dest_dir not in list_files and new_ini == True:
        c.add_section("Search Query")
        count = 0
        for each in search_query:
            #print each, search_query[each], 
            c.set("Search Query", each, search_query[each])
            count += 1
        FILE = open(os.path.abspath(os.path.join(dest_dir, query_file)), "w")
        c.write(FILE)
        print "Config file stored at:\n", os.path.abspath(os.path.join(dest_dir, query_file))
        FILE.close()   
        return search_query, dest_dir, c.get("Search Query", 'dl_to_diff_folders')
def search_options(dest_dir, query = '' ):
    '''
    This method populates a urllib encoded data stream used in the request of search URLs.
    usage: 
    '''
    ###############################################################################################################
    #default search values not yet implemented into the user prompts they are however 
    #needed for the query, so they're set to wildcards on the server side
    query = ''
    nsfw = '110'
    aspect = '0'
    orderby = 'date'
    start_range = 0
    max_range = 2000
    board = '0' 
    res='0' 
    res_opt='0' 
    orderby_opt='0'
    thpp='32'
    section= 'wallpapers'
    dl_to_diff_folders = 'False'
    search_query = ({'query': query, 'board': board, 'nsfw': nsfw, 'res': res, 'res_opt': res_opt, 'aspect':aspect, 
                       'orderby':orderby, 'orderby_opt': orderby_opt, 'thpp':thpp, 'section': section, '1': 1,
                        'start_range' : start_range, 'max_range' : max_range, 'query_name': query, 'dl_to_diff_folders' : dl_to_diff_folders})
    ###############################################################################################################
    
    
    #The following are user prompts, used if they want to change the defaults to something more specific
    print "+" * 80 + '\n' + "#" * 80 + "\nIn the next series of questions, please choose the search options"\
    " you would like\n to use.In all cases, leaving the field blank and pressing enter will use the \ndefault "\
    "value of 'all'\n" + "#" * 80 + '\n' + "+" * 80 + '\n'
    if query != '' :
        print "+" * 80 + '\n' + "Pre-selected query detected\nYou are searching for:", query, "\n" + "+" * 80 +'\n'
    if not query:
        print "#" * 80 + '\n' + "What are you searching for?\nCan be 'tag:XXXX', or \"Kate Beckinsale\", "\
        "or blank for 'new' wallpapersetc...\nUse \"\" to make the search specific, otherwise any words in"\
        " the query will match\n" + "#" * 80 
        search_query['query'] = raw_input()
        
        #change this down the line to make tag searches a different folder 
        search_query['query_name'] = search_query['query']
        #Error to switch return query if a type error is encountered
        type_error = False
        
        if search_query['query'] =='':
            print 'Non-keyword query detected!\nPlease choose how you want to sort the query below'
            search_query['query'] = ' '
            search_query['query_name'] = 'Non-Keyword Query'
        if search_query['query'] != '':
            print 'Would you like to search for a configuration file? (y or n)'
            config_choice = raw_input()
            if config_choice == 'y':
                try:
                    search_query, dest_dir, dl_to_diff_folders = search_config(dest_dir, search_query, search_query['query_name'])
                    #################################################################################################################
                    #NSFW check if the call to config was successfull
                    #S really move the NSFW check to the wallbase auth method
                    #################################################################################################################
                    if search_query['nsfw'] == '001' or search_query['nsfw'] == '011' or search_query['nsfw'] == '101' or search_query['nsfw'] == '111':
                        print "+" * 25 + 'Login required for nsfw images' + "+" *25 + '\nPlease enter your username:'
                        user = raw_input()
                        print 'Please enter your password:'
                        passw = raw_input()
                        wallbase_auth(user, passw)
                        #############################################################################################################
                except TypeError:
                    type_error = True
                    print "Search ini not found!\nPlease complete the following questions to create a new query"
                    search_config(dest_dir, search_query, search_query['query_name'], True)
                if type_error == False:
                    return urllib.urlencode(search_query), search_query['start_range'], search_query['max_range'], dest_dir, dl_to_diff_folders
                    
                
            if config_choice =='n' or config_choice == '' or type_error == True:
                print "#" *80 + "\nWhat purity setting do you want to use? (default is 110)\nFirst bit allows SFW images, "\
                "second bit allows Sketchy images, third bit allows\nNSFW images e.g. if you want to see only Sketchy and"\
                "NSFW you will input 011.\nIf you want only SFW images 100\n" + "#" * 80
                search_query['nsfw'] = raw_input()
                if search_query['nsfw'] == '':
                    search_query['nsfw'] = '110'
                if search_query['nsfw'] == '001' or search_query['nsfw'] == '011' or search_query['nsfw'] == '101' or search_query['nsfw'] == '111':
                    print "+" * 25 + 'Login required for nsfw images' + "+" *25 + '\nPlease enter your username:'
                    user = raw_input()
                    print 'Please enter your password:'
                    passw = raw_input()
                    wallbase_auth(user, passw)
                print "#" * 80 + "\nWould you like to keep your folder organized by purity??\nAccepted values are True or False (leave blank for False).\n" + "#" * 80
                search_query['dl_to_diff_folders'] = raw_input()
                if search_query['dl_to_diff_folders'] =='':
                    search_query['dl_to_diff_folders'] = 'False'
                print "#" * 80 + "\nWhich Aspect Ratio do you want to filter by?\nAccepted values are 'blank' => All | 1.33 => 4:3 |"\
                " 1.25 => 5:4 | 1.77 => 16:9 |\n1.60 => 16:10 | 1.70 => Netbook | 2.50 => Dual | 3.20 => Dual Wide | 0.99 => "\
                "Port.\n" + "#" * 80
                search_query['aspect'] = raw_input()
                if search_query['aspect'] =='':
                    search_query['aspect'] = '0'
                print "#" * 80 + '\nHow do you want your wallpapers ordered? Input one of the following to choose:\ndate, views, favs,'\
                ' relevance (default = date)\n' + "#" * 80
                search_query['orderby'] = raw_input()
                if search_query['orderby']  == '':
                    search_query['orderby']  = 'date'
                print "#" * 80 + '\n' + "Please specify a start range of wallpers to download:\nTypically this is 0, default is 0"\
                "\nYou can use this to pick up where you left off if you stopped dl's previously\n"+ "#" * 80
                search_query['start_range'] = raw_input()
                if search_query['start_range'] =='':
                    search_query['start_range'] = 0
                print "#" * 80 + '\n' + "Please specify an end range of wallpers to download:\ndefault is 2000\n"+ "#" * 80
                search_query['max_range'] = raw_input()
                if search_query['max_range'] =='':
                    search_query['max_range'] = 2000
                    
                #Populate the search_query with values input by the user as well as the default ones
                search_query, dest_dir, dl_to_diff_folders = search_config(dest_dir, search_query, search_query['query'], True)
                
                
                #Return the encoded search string for requests, the actual query string, and the range of the search
                return urllib.urlencode(search_query), search_query['start_range'], search_query['max_range'], dest_dir, dl_to_diff_folders
def download_walls(dest_dir = '.', search_query='', url = '', start_range = 0, max_range = 2000, dl_to_diff_folders = "False"):
    """
    This method initiates the downloads the html matches urls, and uses a counter and range to limit the downloads
    """

    #check if the directory exists or not
    dir_check(dest_dir)
    print 'Files being saved to:\n', os.path.abspath(dest_dir) 
    
    #Uses the start number and max number to limit the amount of wallpapers you download
    while start_range <= max_range: 
    
        #Used as a placeholder for the url so we can reset it after the loop
        temp_url = url
        
        #Modify the url to retrieve the current range of wallpapers
        url = url + '/' + str(start_range)
        
        #verbose, verification to the user of which page they're on. not needed
        print "We are looking for wallpapers in the url:\n",  url
        
        #Begin matching imgs in the html and pull the start number out of the resultant matches
        start_range = match_imgs(url, dest_dir, search_query, start_range, max_range, dl_to_diff_folders)
        
        #reset the url since the match is completed
        url = temp_url
        
        #Call to method used to actually download the images from the match
        #Uses dictionary of names:sources
        print "Deploying ninjas to steal wallpapers"
        get_imgs(img_names_dict, start_range, dest_dir)
    
    if start_range >= max_range: #Stop downloads if max range is reached
        print 'Max range reached, stopping downloads'
        sys.exit(1)
def match_imgs(url, dest_dir, search_query, start_range, max_range, dl_to_diff_folders = "False"):

    #url requests need values passed, when downloading favorites they're not necessary
    #so we send blank vals along with the reqeusts
    blank_vals = {}
    blank_data = urllib.urlencode(blank_vals)
    search_headers = {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'referer': 'wallbase.cc/search'}
    search_req = urllib2.Request(url, search_query, search_headers)
    
    #Initial html request, in a while loop in case of http errors
    while True:
        try:
            search_url = urllib2.urlopen(search_req)
        except urllib2.HTTPError as detail:
            print "%s error encountered\nWaiting to try again" %(detail)
            sleep(30)
            continue
        break
    
    #Populate an object with the source html
    url_html = search_url.read()
    
    #Uncomment if you wish to have an html file to verify your query is working properly
#    output_html_to_file(url_html, dest_dir)
    
    #Regular expression used to find valid wallpaper urls within the index.html
    matchs = re.findall(r'http://wallbase.cc/wallpaper/\d+', url_html)
    
    #regex that finds the number of search results, up to a billion
    active_walls = re.search(r'a\sactive"><span>(\d+),*(\d*),*(\d*)', url_html)
    
    #attempts to set the number of wallpapers to the regex results
    try:
        if active_walls.group(2) == '0' and active_walls.group(3) == '0':
            num_of_walls = active_walls.group(1)
        if active_walls.group(3) == '0' and active_walls.group(2) != '0':
            num_of_walls = active_walls.group(1) + active_walls.group(2)
        else: 
            num_of_walls = active_walls.group(1) + active_walls.group(2) + active_walls.group(3)
    except AttributeError:
        try:
            active_walls = re.search(r'count\s\S\s(\d+)', url_html)
            num_of_walls = active_walls.group(1)
        except AttributeError:
            print 'number of wallpapers not found'
    
    #The number of wallpapers is used to limit the matches as well as determine start and stop ranges in this method
    print 'Currently processing matches'
    if int(num_of_walls) > max_range:
        print '%s wallpapers found\n%d queued for dl, out of %d' %(num_of_walls, max_range - start_range, max_range)
    elif (max_range > int(num_of_walls)) and (int(num_of_walls)-start_range) > 0:
        print 'Found %d wallpapers\nDownloading %d wallpapers' % (int(num_of_walls), int(num_of_walls)-start_range) 
    
    #For each img url, find the source url of that img in it's own html file
    for match in matchs:
    
        #while loop used stop matching once the max is reached
        while True and start_range < max_range:
        
            try: #and request the img src url, if http error, wait and try again
                sleep(.15)
            
                #request for src html of matched image
                img_src_req = urllib2.Request(match, blank_data, search_headers)
                img_src_open = urllib2.urlopen(img_src_req)
                img_src_html = img_src_open.read()
                
                #regex for locating the wallpapers img src url and appending the src and name to the dictionary
                img_match_src = re.search(r'http://[^www]\S+(wallpaper-*\d+\S+\w+)', img_src_html)

                #Added a regex to tag each wallpaper with it's purity setting
                #so that you can download the wallpaper to a different folder
                #if you wish.                
                if img_match_src:
                    if dl_to_diff_folders == 'True':
                        purity_match = re.search(r'class="[c|l]\sselected\s(\w+)', img_src_html)
                        img_names_dict[img_match_src.group(1)] = (img_match_src.group(0), purity_match.group(1))
                    else:
                        img_names_dict[img_match_src.group(1)] = img_match_src.group(0)
                    
                    #status of matches based on range or limits
                    if max_range < int(num_of_walls):
                        print "matched: ",  start_range +1 , '/', max_range
                    else:
                        print "matched: ", start_range +1, '/', int(num_of_walls)
                    
                    #increment start number that's then returned to the other method for counting
                    start_range +=1
                else:
                    print 'Error: No img_src\'s found. Make sure you logged in.'
            except urllib2.URLError as detail:
                print "%s error encounted\nWaiting to try again" %(detail)
                sleep(30)
                continue
            break
        
    #stop process if there are no more matches available
    if start_range >= 0 and len(img_names_dict) == 0: 
        print 'All wallpapers downloaded or already exist:\n"END OF LINE, TRON"'
        sys.exit()
    else: print len(img_names_dict), " Matches successfully made."
    
    #used for returning the proper number of matches if the number of matches is less than the thumbnails per page
    if len(img_names_dict) < 32:
        return (start_range + (32 - len(img_names_dict)))
    else:
        #start number returned that's used for incrementing elsewhere
        return start_range
def get_imgs(img_names_dict, start_range, dest_dir = ''):
    """This method is used to retrieve images from a dictionary of wallpapers and urls,
    saves them to your hard drive, and if they already exist skips the download."""

    #If the chosen directory doesn't exist, create it
    dir_check(dest_dir)
    
    #counters used to report back the number of successfull matches and downloads
    match_count = 0
    success_count = 0
    
    #The 32 below is because the thpp is set to 32, should make this dynamic
    #logic is such that if the passed in start number is less than 30, it downlaods the correct # of imgs
    if start_range < 32:
        start_range -=  start_range
    elif start_range >= 32:
        start_range -= 32
    
    #Iterate through the loop and download images in the lists
    for img in img_names_dict:
        
        #Setting the file name and directory in case of purity download filtering
        purity_dir = os.path.join(dest_dir, (img_names_dict[img])[1])
        purity_file = os.path.join(purity_dir, img)

        #Create purity directory if it's needed
        if img_names_dict[img][1] in purity_list:
            dir_check(purity_dir)            

            #else if image exists in purity directory, don't move it
            if os.path.isfile(purity_file):
                print "File %d, %s exists in %s folder, not moving" %(start_range +1, img, img_names_dict[img][1])
            #If image exists is in main directory, and dl to diff true, move image to purity folder
            elif os.path.isfile(os.path.join(dest_dir, img)):
                print "File %d, %s exists, moving to %s folder" %(start_range +1, img, img_names_dict[img][1])
                shutil.move(os.path.join(dest_dir, img), purity_dir)
            #else if image doesn't exist in purity direcotry, download that shit
            elif not os.path.isfile(purity_file):
                print 'File %d, %s downloading to %s folder' %(start_range +1, img, img_names_dict[img][1])
                urllib.urlretrieve(img_names_dict[img][0], purity_file)
                sleep(1)
                success_count += 1
        
        #Check whether the image already exists or not, if yes, skip download, if not, download it used when purity sorting is not enabled
        if img_names_dict[img][1] not in purity_list:
            if os.path.isfile(os.path.join(dest_dir, img))  :
                print 'File %d, %s exists in %s, not moved' % (start_range +1, img, os.path.basename(dest_dir))
            elif not os.path.isfile(os.path.join(dest_dir, img)):
                print 'File %d, %s downlaoding to %s folder' %(start_range +1, img, os.path.basename(dest_dir))
                urllib.urlretrieve(img_names_dict[img], os.path.join(dest_dir, img))
                sleep(1)
                success_count += 1
        start_range +=1
        match_count +=1
    if success_count:
        print success_count, 'successful downloads'

    #Image dictionary is cleaned up after each run and re-used for the next series of matches
    print "End of list! Flushing temporary urls..."
    img_names_dict.clear()
    return success_count
def output_html_to_file(url_html, dest_dir = '.'):
    
    #This code will output the html of the search page, needs fed a req.open()
    dir_check(dest_dir)
    filename = 'page.html'
    FILE = open(os.path.join(dest_dir,filename), "w")
    FILE.writelines(url_html)
    print "HTML file written to:\n", os.path.abspath(os.path.join(dest_dir, filename))
    FILE.close()   
def wallbase_auth(username, password):
    '''The following code takes user variables and logs you into wallbase.
    this allows you to download images from favorites, and NSFW images. 
    This method needs to be run every time you attempt to run a match against
    restricted pages on wallbase'''

    #Values passed to the cgi interface of the webserver to log the user in
    login_vals = {'usrname': username, 'pass': password, 'nopass_email': 'TypeInYourEmailAndPressEnter', 'nopass': '0', '1': '1'}
    login_url = 'http://wallbase.cc/user/login'
    login_data = urllib.urlencode(login_vals)
    http_headers =  {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'referer': 'http://wallbase.cc/start/'}   
    req = urllib2.Request(login_url, login_data, http_headers)
    
    #Accounting for firewall blocking me due to traffic and handling it
    while True:
        try:
            resp = urllib2.urlopen(req)
        except urllib2.HTTPError as detail:
            print "%s error encountered\nWaiting to try again" %(detail)
            sleep(30)
            continue
        break

    #Save cookie with login info
    cj.save(COOKIEFILE)
    print 'User %s logged in' %(username)
def dl_favorites(dest_dir = ''):
    '''Calls to this method download a category of favorites wallpapers from 
    a users wallbase account. The only argument it takes is a destination directory. 
    Once this directory is checked it downloads the images to a directory matching the 
    name of the category within the directory'''
   
    #Code to set variables for login and search functions
    #This is needed here becuase you can't download images from favorites without logging in
    #Should probably move this to a method of it's own to just return the fav_list_html file
    print "#" * 80 + '\n' + "+" * 26 + 'Login required to dl favorites' + "+" *24 + "\n" + "#" * 80 + '\n' + 'Please enter your username:'
    user = raw_input()
    print "Please enter your password:"
    passw = raw_input()
    wallbase_auth(user, passw)
    login_vals = {'usrname': user, 'pass': passw, 'nopass_email': 'TypeInYourEmailAndPressEnter', 'nopass': '0', '1': '1'}
    login_data = urllib.urlencode(login_vals)
    http_headers =  {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'referer': 'wallbase.cc http://wallbase.cc/user/adult_confirm/1 '} 
    favorites_url = 'http://wallbase.cc/user/favorites'
    fav_req = urllib2.Request(favorites_url, login_data, http_headers)
    fav_resp = urllib2.urlopen(fav_req)
    fav_list_html = fav_resp.read()

    #Begin matching the favorites urls and their names
    fav_src_dict ={}
    fav_src_url = re.findall(r'(http://wallbase.cc/user/favorites/\d+)" class="collink"><span class="counter">\d+</span>\s\w+\s*\w*', fav_list_html)
    fav_src_name = re.findall(r'</span>\s(\w+\s*\w*)', fav_list_html)
    count = 0
    while count < len(fav_src_name):
        fav_src_dict [fav_src_name[count]] = fav_src_url[count]
        count +=1
  
    #If dest_dir is blank, enter a custom dir
    if dest_dir == '':
        print "#" * 80 + '\n' + ('Please enter the path you wish to use for your favorites e.g. c:\\favorites\nLeave blank use the current directory of the Python interpreter\n') + "#" * 80  
        dest_dir = raw_input()
    print "#" * 80 + '\n' + 'Please type the name of the favorites folder you would like to download now e.g. Minimalist\n' +"#" * 80
    print fav_src_dict.keys()
    user_choice = raw_input() 
    print  "#" * 80
  
    #If the chosen directory doesn't exist, create it
    dir_check(dest_dir)
  
    #Field validation to check that what the user typed matched an available favorites folder
    if user_choice == '':
        print "Please type something"
    count = 0
    while user_choice not in fav_src_dict and count <2:
        print "That is not a valid favorite folder, %d chances left" %(2 - count)
        user_choice = raw_input()
        count +=1
        if count ==2 and user_choice not in fav_src_dict:
            print 'Please try again when you learn how to type'
            sys.exit(1)
    else:
        dest_dir = os.path.join(dest_dir, user_choice)
   
        #Check if the favorites directory exists
        dir_check(dest_dir)
        
        #Prompt for organizing folders by purity
        choices = ['False', 'True']
        print "#" * 80 + '\n' + ('Would you like to organize your images in folders based on purity level?\nOptions: True or False. (default is False)\n') + "#" * 80  
        dl_to_diff_folders = raw_input()
        if dl_to_diff_folders == '':
            dl_to_diff_folders = 'False'
        del count
        count = 0
        while dl_to_diff_folders not in choices and count < 2:
            print "Please enter True or False without quotes to make your choice."
            dl_to_diff_folders = raw_input()
            count +=1
            if count == 2 and dl_to_diff_folders not in choices:
                print "Please try again when you learn how to type"
                sys.exit(1)
            
        
        print  "#" * 80
        
        #call to actually begin downloads of the favorites
        download_walls(dest_dir, '', fav_src_dict[user_choice], 0 , 3000 , dl_to_diff_folders)
def dl_config(config_dir):
    '''This method allows you to kick of a query without going through any user prompts
    by simply feeding it a configuration file location and telling it to go.
    Can ONLY be called via the command line. If a config file isn't found, it creates a default
    that you fill in and can use. Depending on options, it will download whereever you want
    as well as sort your wallpapers based on purity level.'''
    ###############################################################################################################
    #default search values used to generate the ini files 
    #needed for the query, so they're set to wildcards on the server side
    query = ''
    nsfw = '110'
    aspect = '0'
    orderby = 'date'
    start_range = 0
    max_range = 2000
    board = '0' 
    res='0' 
    res_opt='0' 
    orderby_opt='0'
    thpp='32'
    section= 'wallpapers'
    username = ''
    password = ''
    dest_dir = ''
    query_name = ''
    dl_to_diff_folders = 'False'
    search_query = ({'query': query, 'board': board, 'nsfw': nsfw, 'res': res, 'res_opt': res_opt, 'aspect':aspect, 
                       'orderby':orderby, 'orderby_opt': orderby_opt, 'thpp':thpp, 'section': section, '1': 1,
                        'start_range' : start_range, 'max_range' : max_range, 'query_name': query_name, 'dl_to_diff_folders' : dl_to_diff_folders})
    user_vars = ({'destination_directory': dest_dir, 'username': username, 'password': password})
    ###############################################################################################################
        
    #instantiate c as a configparser class
    c = ConfigParser.ConfigParser()
  
        
    #Make the following code robust enough to create a default ini if it doesn't exist
    #as well as move the custom search ini to the destination direcotry if it does already exist
    #perhaps prompt the user about where they would like to store the ini? Don't know      
    if not os.path.exists(os.path.join(config_dir, 'Custom_Search.ini')):
        print 'No Custom_Search.ini file found, creating new default .ini'
        #Make sure the directory exists that we'll be saving the ini file to
        dir_check(config_dir)
        c.add_section("Search Query")
        for each in search_query:
            #print each, search_query[each], 
            c.set("Search Query", each, search_query[each])
        c.add_section('User Options')
        for var in user_vars:
            c.set('User Options', var, user_vars[var])
        c.set('User Options', 'destination_directory', (os.path.abspath(os.path.join(config_dir, 'CustomSearch' ))))       
        FILE = open(os.path.join(config_dir, 'Custom_Search.ini'), 'w')
        c.write(FILE)
        print "Config file stored at:\n", os.path.abspath(config_dir), '\n\n' + '#'*80 + '\nEdit the Custom_Search.ini file and press enter to begin your downloads\n' + '#'*80
        FILE.close()  
        raw_input()
        
    #Populate a list with the names of files and directories in the dest_dir
    if os.path.exists(os.path.join(config_dir, 'Custom_Search.ini')):
        #Code to read the configuration file and set variables to match what's in the config
        print 'Custom_Search.ini found\nLoading settings from %s' %(os.path.join(config_dir, 'Custom_Search.ini'))
        FILE = open(os.path.join(config_dir, 'Custom_Search.ini'), "rb")
        c.readfp(FILE)
        print '#'*40 + '\nQuery file contents\n' + '#' *40
        if c.has_section('Search Query'):
            print 'Search Query'
            for option in c.options('Search Query'):
                search_query[option] = c.get('Search Query', option)
                print "\t", option, "=", c.get('Search Query', option)
        if c.has_section('User Options'):
            print 'User Options'
            for option in c.options('User Options'):
                user_vars[option] = c.get('User Options', option)
                print "\t", option, '=', c.get('User Options', option)
        if (c.get('Search Query', 'nsfw') in purity_bits) and (c.get("User Options", 'password') == ''):
            print "NSFW query detected:\nMake sure your username and password is in the ini file, save the changes and press enter"
            raw_input()
            wallbase_auth(c.get("User Options", 'username'), c.get("User Options", 'password'))
        print '#'*40
        #Return the variables set from the config file to the dl_search method
        FILE.close() 
        
    #If the search query is based on a tag: query, then the destionation directory
    #will be created using the name of the tag, not the tag number.
    #This is done using a regex to pull the name from the html code and then creating the directory from taht
    if "tag:" in c.get("Search Query", 'query'):
        #Search headers and query necessary to get the search name of a tag: query
        search_headers = {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'referer': 'wallbase.cc/search'}
        tag_query = urllib.urlencode(search_query)
        search_req = urllib2.Request('http://wallbase.cc/search', tag_query, search_headers)
        #Initial html request, in a while loop in case of http errors
        while True:
            try:
                search_url = urllib2.urlopen(search_req)
            except urllib2.HTTPError as detail:
                print "%s error encountered\nWaiting to try again" %(detail)
                sleep(30)
                continue
            break
        
        #Populate an object with the source html
        tag_html = search_url.read()
        tag_match = re.search(r'search\s\S(\w+\s*\w+)\S', tag_html)
        
        #The following code creates a destination directory based on whether or not
        #the user has specified one in the custom_search.ini and whether or not
        print "Tag: query found!! Download directory will be based on the tags actual name, not number."
        alnum_name = ''.join(e for e in tag_match.group(1) if e.isalnum())
        if config_dir != '.' and user_vars['destination_directory'] == "":
            new_dir = os.path.abspath(os.path.join(config_dir, alnum_name))
        elif user_vars['destination_directory'] != "":
            new_dir = os.path.abspath(os.path.join(c.get("User Options", 'destination_directory'), alnum_name))
        else:
            new_dir = os.path.abspath(alnum_name)
            dir_check(alnum_name)
        dir_check(new_dir)
        new_config_dir = os.path.join(new_dir, (alnum_name + '.ini'))
        shutil.copyfile((os.path.join(config_dir, 'Custom_Search.ini')), new_config_dir)   
        FILE = open(new_config_dir, "rb")
        c.readfp(FILE)
        c.set("Search Query", 'query_name', c.get("Search Query", "query"))
        c.set("User Options", 'destination_directory', new_dir)
        FILE = open(new_config_dir, 'w')
        c.write(FILE)
        FILE = open(new_config_dir, 'rb')
        c.readfp(FILE)
        user_vars['destination_directory'] = c.get("User Options", 'destination_directory')
        FILE.close()
        
        encoded_query = urllib.urlencode(search_query)
        dest_dir = user_vars['destination_directory']
        wallbase_auth(user_vars['username'], user_vars['password'])
        download_walls(dest_dir, encoded_query, 'http://wallbase.cc/search', int(search_query['start_range']), int(search_query['max_range']), search_query['dl_to_diff_folders'])
    
    #This code creates the directories based on the Query name
    #If the dest_dir is set in the ini file, it downloads to that directory
    elif c.get("Search Query", 'query') != '':
        print "Non-blank query found\nCreating custom directory for the query and copying the .ini file.."
        alnum_name = ''.join(e for e in c.get("Search Query", 'query') if e.isalnum())
        if config_dir != '.' and user_vars['destination_directory'] == "":
            new_dir = os.path.abspath(os.path.join(config_dir, alnum_name))
        elif user_vars['destination_directory'] != "":
            new_dir = os.path.abspath(os.path.join(c.get("User Options", 'destination_directory'), alnum_name))
        else:
            new_dir = os.path.abspath(alnum_name)
            dir_check(alnum_name)
        dir_check(new_dir)
        new_config_dir = os.path.join(new_dir, (alnum_name + '.ini'))
        shutil.copyfile((os.path.join(config_dir, 'Custom_Search.ini')), new_config_dir)   
        FILE = open(new_config_dir, "rb")
        c.readfp(FILE)
        c.set("Search Query", 'query_name', c.get("Search Query", "query"))
        c.set("User Options", 'destination_directory', new_dir)
        FILE = open(new_config_dir, 'w')
        c.write(FILE)
        FILE = open(new_config_dir, 'rb')
        c.readfp(FILE)
        user_vars['destination_directory'] = c.get("User Options", 'destination_directory')
        FILE.close()
        
        encoded_query = urllib.urlencode(search_query)
        dest_dir = user_vars['destination_directory']
        wallbase_auth(user_vars['username'], user_vars['password'])
        download_walls(dest_dir, encoded_query, 'http://wallbase.cc/search', int(search_query['start_range']), int(search_query['max_range']), search_query['dl_to_diff_folders'])
        
  
    else:
        encoded_query = urllib.urlencode(search_query)
        dest_dir = user_vars['destination_directory']
        dir_check(dest_dir)
        wallbase_auth(user_vars['username'], user_vars['password'])
        download_walls(dest_dir, encoded_query, 'http://wallbase.cc/search', int(search_query['start_range']), int(search_query['max_range']), search_query['dl_to_diff_folders'])
def dl_search(dest_dir, query_string =''):
    '''This method let's you pick search options for your query. 
    You can leave both arguments blank and you will be asked to provide a query and a destination directory during the selection process.
    usage: dl_search('c:\wallbase', 'Kate Beckinsale') or dl_search()'''
   
    #If dest_dir is blank, enter a custom dir
    if dest_dir == '':
        print ("#" * 80 + '\n' + 'What directory would you like to save your queries to?\nQueries will automatically be saved in a folder named after the query\ne.g. c:\\"searches"\n' + "#" * 80)
        dest_dir = raw_input()
        dest_dir = os.path.abspath(dest_dir) 
        encoded_query, start_range, max_range, dest_dir, dl_to_diff_folders = search_options(dest_dir)    

    #call to begin actual download of the wallpapers
    download_walls(dest_dir, encoded_query, 'http://wallbase.cc/search', int(start_range), int(max_range), dl_to_diff_folders)
def logout():
    '''This sub-method when invoked will clear all cookies
        stored by this method and effectively log the user out.
        Run this method when you're down downloading if you want to 
        clear your cookies'''
  
    cj.clear_session_cookies()
    print 'You have been logged out'
def main():
    '''This function is used to call the rest of the methods from the command line'''
        
    # Make a list of command line arguments, omitting the [0] element which is the script itself.
    args = sys.argv[1:]
    
    #If no argruments are given, print proper usage and call the search method
    if not args:
        print "\nProper usage:\n\n\t[Wallscraper.py --favorites  'This allows you to download your own favorites collections from wallbase(username and password required!)]\n\n\t[Wallscraper.py --search 'This prompts the user to enter in specific search options and performs a query based on those options]\n\n\t[Wallscraper.py --config (directory where the CustomSearch_ini is located, or where you wish to create one. Leave blank for default e.g. c:\\Wallbase\\)]"; 
#        dl_search('','')
    
    #Default values passed to the method when called through a command line argument
    fdest_dir = ''
    sdest_dir = ''
    config_dir = '.'
    query_string = ''
    if len(args) == 0:
#        dl_search('','')
        print "\n\nYou must enter an argument to proceed!"
    elif args[0] == '--favorites':
        dl_favorites(fdest_dir)
        del args[0:0]
    elif args[0] == '--search':
        dl_search(sdest_dir, query_string)
        del args[0:0]
    elif args[0] == '--config':
        try:
            config_dir = args[1]
            dl_config(config_dir)
        except IndexError:
            print 'Using default directory of', os.path.abspath(config_dir)
            dl_config(config_dir)
#dl_search('', '')
#dl_favorites('')
#dl_config(r'c:\wallbase\searches')
##uncomment to run the main method from the console        
if __name__ == "__main__":
    '''If the scripts initiates itself, run the main method
    this prevent the main from being called if this module is 
    imported into another script'''
    main()

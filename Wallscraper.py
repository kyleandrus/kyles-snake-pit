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
import operator
import unicodedata
try:
    from ghost import Ghost
except:
    print "You need to install PySide as well as Ghost.py. Check your dependencies folder to install these"
    sys.exit()
try:
    from bs4 import BeautifulSoup
except:
    print "You need to install BeautifulSoup.\nGo here to download it\nhttp://www.crummy.com/software/BeautifulSoup/bs4/download/"
    sys.exit()
    


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
toplist_dict = {"0": "AllTime", "3m": '3Months', '2m':'2Months', '1m':'1Month', '2w':'2Weeks', '1w':'1Week', '3d':'3Days', '1d':'1Day'}
yes_list = {'yes', 'y', 'Y', 'Yes', 'YES', 'YEs', 'yeS','yES'}

def evaluate_js(js_file, code):
    if js_file == "":
        js_file = os.path.abspath('function_b.html')
    else:
        js_file = os.path.abspath(js_file)
    #Coded url useful for testing whether this function works properly or not
    #code = 'aHR0cDovL25zMjIzNTA2Lm92aC5uZXQvaGlnaC1yZXNvbHV0aW9uLzcwOGNjNGUyNjlmYTU1ZDZiNGYzZjE2NGIwMjRhMjc4L3dhbGxwYXBlci0xNTY4ODYuanBn'
    ghost = Ghost()
    ghost.open(js_file)
    output = ghost.evaluate('B("'+ code + '")')
    img_src = output[0]
    return str(img_src)

def html_parse(html_file, type_of_parse, login_vals = None):
    '''this method parses an html file and pulls out the data that is needed based on the type of parsing requested'''
    #####IDEA!!!! Within this function the htmlfile is available for parsing. Call
    #####Ghost.py from within this function and compute the javascript to find the src url
    
    
    #Dictionary used to store the contents of the parsing that will take place
    src_dict = {}
    
    #If I'm parsing a users collections, use the following parsing code
    if type_of_parse == 'collection':
        #Opening an html_file for parsing
        soup = BeautifulSoup(open(html_file))
        count = 0
        for link in soup.find_all('a', href=re.compile('wallbase.cc/user/collection/\d+')):
            coll_url = link.get('href')
            title_string = link.contents[3].contents
            src_dict[str(title_string)] = [count, str(coll_url)]
            count +=1
        sorted_dict = sorted(src_dict.iteritems(), key=operator.itemgetter(1))
        return sorted_dict
    
    #If i'm looking for the name of a user, use this parse
    if type_of_parse == 'match_user':
        #Opening an html_file for parsing
        soup = BeautifulSoup(open(html_file))
        count = 0
        for link in soup.find_all('a', href=re.compile('wallbase.cc/user/profile/\d+')):
            if link.contents[1]:
                user_url = link.get('href')
                user_name = link.contents[1]
                src_dict[user_name] = [count, user_url]
                count +=1
        sorted_dict = sorted(src_dict.iteritems(), key=operator.itemgetter(1))
        return sorted_dict
    
    #If I'm building a dictionary of image urls, use this
    if type_of_parse == 'match_imgs':
        #Opening an html_file for parsing
        soup = BeautifulSoup(open(html_file))
        wall_links = []
        for link in soup.find_all('a', href=re.compile('wallbase.cc/wallpaper/\d+')):
            wall_links.append(link.get('href'))
        return wall_links
    
    
####Original code for parsing image sources!!!    
#    #Use this code to match img sources to the img link
#    if type_of_parse == 'match_imgs_src':
#        #Opening an html_file for parsing
#        soup = BeautifulSoup(open(html_file))
#        img_src = ''
#        purity_link = []
#        for link in soup.find_all('img', src=re.compile(r'http://[^www]\S+(wallpaper-*\d+\S+\w+)')):
#            img_src = link.get('src')
#            img_name = re.search('(wallpaper-*\d+\S+\w+)', img_src)
#        for link in soup.find_all('li', class_=re.compile(r'[c|l]')):
#            purity_link.append(str(link))
#        for purity in purity_link:
#            purity_match = re.search(r'class="[c|l]\sselected\s(\w+)', purity)
#            if purity_match:
#                purity_link = purity_match.group(1)
#        return img_src, img_name.group(), purity_link
    #Use this code to match img sources to the img link
    #New code for attempting to parse image files using the Ghost.py javascript library
    if type_of_parse == 'match_imgs_src':
        
        #Opening an html_file for parsing
        soup = BeautifulSoup(open(html_file))
        img_src = ''
        purity_link = []
        
        #Parse the html document for script elements with matching javascript tag
        #for src in soup.find_all('script', type="text/javascript"):
        for src in soup.find('script', type="text/javascript"):
            
            #Uncomment to print the entire script string
            #print "src\n", src
            
            #Cast javascript tag to string so i can search it
            src = str(src)
            
            ############################################
            #Currently this regular expression is failing in certain cases, need to tighten it up
            #Regular expression used to separate the encoded url out from the javascript string
            #img_src = re.search(("[B]\S\S(\w+)\S"), src)
            #img_src = re.search((r"B\W\W(\w+[(=+/)]*[(=+/)]*[(=+/)]*)\W\W"), src)
            img_src = re.search((r"B[(]['](\w+[(=+/)]*)['][)]"), src)
            #############################################
            
            #Uncomment to print the encoded url
            #print "img_src.group(1)\n", img_src.group(1)
#            print unicodedata.normalize('NFKD', img_src.group(1)).encode('ascii', 'ignore')
#            print img_src.group(1)
            
            #Put the encoded url through the javascript evaluater to decode the url string
            img_src = evaluate_js("", img_src.group(1))
            
            #Uncomment to print the decoded url
            #print "img_src\n", img_src
            img_name = re.search('(wallpaper-*\d+\S+\w+)', img_src)
            
        for link in soup.find_all('li', class_=re.compile(r'[c|l]')):
            purity_link.append(str(link))
        for purity in purity_link:
            purity_match = re.search(r'class="[c|l]\sselected\s(\w+)', purity)
            if purity_match:
                purity_link = purity_match.group(1)
        return img_src, img_name.group(), purity_link
    
    

    #Use this code to parse out the active number of walls from the page
    if type_of_parse == 'active_walls':
        #Opening an html_file for parsing
        soup = BeautifulSoup(open(html_file))
        active_walls = ""
        num_of_walls = ""
        for link in soup.find_all('a', class_=("walls-link a active")): 
            active_walls = str(link.contents[0])
            regex_walls = re.search(r'(\d+),*(\d*),*(\d*)', active_walls)
            ###########################
            #regex that finds the number of search results, up to a billion
            active_walls = re.search(r'a\sactive"><span>(\d+),*(\d*),*(\d*)', active_walls)
            #return regex_walls.group()
        #Will only reach this point if the first for loop doesn't return any values for active walls.
        if True:
            #attempts to set the number of wallpapers to the regex results
            try:
                if active_walls.group(2) == '0' and active_walls.group(3) == '0':
                    num_of_walls = active_walls.group(1)
                    if num_of_walls.isdigit():       
                        num_of_walls = int(num_of_walls)
                    return num_of_walls
                if active_walls.group(3) == '0' and active_walls.group(2) != '0':
                    num_of_walls = active_walls.group(1) + active_walls.group(2)
                    if num_of_walls.isdigit():       
                        num_of_walls = int(num_of_walls)
                    return num_of_walls
                else: 
                    num_of_walls = active_walls.group(1) + active_walls.group(2) + active_walls.group(3)
                    #Cast num_of_walls to int for easier comparisons
                    if num_of_walls.isdigit():       
                        num_of_walls = int(num_of_walls)
                    return num_of_walls
            except AttributeError:
                try:
                    FILE = open(html_file)
                    html_input = FILE.read()
                    active_walls = re.search(r'count\s\S\s(\d+)', html_input)
                    FILE.close()
                    num_of_walls = active_walls.group(1)
                    #Cast num_of_walls to int for easier comparisons
                    if num_of_walls.isdigit():       
                        num_of_walls = int(num_of_walls)
                    return num_of_walls
                except AttributeError:
                    print 'number of wallpapers not found'
        
    if type_of_parse == 'user_settings':
        #code to pull thpp setting from the user page
        login_data = urllib.urlencode(login_vals)
        wallbase_auth(login_vals['usrname'], login_vals['pass'])
        http_headers =  {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'referer': 'wallbase.cc http://wallbase.cc/user/adult_confirm/1 '} 
        settings_url = 'http://wallbase.cc/user/settings'
        settings_req = urllib2.Request(settings_url, login_data, http_headers)
        settings_resp = urllib2.urlopen(settings_req)
        settings_html = settings_resp.read()
        output_html_to_file(settings_html, '.')
        html_file_loc = ('./deleteme.html')
        soup = BeautifulSoup(open(html_file_loc))
        for link in soup.find_all('input', id="filter_set_thpp"):
            os.unlink(html_file_loc)
            return link.get('value')
        
    #Need to add parsing for tag matching in the dl_config folder
    if type_of_parse == 'tag_match':
        file_tags = {}
        soup = BeautifulSoup(open(html_file))
        for link in soup.find_all('a', href=re.compile(r'wallbase.cc/search/(tag:\d+)')):
            tag = re.search(r'tag:\d+', link.get('href'))
            if link.contents[1] not in file_tags:
                file_tags[link.contents[1]] = tag.group()
        return file_tags      
def read_config(config_dir):
    '''Reads from a config file and returns the contents of the file as a searchquery and uservars dictionary'''
    #instantiate c as a configparser class
    config_file =  os.path.join(config_dir, os.path.basename(config_dir) + '.ini')
    search_query = {}
    user_vars = {}
    c = ConfigParser.ConfigParser()
    #print 'Loading settings from %s' %(os.path.basename(config_file))
    FILE = open(config_file, "rb")
    c.readfp(FILE)
    for option in c.options("Search Query"):
        search_query[option] = c.get("Search Query", option)
    for option in c.options("User Options"):
        user_vars[option] = c.get("User Options", option)
    
    #Return the variables set from the config file to the dl_search method
    FILE.close()   
    return search_query, user_vars
def write_config(config_dir, search_contents, user_contents):
    '''Takes as arugments different sets of options, and writes those options to a config file'''
    ################################################################################################################
    #Read in the contents of the file to the search_query and user_vars, then change what's been passed in further down
    search_query={}
    user_vars = {}
    c = ConfigParser.ConfigParser()
    config_file =  os.path.join(config_dir, os.path.basename(config_dir) + '.ini')
    
    #if the config file doesn't exist, create one from the passed in variables, otherwise, update it like normal
    if not os.path.isfile(config_file):
        
        #Set the variables in the search_query and user_vars to match the updated ones that were passed in
        c.add_section("Search Query")
        c.add_section("User Options")
        for each in search_contents:
            search_query[each] = search_contents[each]
        for each in user_contents:
            user_vars[each] = user_contents[each]
        for each in search_query:
            c.set("Search Query", each, search_query[each])
        for option in user_vars:
            c.set("User Options", option, user_vars[option])
        FILE = open(config_file, "w")
        c.write(FILE)
        FILE.close()   

    #Update the config file with the latest variables 
    FILE = open(os.path.abspath(config_file), "rb")
    c.readfp(FILE)
    for option in c.options("Search Query"):
        search_query[option] = c.get("Search Query", option)
    for option in c.options("User Options"):
        user_vars[option] = c.get("User Options", option)
        
    #Set the variables in the search_query and user_vars to match the updated ones that were passed in
    for each in search_contents:
        search_query[each] = search_contents[each]
    for each in user_contents:
        user_vars[each] = user_contents[each]
        
    #Set the options to match the fields in the query and the changes being written in with this method
    for each in search_query:
        c.set("Search Query", each, search_query[each])
    for option in user_vars:
        c.set("User Options", option, user_vars[option])
    FILE = open(config_file, "w")
    c.write(FILE)
    FILE.close()   
    print "Config file updated"
def dir_check(directory):
    '''This method checks whether a directory exists or not, if it doesn't, it creates it for you'''
    
    #Essentially do nothing if the path exists
    if os.path.exists(os.path.abspath(directory)):
        return directory
    else: #create the path for the user and tell the user the name of the path
        print '%s | didn\'t exist, creating...' %(os.path.abspath(directory))
        os.makedirs(os.path.join(directory))
def download_walls(dest_dir = '.', search_query='', url = '', start_range = 0, max_range = 2000, dl_to_diff_folders = "False", thpp = 32):
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
        
        #If the query is tagged as a users colleciton query, modify the url to match favorites downloaded    
        if 'collection' in url:
            url = url + '/0/' +str(start_range)
            encoded_query = search_query
            
        #If the query is tagged as a favorites query, modify the url to match favorites downloaded    
        elif 'favorites' in url:
            url = url + '/' + str(start_range)
            encoded_query = search_query
            
        #if the toplist is in the url, match this template http://wallbase.cc/toplist/0/12/eqeq/0x0/0/100/32/2d
        elif 'toplist' in url:
                url = url + '/' + str(start_range) + '/' + search_query['board'] + '/' + search_query['res_opt'] + '/' + search_query['res'] + '/' + search_query['aspect'] + '/' + search_query['nsfw']+'/' +search_query['thpp'] +'/' +search_query['time']
                encoded_query = urllib.urlencode(search_query)        #Modify the url to retrieve the current range of wallpapers
       
        #If a default encoded search_uery, use the default url modifier for wallbase searches
        else:
            url = url + '/' + str(start_range)
            encoded_query = search_query
            
        #verbose, verification to the user of which page they're on. not needed
        print "We are looking for wallpapers in the url:\n%s\nNumber of concurrent dl's set to %d" %(url, thpp)
        
        #Begin matching imgs in the html and pull the start number out of the resultant matches
        start_range = match_imgs(url, dest_dir, encoded_query, start_range, max_range, dl_to_diff_folders, thpp)
        
        #reset the url since the match is completed
        url = temp_url
        
        #Call to method used to actually download the images from the match
        #Uses dictionary of names:sources
        print "Deploying ninjas to steal wallpapers"
        get_imgs(img_names_dict, start_range, dest_dir, thpp)
        
        #set the start range in the config_file to match the current start range, this makes it easier to pickup where you left off
        if dest_dir != ".":
            search_option, user_option= read_config(dest_dir)
            search_option['start_range']= start_range
            write_config(dest_dir, search_option, user_option)
    
    if start_range >= max_range: #Stop downloads if max range is reached
        print 'Max range reached, stopping downloads'
        sys.exit(1)
def match_imgs(url, dest_dir, search_query, start_range, max_range, dl_to_diff_folders = "False", thpp = 32):

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
    temp_file_loc = os.path.join(dest_dir, 'deleteme.html')
    #Save query as html and parse the html for results
    output_html_to_file(url_html, dest_dir) 
    matchs = html_parse(temp_file_loc, 'match_imgs')
    num_of_walls = html_parse(temp_file_loc, 'active_walls')
    #delete the html to leave the directory clean
    os.unlink(temp_file_loc)
    
    if num_of_walls == "":
        print "No wallpapers found, try a different query"
        sys.exit(1)
    
    #The number of wallpapers is used to limit the matches as well as determine start and stop ranges in this method
    print 'Currently processing matches'
    if int(num_of_walls) > int(max_range):
        print '%s wallpapers found\n%d queued for dl, out of %d' %(num_of_walls, (max_range - start_range), max_range)
    elif (max_range > num_of_walls) and (num_of_walls - start_range) > 0:
        print 'Found %d wallpapers\nDownloading %d wallpapers' % (num_of_walls, num_of_walls - start_range) 
    
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
                output_html_to_file(img_src_html, dest_dir)
                
                #Parsing of the html for the source url, image name, and purity setting. 
                ####IDEA####Can also parse the tags from the same page and save them for later#####
                img_match_src, img_name, purity_match = html_parse(temp_file_loc, 'match_imgs_src')
                #Need to think of some fancy way to take these tags and use them for later!!
                #img_tags = html_parse(temp_file_loc, 'tag_match')
                
                
                #Purity sorting
                if img_match_src:
                    if dl_to_diff_folders == 'True':
                        img_names_dict[img_name] = img_match_src, purity_match
                    else:
                        img_names_dict[img_name] = img_match_src

                    if max_range < num_of_walls:
                        print "matched: ",  start_range +1 , '/', max_range
                    else:
                        print "matched: ", start_range +1, '/', num_of_walls
                    
                    #increment start number that's then returned to the other method for counting
                    start_range +=1
                    #delete html after each match to keep directory clean
                    os.unlink(temp_file_loc)
                else:
                    print 'Error: No img_src\'s found. Make sure you logged in.'
            except Exception as detail:
                print "%s error encounted\nWaiting to try again" %(detail)
                sleep(60)
                continue
            break
        
    
    #stop process if there are no more matches available
    if start_range >= 0 and len(img_names_dict) == 0: 
        print 'All wallpapers downloaded or already exist:\n"END OF LINE, TRON"'
        sys.exit()
    else: print len(img_names_dict), " Matches successfully made."
    
    #used for returning the proper number of matches if the number of matches is less than the thumbnails per page
    if len(img_names_dict) < thpp:
        return (start_range + (thpp - len(img_names_dict)))
    else:
        #start number returned that's used for incrementing elsewhere
        return start_range
def get_imgs(img_names_dict, start_range, dest_dir = '', thpp = 32):
    """This method is used to retrieve images from a dictionary of wallpapers and urls,
    saves them to your hard drive, and if they already exist skips the download."""

    #If the chosen directory doesn't exist, create it
    dir_check(dest_dir)
    
    #counters used to report back the number of successfull matches and downloads
    match_count = 0
    success_count = 0
    
    #The 32 below is because the thpp is set to 32, should make this dynamic
    #logic is such that if the passed in start number is less than 30, it downlaods the correct # of imgs
    if start_range < thpp:
        start_range -=  start_range
    elif start_range >= thpp:
        start_range -= thpp
    
    #Iterate through the loop and download images in the dictionary
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
                sleep_count = 0
                while True:
                    try:
                        urllib.urlretrieve(img_names_dict[img][0], purity_file)
                        success_count += 1
                        sleep(.5)
                    except IOError as detail:
                        print detail, 'occured, waiting to try again'
                        sleep(20)
                        sleep_count += 20
                        if sleep_count == 120:
                            print 'URL unresponsive, skipping file'
                            break
                        continue
                    break
        #Check whether the image already exists or not, if yes, skip download, if not, download it used when purity sorting is not enabled
        if img_names_dict[img][1] not in purity_list:
            if os.path.isfile(os.path.join(dest_dir, img))  :
                print 'File %d, %s exists in %s, not moved' % (start_range +1, img, os.path.basename(dest_dir))
            elif not os.path.isfile(os.path.join(dest_dir, img)):
                print 'File %d, %s downlaoding to %s folder' %(start_range +1, img, os.path.basename(dest_dir))
                sleep_count = 0
                while True:
                    try:
                        urllib.urlretrieve(img_names_dict[img], os.path.join(dest_dir, img))
                        success_count += 1
                        sleep(.5)
                    except IOError as detail:
                        print detail, 'occured, waiting to try again'
                        sleep(20)
                        sleep_count += 20
                        if sleep_count == 120:
                            print 'URL unresponsive, skipping file'
                            break
                        continue
                    break
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
    filename = 'deleteme.html'
    FILE = open(os.path.join(dest_dir,filename), "w")
    FILE.writelines(url_html)
    #print "HTML file written to:\n", os.path.abspath(os.path.join(dest_dir, filename))
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
            print "%s error encountered\nWaiting to try again\nMake sure your username and password are in the ini file, and restart the query" %(detail)
            sleep(30)
            continue
        break

    #Save cookie with login info
    cj.save(COOKIEFILE)
    #print 'User %s logged in' %(username)
def dl_favorites(dest_dir = ''):
    '''Calls to this method download a category of favorites wallpapers from 
    a users wallbase account. The only argument it takes is a destination directory. 
    Once this directory is checked it downloads the images to a directory matching the 
    name of the category within the directory'''
   
    #Code to set variables for login and search functions
    #This is needed here becuase you can't download images from favorites without logging in
    #Should probably move this to a method of it's own to just return the fav_list_html file
    print "#" * 80 + '\n' + "+" * 26 + 'Login required to dl favorites' + "+" *24 + "\n" + "#" * 80 + '\n' + 'Please enter your username:'
    user_name = raw_input()
    print "Please enter your password:"
    passw = raw_input()
    wallbase_auth(user_name, passw)
    login_vals = {'usrname': user_name, 'pass': passw, 'nopass_email': 'TypeInYourEmailAndPressEnter', 'nopass': '0', '1': '1'}
    login_data = urllib.urlencode(login_vals)
    http_headers =  {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'referer': 'wallbase.cc http://wallbase.cc/user/adult_confirm/1 '} 
    user_collection_user = {}

    #Code to the let the user download a different users collection
    print 'Would you like to download somebody else\'s favorites collections?(y or n):'
    choice = raw_input()
    if choice in yes_list:
        print "Please type the name of the user whos favorites you would like to download:"
        user_collection_user['user_title'] = raw_input()
    else:
        user_collection_user['user_title'] = user_name  
    encoded_user = urllib.urlencode(user_collection_user)
    user_list_headers =  {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'referer': 'wallbase.cc http://wallbase.cc/users/all/ '} 
    user_list_url = "http://wallbase.cc/users/all"
    user_req = urllib2.Request(user_list_url, encoded_user, user_list_headers)    
    user_list_resp = urllib2.urlopen(user_req)
    user_list_html = user_list_resp.read()
    #new code to match user names using parsing
    temp_user_html_file = os.path.join(dest_dir, 'deleteme.html')
    output_html_to_file(user_list_html, dest_dir)
    match_user = html_parse(temp_user_html_file, 'match_user')
    print "\nChoose the number of the user that matches the one you want to download from:"
    for user in match_user:
        match_user_name = ''.join(e for e in user[0] if e.isalnum())
        #Your own url profile is always matched, so ignore it. If it's not longer than that exit
        if len(match_user) == 1:
            print "That user could not be found. Check your spelling and try again"
            sys.exit()
        if match_user_name !='':
            print 'User#:', user[1][0], "User:", match_user_name
        
    #code to valide the input of the user
    count = 0
    val_input = True   
    while val_input:
        try:
            user_num = raw_input() 
            user_num = int(user_num)
            match_user_name = ''.join(e for e in user[0] if e.isalnum())
            favorites_url = match_user[user_num][1][1]
            #print 'Valid number found. Moving on...'
            val_input = False
        except ValueError:
            print "Please type a valid number"
            count +=1
            if count ==3:
                print 'Please try again when you learn how to type'
                sys.exit(1)
            else:
                continue   
            
    favorites_url = favorites_url + '/favorites'
    os.unlink(os.path.join(dest_dir, 'deleteme.html'))
    fav_req = urllib2.Request(favorites_url, login_data, http_headers)
    fav_resp = urllib2.urlopen(fav_req)
    fav_list_html = fav_resp.read()
    output_html_to_file(fav_list_html, dest_dir)
    html_file_loc = os.path.join(dest_dir, 'deleteme.html')
    #If dest_dir is blank, enter a custom dir
    if dest_dir == '':
        print  ('\nPlease enter the path you wish to use for your favorites e.g. c:\\favorites\nLeave blank use the current directory of the Python interpreter\n') 
        dest_dir = raw_input()
    
    #Call the html_parse method and get the dict with collection urls and names
    #Returned in Unicode!!! 
    fav_src_dict = html_parse(html_file_loc, 'collection')
    os.unlink(html_file_loc)

    
    temp_coll_list = []
    print 'Please type the number of the favorites folder you would like to download now e.g. 1, 2, 3, etc...\n'
    
    for collection in fav_src_dict:
        print collection[1][0], ''.join(e for e in collection[0][3:] if e.isalnum()) 
        temp_coll_list.append(str(collection[1][0]))
        
    #code to valide the input of the user
    count = 0
    val_input = True   
    while val_input:
        try:
            collection_number = raw_input() 
            collection_number = int(collection_number)
            collection_name = ''.join(e for e in fav_src_dict[collection_number][0][3:] if e.isalnum())
            dl_url = fav_src_dict[collection_number][1][1]
            #print 'Valid number found. Moving on...'
            val_input = False
        except ValueError:
            print "Please type a valid number"
            count +=1
            if count ==3:
                print 'Please try again when you learn how to type'
                sys.exit(1)
            else:
                continue
    dest_dir = os.path.join(os.path.join(dest_dir, user_collection_user['user_title'] ), collection_name)
    dir_check(dest_dir)
    
    #Prompt for organizing folders by purity
    choices = ['False', 'True']
    print ('Would you like to organize your images in folders based on purity level?\nOptions: True or False. (default is False)\n') 
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
    
    #User these variables to populate a config file if it doesn't already exist
    search_contents = {}
    user_contents = {}
    search_contents['dl_user_name'] = user_collection_user['user_title']
    search_contents['dl_user_number'] = 'n/a'
    search_contents['dl_to_diff_folders'] = dl_to_diff_folders
    search_contents['collection_name'] = collection_name
    search_contents['start_range'] = '0'
    search_contents['max_range'] = '3000'
    search_contents['thpp'] = ""
    user_contents ['username'] = user_name
    user_contents['password'] = passw
    user_contents['destination_directory'] = os.path.abspath(dest_dir)
    user_contents['collection_query'] = 'True'
    
    #If it already exists, read from it and download from there
    if os.path.isfile(os.path.join(dest_dir, collection_name + '.ini')):
        print '%s exists already, resuming from it. ' %(collection_name+ '.ini')
        search_contents, user_contents = read_config(dest_dir)
    
    #Updating the config file if one doesn't exists
    write_config(dest_dir, search_contents, user_contents )
    
    #call to actually begin downloads of the favorites
    search_contents['thpp'] = html_parse(html_file_loc, 'user_settings', login_vals)
    download_walls(dest_dir, '&', dl_url, int(search_contents['start_range']) , int(search_contents['max_range']), dl_to_diff_folders, int(search_contents['thpp']))
def dl_config(config_dir):
    '''This method allows you to kick off a query without going through any user prompts
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
    toplist_time = ''
    dl_to_diff_folders = 'False'
    search_query = ({'query': query, 'board': board, 'nsfw': nsfw, 'res': res, 'res_opt': res_opt, 'aspect':aspect, 
                       'orderby':orderby, 'orderby_opt': orderby_opt, 'thpp':thpp, 'section': section, '1': 1,
                        'start_range' : start_range, 'max_range' : max_range, 'query_name': query_name, 'dl_to_diff_folders' : dl_to_diff_folders, 'time': toplist_time})
    user_vars = ({'destination_directory': dest_dir, 'username': username, 'password': password})
    ###############################################################################################################

    #instantiate c as a configparser class
    c = ConfigParser.ConfigParser()
    download_url = "http://wallbase.cc/search"
  
    #Grabbing thpp setting from the server, you can't set it manually it I force it here
    login_vals = {'usrname': user_vars['username'], 'pass': user_vars['password'], 'nopass_email': 'TypeInYourEmailAndPressEnter', 'nopass': '0', '1': '1'}
    search_query['thpp'] = html_parse('', 'user_settings', login_vals)
    
    #If a Custom_Search.ini file doesn't exist in the given path, create one   
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
        #print '#'*40 + '\nQuery file contents\n' + '#' *40
        if c.has_section('Search Query'):
            #print 'Search Query'
            for option in c.options('Search Query'):
                search_query[option] = c.get('Search Query', option)
                #print "\t", option, "=", c.get('Search Query', option)
            #Grabbing thpp setting from the server, you can't set it manually it I force it here
            search_query['thpp'] = html_parse('', 'user_setting', login_vals)
        if c.has_section('User Options'):
            #print 'User Options'
            for option in c.options('User Options'):
                user_vars[option] = c.get('User Options', option)
                #print "\t", option, '=', c.get('User Options', option)
        if (c.get('Search Query', 'nsfw') in purity_bits) and (c.get("User Options", 'password') == ''):
            #print "NSFW query detected:\nMake sure your username and password is in the ini file, save the changes and press enter"
            raw_input()
            wallbase_auth(c.get("User Options", 'username'), c.get("User Options", 'password'))
        #print '#'*40
        #Return the variables set from the config file to the dl_search method
        FILE.close() 
        
    
   
    
    #Code to base the downloads on the BEST OF TOPLIST on wallbase
    if c.get("Search Query", 'time') in toplist_dict:
        print "BestOf Download found! Ignoring search queries..."
        if config_dir != '.' and user_vars['destination_directory'] == "":
            toplist_dir = os.path.abspath(os.path.join(config_dir, "BestOf%s" %(toplist_dict[search_query['time']])))  
        elif user_vars['destination_directory'] != "":
            toplist_dir = os.path.abspath(os.path.join(user_vars['destination_directory'], "BestOf%s" %(toplist_dict[search_query['time']])))        
        else:
            toplist_dir = os.path.abspath(os.path.join("BestOf%s" %(toplist_dict[search_query['time']])))
        dir_check(toplist_dir)
        new_config_dir = os.path.join(toplist_dir, ("BestOf%s" %(toplist_dict[search_query['time']] + '.ini')))
        
        #if config file has been read, read from it instead of re-doing the custom_search.
        if os.path.isfile(new_config_dir):
            print "%s already exists. Edit it if you want to change this query.\nPicking up where it left off" %((os.path.join(os.path.basename(toplist_dir), os.path.basename(new_config_dir))))
        else:
            shutil.copyfile((os.path.join(config_dir, 'Custom_Search.ini')), new_config_dir)   
        
        #reading the search file from the config file for the download_walls method   
        search_query, user_vars = read_config(toplist_dir)
        #Writing the new destination directory to the config file
        user_vars['destination_directory'] = toplist_dir
        write_config(toplist_dir, search_query, user_vars)
        
        #set the download url to toplist and download walls. This url doesn't need an encoded query
        download_url = 'http://wallbase.cc/toplist'
        wallbase_auth(user_vars['username'], user_vars['password'])
        #Grabbing thpp setting from the server, you can't set it manually it I force it here
        login_vals = {'usrname': user_vars['username'], 'pass': user_vars['password'], 'nopass_email': 'TypeInYourEmailAndPressEnter', 'nopass': '0', '1': '1'}
        search_query['thpp'] = html_parse('', 'user_settings', login_vals)
        download_walls(toplist_dir, search_query, download_url, int(search_query['start_range']), int(search_query['max_range']), search_query['dl_to_diff_folders'], int(search_query['thpp']))
    
    #If the search query is based on a tag: query, then the destionation directory will be created using the name of the tag, not the tag number.
    elif "tag:" in c.get("Search Query", 'query'):
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
        
        #attempts to set the name of the tag using regex 
        tag_html = search_url.read()
        tag_match = re.search(r'search\s\S(\w+)\s*(\w+)\s*(\w+)\S', tag_html)
        try:
            if tag_match.group(2) == '0' and tag_match.group(3) == '0':
                tag_name = tag_match.group(1)
            if tag_match.group(3) == '0' and tag_match.group(2) != '0':
                tag_name = tag_match.group(1) + tag_match.group(2)
            else: 
                tag_name = tag_match.group(1) + tag_match.group(2) + tag_match.group(3)
        except AttributeError:
            try:
                tag_match = re.search(r'search\s\S(\w+\s*\w+)\S', tag_html)
                tag_name = tag_match.group(1)
            except AttributeError:
                print 'no tag name found'
                tag_name = 'Unknown Tag'
        
        #The following code creates a destination directory based on whether or not
        #the user has specified one in the custom_search.ini and whether or not
        print "Tag: query found!! Download directory will be based on the tag's actual name, not number."
        alnum_name = ''.join(e for e in tag_name if e.isalnum())
        if config_dir != '.' and user_vars['destination_directory'] == "":
            new_dir = os.path.abspath(os.path.join(config_dir, alnum_name))
        elif user_vars['destination_directory'] != "":
            new_dir = os.path.abspath(os.path.join(c.get("User Options", 'destination_directory'), alnum_name))
        else:
            new_dir = os.path.abspath(alnum_name)
            dir_check(alnum_name)
        dir_check(new_dir)
        
        new_config_dir = os.path.join(new_dir, (alnum_name + '.ini'))
        #if config file has been read, read from it instead of re-doing the custom_search.
        if os.path.isfile(new_config_dir):
            print "%s already exists. Picking up where it left off" %(os.path.join(os.path.basename(new_dir), os.path.basename(new_config_dir)))
        else:
            shutil.copyfile((os.path.join(config_dir, 'Custom_Search.ini')), new_config_dir)
               
        #reading the search file from the config file for the download_walls method   
        search_query, user_vars = read_config(new_dir)
        #Writing the new destination directory to the config file
        user_vars['destination_directory'] = new_dir
        write_config(new_dir, search_query, user_vars)
        
        #encode the query and download the wallpapers
        encoded_query = urllib.urlencode(search_query)
        wallbase_auth(user_vars['username'], user_vars['password'])
        #Grabbing thpp setting from the server, you can't set it manually it I force it here
        login_vals = {'usrname': user_vars['username'], 'pass': user_vars['password'], 'nopass_email': 'TypeInYourEmailAndPressEnter', 'nopass': '0', '1': '1'}
        search_query['thpp'] = html_parse('', 'user_settings', login_vals)
        download_walls(new_dir, encoded_query, 'http://wallbase.cc/search', int(search_query['start_range']), int(search_query['max_range']), search_query['dl_to_diff_folders'], int(search_query['thpp']))
    
    #This code creates the directories based on the Query name
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
        #if config file has been read, read from it instead of re-doing the custom_search.
        if os.path.isfile(new_config_dir):
            print "%s already exists. Picking up where it left off" %(os.path.join(os.path.basename(new_dir), os.path.basename(new_config_dir)))
        else:
            shutil.copyfile((os.path.join(config_dir, 'Custom_Search.ini')), new_config_dir)
            
        #reading the search file from the config file for the download_walls method   
        search_query, user_vars = read_config(new_dir)
        #Writing the new destination directory to the config file
        user_vars['destination_directory'] = new_dir
        write_config(new_dir, search_query, user_vars)
        
        #encode the query and download the wallpapers
        encoded_query = urllib.urlencode(search_query)
        wallbase_auth(user_vars['username'], user_vars['password'])
        #Grabbing thpp setting from the server, you can't set it manually it I force it here
        login_vals = {'usrname': user_vars['username'], 'pass': user_vars['password'], 'nopass_email': 'TypeInYourEmailAndPressEnter', 'nopass': '0', '1': '1'}
        search_query['thpp'] = html_parse('', 'user_settings', login_vals)
        download_walls(new_dir, encoded_query, 'http://wallbase.cc/search', int(search_query['start_range']), int(search_query['max_range']), search_query['dl_to_diff_folders'], int(search_query['thpp']))

    #Else, if the search query is blank, it's not a toplist download, and it's not a tag: download
    else:
        print "Blank query found:\nDL'ing the newest walls that match your options..."
        if user_vars['destination_directory'] == "":
            dest_dir = os.path.join(config_dir, 'BlankQuerySearch')
        else:
            dest_dir = os.path.join(user_vars['destination_directory'], 'BlankQuerySearch')
        dir_check(dest_dir)
        #if config file has been read, read from it instead of re-doing the custom_search.
        new_config_dir = os.path.join(dest_dir, os.path.basename(dest_dir)+'.ini')
        if os.path.isfile(new_config_dir):
            print "%s already exists. Picking up where it left off" %(os.path.join(os.path.basename(dest_dir), os.path.basename(dest_dir) + '.ini'))
        else:
            shutil.copyfile(os.path.join(config_dir, 'Custom_Search.ini'),os.path.join(dest_dir, 'BlankQuerySearch.ini'))
        
        #reading the search file from the config file for the download_walls method   
        search_query, user_vars = read_config(dest_dir)
        #Writing the new destination directory to the config file
        user_vars['destination_directory'] = dest_dir
        write_config(dest_dir, search_query, user_vars)
        
        #encode the query and download the wallpapers
        encoded_query = urllib.urlencode(search_query)
        wallbase_auth(user_vars['username'], user_vars['password'])
        #Grabbing thpp setting from the server, you can't set it manually it I force it here
        login_vals = {'usrname': user_vars['username'], 'pass': user_vars['password'], 'nopass_email': 'TypeInYourEmailAndPressEnter', 'nopass': '0', '1': '1'}
        search_query['thpp'] = html_parse('', 'user_settings', login_vals)
        download_walls(dest_dir, encoded_query, 'http://wallbase.cc/search', int(search_query['start_range']), int(search_query['max_range']), search_query['dl_to_diff_folders'])
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
    
    #Default values passed to the method when called through a command line argument
#    fdest_dir = ''
    config_dir = '.'
    if len(args) == 0:
        print "\n\nYou must enter an argument to proceed!"
    elif args[0] == '--favorites':
        try:
            fdest_dir = args[1]
        except IndexError:
            fdest_dir = ''
        dl_favorites(fdest_dir)
        del args[0:0]
    elif args[0] == '--config':
        try:
            config_dir = args[1]
            dl_config(config_dir)
        except IndexError:
            print 'Using default directory of', os.path.abspath(config_dir)
            dl_config(config_dir)
#html_parse(r"Y:\Users\Kyle\Documents\Workspace\WallScraper\imgsrc.html", "tag_match")
#dl_favorites('')
#dl_config(r'.')
#evaluate_js("","")  

##uncomment to run the main method from the console    

if __name__ == "__main__":
    '''If the scripts initiates itself, run the main method
    this prevent the main from being called if this module is 
    imported into another script'''
    main()

'''
Created on Aug 1, 2012

@author: kandrus
'''

import os 
import time
import re 
import sys 
import urllib 
import urllib2
import cookielib

#Create cookie file, bind variables to openeners and requesters
#This simplifies the typing and makes it easier to make the script
#cross platform
COOKIEFILE = 'cookies.lwp'
urlopen = urllib2.urlopen
Request = urllib2.Request
cj = cookielib.LWPCookieJar()
cj.save(COOKIEFILE)
#Installing the CookieJar - This will make the urlopener bound to the CookieJar.
#This way, any urls that are opened will handle cookies appropratiely
if cj is not None:
    if os.path.isfile(COOKIEFILE):
    #If there is already a cookoie file, load from it
        cj.load(COOKIEFILE)
    if cookielib is not None:
    #This installs the cookie Jar into the opener for fetching URLs
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)
        
#Creating a dictionary to store the urls etc...
img_names_dict = {}

def dir_check(directory):
    '''This method checks whether a directory exists or not, if it doesn't, it creates it for you'''
    if os.path.exists(os.path.abspath(directory)):
        return True
    else:
        print 'Directory didn\'t exist, creating...'
        os.makedirs(os.path.join(directory))
def login_vals():
    '''Not yet implemented'''
    user_dict = {}
    username = raw_input('What is your username: ')
    password = raw_input('What is your password: ')
    user_dict = {username: password}
    print user_dict
    return user_dict
def search_options(query = '', board ='0', nsfw ='111', res='0', res_opt='0', aspect='0', orderby='0', orderby_opt='0', thpp='32', section= 'wallpapers'):
    '''
    This method populates a urllib encoded data stream used in the request of search URLs.
    usage: 
    '''
    #Populate the search_query with new values if the user doesn't want to use the default ones.)
    search_query = ({'query': query, 'board': board, 'nsfw': nsfw, 'res': res, 'res_opt': res_opt, 'aspect':aspect, 
                       'orderby':orderby, 'orderby_opt': orderby_opt, 'thpp':thpp, 'section': section, '1': 1})
    return urllib.urlencode(search_query)
def download_walls(dest_dir = '.', search_query='', url = '', start_range = 0, max_range = 2000):
    """
    This method initiates the downloads and matches, uses a counter and range, along with queries for searches
    """
    if start_range != 0:
        max_range = max_range - start_range
    #check if the directory exists or not
    dir_check(dest_dir)
    print dest_dir
    #Implement a counter so you can download up to the maximum range 
    count = 0
    while count <= max_range:
        #Used to reset the url to it's original base after the loop'
        temp_url = url
        if url == '':
            url = 'http://wallbase.cc/search/' + str(count)
        elif start_range != 0:
            url = url + '/' + str(start_range)
        else:
            url = url + '/' + str(count)
        print "We are looking for wallpapers in the url:",  url
        match_imgs(url, dest_dir, search_query, count)
        print "Deploying ninjas to steal wallpapers"
        count += 32
        start_range += 32
        url = temp_url
        #Call to method used to actually download the images
        #Use the dictionary to call the next method
        get_imgs(img_names_dict, dest_dir)
    if count >= max_range:
        print 'Max range reached, stopping downloads'
def match_imgs(url, dest_dir, search_query, count):
    blank_vals = {}
    blank_data = urllib.urlencode(blank_vals)
    search_headers = {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'referer': 'wallbase.cc/search'}
    search_req = Request(url, search_query, search_headers)
    search_url = urlopen(search_req)
    #Populate an object with the source html
    url_html = search_url.read()
    output_html_to_file(url_html, dest_dir)
    #Regular expression used to find valid wallpaper urls within the index.html
    matchs = re.findall(r'http://wallbase.cc/wallpaper/\d+', url_html)
    print 'Currently processing matches'
    for match in matchs:
        while True:
            try:
                #Time delay to try and stop 503 messages
                time.sleep(.25)
                img_src_req = Request(match, blank_data, search_headers)
                img_src_open = urlopen(img_src_req)
                img_src_html = img_src_open.read()
                #Locating the wallpapers img src url and appending the src and name to lists
                img_match_src = re.search(r'http://[^www]\S+(wallpaper-*\d+\S+\w+)', img_src_html)
                if img_match_src:
                    img_names_dict[img_match_src.group(1)] = img_match_src.group(0)
#                    print img_names_dict.get(img_match_src.group(1))
                    print 100 * int(matchs.index(match) +1)/int(len(matchs)), '% complete'
                else:
                    print 'Error: No img_src\'s found. Make sure you logged in.'
            except urllib2.URLError:
                print "Webserver error encounted\nWaiting to try again"
                time.sleep(120)
                continue
            break
    if count > 0 and len(img_names_dict) == 0:
        print 'No matches found\n"END OF LINE, PROGRAM"'
        sys.exit()
    print len(img_names_dict), " Matches successfully made."
def get_imgs(img_names_dict, dest_dir = '.'):
    """This method is used to retrieve images from a list of urls,
    saves them to your hard drive, and if they already exist skips the download."""
    #If the chosen directory doesn't exist, create it
    dir_check(dest_dir)
    match_count = 1
    success_count = 0
    #Iterate through the loop and download images in the lists
    for img in img_names_dict:
        #Check whether the file already exists or not, if yes, skip
        if os.path.isfile(os.path.join(dest_dir, img)):
            print 'File %d, %s already exists' % (match_count, img)
        else:
            print 'Retrieving wallpaper ' + str(match_count), img
            urllib.urlretrieve(img_names_dict.get(img), os.path.join(dest_dir, img))
            #Time delay to help with 503 errors
            time.sleep(1)
            success_count += 1
        match_count +=1
    if success_count:
        print success_count, 'successful downloads'
    print "End of list! Flushing temporary urls..."
    img_names_dict.clear()
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
    req = Request(login_url, login_data, http_headers)
    #Needed for wallbase to recognize that I"m logged in
    resp = urlopen(req)
    #Save cookie with login info
    cj.save(COOKIEFILE)
def dl_favorites(dest_dir = ''):
    '''Calls to this method download a category of favorites wallpapers from 
    a users wallbase account. The only argument it takes is a destination directory. 
    Once this directory is checked it downloads the images to a directory matching the 
    name of the category within the directory'''
    #Code to set variables for login and search functions
    #This is needed here becuase you can't download images from favorites without loggin in
    #Should probably move this to a method of it's own to just return the fav_list_html file
    login_vals = {'usrname': 'andrusk', 'pass': 'p0w3rus3r', 'nopass_email': 'TypeInYourEmailAndPressEnter', 'nopass': '0', '1': '1'}
    login_data = urllib.urlencode(login_vals)
    http_headers =  {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'referer': 'wallbase.cc http://wallbase.cc/user/adult_confirm/1 '} 
    favorites_url = 'http://wallbase.cc/user/favorites'
    fav_req = Request(favorites_url, login_data, http_headers)
    fav_resp = urlopen(fav_req)
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
        print ('Please enter the path you wish to use for your favorites e.g. c:\\favorites\nPress enter to use the current directory of the python interpreter')
        dest_dir = raw_input()
    print 'Please type the name of the favorites folder you would like to download now e.g. Minimalist'
    print fav_src_dict.keys()
    user_choice = raw_input()
    #If the chosen directory doesn't exist, create it
    dir_check(dest_dir)
    if user_choice == '':
        print "Please type something"
    count = 1
    while user_choice not in fav_src_dict and count <=3:
        print "That is not a valid favorite folder, please try again"
        user_choice = raw_input()
        count +=1
        if count ==3:
            print 'Please try again when you learn how to type'
            sys.exit()
    else:
        dest_dir = os.path.join(dest_dir, user_choice)
        #Check if the favorites directory exists
        dir_check(dest_dir)
        download_walls(dest_dir, '', fav_src_dict[user_choice])
    return fav_src_dict
def dl_search(dest_dir, query_string, board = '', nsfw = '111', res='0', res_opt='0', aspect='0',
               orderby='0', orderby_opt='0', thpp='32', start_range = 0, max_range = 2000):
    #If dest_dir is blank, enter a custom dir
    search_query = ({'query': query_string, 'board': board, 'nsfw': nsfw, 'res': res, 'res_opt': res_opt, 'aspect':aspect, 
                       'orderby':orderby, 'orderby_opt': orderby_opt, 'thpp':thpp, 'section': 'wallpapers', '1': 1})
    encoded_query = urllib.urlencode(search_query)
    if dest_dir == '':
        print ('What directory would you like to save your queries to?\nQueries will automatically be saved in a folder named after the query\ne.g. c:\\"searches"\\"Kate Backinsale"')
        dest_dir = raw_input()
    if query_string.isalnum() == False:
        new_query_dir = ''.join(e for e in query_string if e.isalnum())
        print new_query_dir
        dir_check(os.path.join(dest_dir, new_query_dir))   
        dest_dir = os.path.join(dest_dir, new_query_dir)
    else:
        dir_check(os.path.join(dest_dir, query_string)) 
        dest_dir = os.path.join(dest_dir, query_string)   
    download_walls(dest_dir, encoded_query, '', start_range, max_range)
def logout():
    '''This sub-method when invoked will clear all cookies
        stored by this method and effectively log the user out.
        Run this method when you're down downloading if you want to 
        clear your cookies'''
    cj.clear_session_cookies()
    print 'You have been logged out'
    
'''
            USER LOGIN   
The following section performs an 
authentication of the user on wallbase
If you attempt a search without 
authenticating you will be unable to download 
favorites or nsfw. Enter login information 
in the form of ('username', 'password')
'''
wallbase_auth('andrusk', 'p0w3rus3r')
       
'''
            SEARCH QUERY
When creating a search query you may 
either use a string for a search e.g. 'Kate'
or you can use a wallbase specific tag in 
its place e.g. 'tag:9383'
'''
#search_query = search_options('tag:9383')

#dl_favorites('')#'c:\wallbase\favorites')
dl_search('', 'tag:9383')

#download_walls(r'', search_query,'', 0, 2000)
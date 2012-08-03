'''
Created on Aug 1, 2012

@author: kandrus
'''

import os 
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
        
def login_vals():
    '''Not yet implemented'''
    user_dict = {}
    username = raw_input('What is your username: ')
    password = raw_input('What is your password: ')
    user_dict = {username: password}
    print user_dict
    return user_dict

def Search_Options(query = '', board ='0', nsfw ='111', res='0', res_opt='0', aspect='0', orderby='0', orderby_opt='0', thpp='32', section= 'wallpapers'):
    '''
    This method populates a urllib encoded data stream used in the request of search URLs.
    usaege: 
    
    Search_Options() -- returns a data stream with default query results. Give you the latest wallpapers
    Search_Options('Kate Beckinsale') -- returns a data stream that will produce a search for Kate Beckinsale
    Search_Options(query = 'different', board = 'different', etc..) You can modify these values manually to produce different search results
    '''
    
    #Populate the search_query with new values if the user doesn't want to use the default ones.)
    search_query = ({'query': query, 'board': board, 'nsfw': nsfw, 'res': res, 'res_opt': res_opt, 'aspect':aspect, 
                       'orderby':orderby, 'orderby_opt': orderby_opt, 'thpp':thpp, 'section': section, '1': 1})
    
    return urllib.urlencode(search_query)

#method for opening the wallbase url and parsing the html code
#need to add arguments and search options. Will do later
def Wallbase_Search(search_query='', url = '', max_range = 320):
    """
    This Method open the wallbase main search page, performs a query and fills lists with
    matches for images that it retrieves based on the query from the host server
    
    usage: 
    Wallbase_Search(query) -- user defined query built from Search_Options
    Wallbase_Search('', 'http://wallbase.cc/customurl) --A query performed against a specific page will ignore any search query 
    """
    #Implement a counter so you can download up to the maximum range 
    count = 0
    while count <= max_range:
        #Used to reset the url to it's original base after the loop'
        temp_url = url
        #The request need values passed, but since we're not loggin in, 
        #there's nothing to pass here. So use blank data in the req
        blank_vals = {}
        blank_data = urllib.urlencode(blank_vals)
        #Header values passed to the site, used for bypassing the age restriction
        #I don't think I need these'
        #http_headers =  {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'referer': 'wallbase.cc http://wallbase.cc/user/adult_confirm/1'} 
        #Headers used to make search think I'm referring from the site
        search_headers = {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'referer': 'wallbase.cc/search'} # http://wallbase.cc/user/adult_confirm/1'} 
        #Lists that will contain all of the urls found in the main search page 
        #as well as the associated filename of the source image
        img_src_name = []
        img_src_url = []
        #Instantiate an object to hold the html text from the webpage
        #search_url = urllib.urlopen(url)
        if url == '':
            #url = 'http://wallbase.cc/search/'
            #Delete next line if this doesn't work'
            url = 'http://wallbase.cc/search/' + str(count)
            req = Request(url, search_query, search_headers)
            search_url = urlopen(req)
        else:
        #Build a request using the search query values and header info
            url = url + '/' + str(count)
            search_req = Request(url, search_query, search_headers)
            search_url = urlopen(search_req)
        #Populate an object with the source html
        url_html = search_url.read()
        #uncomment if you want to output the url html to an html file
        output_html_to_file(url_html)
        #Regular expression used to find valid wallpaper urls and append them to the url list
        matchs = re.findall(r'http://wallbase.cc/wallpaper/\d+', url_html)
        print "We are looking for wallpapers in the url:",  url
        print 'Currently processing matches'
        for match in matchs:
            img_src_req = Request(match, blank_data, search_headers)
            img_src_open = urlopen(img_src_req)
            img_src_html = img_src_open.read()
            img_match_src = re.search(r'http://[^www]\S+(wallpaper-*\d+\S+\w+)', img_src_html)
            if img_match_src:
                img_src_name.append(img_match_src.group(1))
                img_src_url.append(img_match_src.group(0))
                #Completion percentage, useful to see where you are in the matching process
                print 100 * int(matchs.index(match) +1)/int(len(matchs)), '% complete'
            else:
                #If no <img src> is found in the file, print error. Probably a login issue.
                print 'Error: No img_src\'s found. Make sure you authed first'
        print '\n', len(img_src_name), " Wallpapers successfully found."
#        raw_input("\nPress enter to download your wallpapers!")
        print "Deploying ninjas to steal wallpapers"
        get_imgs(img_src_name, img_src_url)
        print "Wallpapers successfully downloaded. Enjoy!"
        count += 32
        url = temp_url
        
def get_imgs(img_name_list, img_url_list):
    """This method is used to retrieve images from a list of urls,
    saves them to your hard drive, and if they already exist skips the download.
    """
    count = 0
    for img in img_name_list:
        if os.path.isfile(img):
            print 'File already exists, skipping'
            count += 1
        else:
            print 'Retrieving wallpaper', img_name_list.index(img) + 1, img
            urllib.urlretrieve(img_url_list[count], img)
            count += 1
def output_html_to_file(url_html):
    #This code will output the html of the search page
    filename = 'page.html'
    FILE = open(filename, "w")
    FILE.writelines(url_html)
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
    
    #Used to fool the website into this it's a browser, and a fake referrer for login
    http_headers =  {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'referer': 'http://wallbase.cc/start/'} 
    
    #Request built to actually log the user into the server        
    req = Request(login_url, login_data, http_headers)
    
    #Needed for wallbase to recognize that I"m logged in
    resp = urlopen(req)
    
    #Save cookie with login info
    cj.save(COOKIEFILE)
    
    #print resp.read()
    #print Successfully Authed
def list_favorites():
    '''Calls to this method returns a dictionary of the users favorites
    This will allow to select which favorites they would like to download'''
    
    #Code to set variables for login and search functions
    login_vals = {'usrname': 'andrusk', 'pass': 'p0w3rus3r', 'nopass_email': 'TypeInYourEmailAndPressEnter', 'nopass': '0', '1': '1'}
    login_data = urllib.urlencode(login_vals)
    http_headers =  {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'referer': 'wallbase.cc http://wallbase.cc/user/adult_confirm/1 '} 
    favorites_url = 'http://wallbase.cc/user/favorites'
    fav_req = Request(favorites_url, login_data, http_headers)
    fav_resp = urlopen(fav_req)
    fav_list_html = fav_resp.read()
    cj.save(COOKIEFILE)
    
    #Begin matching the favorites urls and their names
    fav_src_dict ={}
    fav_src_url = re.findall(r'(http://wallbase.cc/user/favorites/\d+)" class="collink"><span class="counter">\d+</span>\s\w+\s*\w*', fav_list_html)
    fav_src_name = re.findall(r'</span>\s(\w+\s*\w*)', fav_list_html)
    count = 0
    while count < len(fav_src_name):
        fav_src_dict [fav_src_name[count]] = fav_src_url[count]
        count +=1
    return fav_src_dict
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
in the form of 'username', 'password'
'''
wallbase_auth('andrusk', 'p0w3rus3r')
       
'''
            SEARCH QUERY
When creating a search query you may 
either use a string for a search e.g. 'Kate'
or you can use a wallbase specific tag in 
its place e.g. 'tag:9383
'''
search_query = Search_Options('tag:9383')

Wallbase_Search(search_query, 'http://wallbase.cc/user/favorites/24353')

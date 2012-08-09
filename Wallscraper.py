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
    print "+" * 95 + '\n' + "#" * 95 + "\nIn the next series of questions, please choose the search options you would like to use.\nIn all cases, leaving the field blank and pressing enter will use the default value of 'all'\n" + "#" * 95 + '\n' + "+" * 95 + '\n'
    if query:
        print "+" * 95 + '\n' + "Pre-selected query detected\nYou are searching for:", query, "\n" + "+" * 95 +'\n'
    if not query:
        print "#" * 95 + '\n' + "What are you searching for?\nCan be 'tag:XXXX', or \"Kate Beckinsale\", or blank for 'new' wallpapersetc...\nUse \"\" to make the search specific, otherwise any words in the query will match\n" + "#" * 95 
        query = raw_input()
        if query =='':
            query = ''

    print "#" *95 + "\nWhat purity setting do you want to use? (default is 110)\nFirst bit allows SFW images, second bit allows Sketchy images, third bit allows NSFW images\ne.g. if you want to see only Sketchy and NSFW you will input 011. If you want only SFW images 100\n" + "#" * 95
    nsfw = raw_input()
    if nsfw == '':
        nsfw = '110'
    if nsfw[-1] == '1':
        print "+" * 32 + 'Login required for nsfw images' + "+" *33 + '\nPlease enter your username:'
        user = raw_input()
        print 'Please enter your password:'
        passw = raw_input()
        wallbase_auth(user, passw)
    print "#" * 95 + "\nWhich Aspect Ratio do you want to filter by?\n Accepted values are 'blank' => All | 1.33 => 4:3 | 1.25 => 5:4 | 1.77 => 16:9 | 1.60 => 16:10 |\n 1.70 => Netbook | 2.50 => Dual | 3.20 => Dual Wide | 0.99 => Portrait\n" + "#" * 95
    aspect = raw_input()
    if aspect =='':
        aspect = '0'
    print "#" * 95 + '\nHow do you want your wallpapers ordered? Input one of the following to choose:\n date, views, favs, relevance (default = date)\n' + "#" * 95
    orderby = raw_input()
    if orderby == '':
        orderby = 'date'
    print "#" * 95 + '\n' + "Please specify an start range of wallpers to download:\nTypically this is 0, default is 0\nYou can use this to pick up where you left off if you stopped dl's previously\n"+ "#" * 95
    start_range = raw_input()
    if start_range =='':
        start_range = 0
    print "#" * 95 + '\n' + "Please specify an end range of wallpers to download:\ndefault is 2000\n"+ "#" * 95
    max_range = raw_input()
    if max_range =='':
        max_range = 2000
    #Populate the search_query with new values if the user doesn't want to use the default ones.)
    search_query = ({'query': query, 'board': board, 'nsfw': nsfw, 'res': res, 'res_opt': res_opt, 'aspect':aspect, 
                       'orderby':orderby, 'orderby_opt': orderby_opt, 'thpp':thpp, 'section': section, '1': 1})
    return urllib.urlencode(search_query), query, int(start_range), int(max_range)
def download_walls(dest_dir = '.', search_query='', url = '', start_range = 0, max_range = 2000):
    """
    This method initiates the downloads and matches, uses a counter and range, along with queries for searches
    """
    #check if the directory exists or not
    dir_check(dest_dir)
    print 'Files being saved to:\n', os.path.abspath(dest_dir)
    #Implement a counter so you can download up to the maximum range 
    while start_range <= max_range:
        #Used to reset the url to it's original base after the loop'
        temp_url = url
        url = url + '/' + str(start_range)
        print "We are looking for wallpapers in the url:\n",  url
        start_range = match_imgs(url, dest_dir, search_query, start_range, max_range)
        print "Deploying ninjas to steal wallpapers"
        url = temp_url
        #Call to method used to actually download the images
        #Use the dictionary to call the next method
        get_imgs(img_names_dict, start_range, dest_dir)
    if start_range >= max_range:
        print 'Max range reached, stopping downloads'
        sys.exit(1)
def match_imgs(url, dest_dir, search_query, start_range, max_range):
    blank_vals = {}
    blank_data = urllib.urlencode(blank_vals)
    search_headers = {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'referer': 'wallbase.cc/search'}
    search_req = urllib2.Request(url, search_query, search_headers)
    while True:
        try:
            search_url = urllib2.urlopen(search_req)
        except urllib2.HTTPError as detail:
            print "%s error encountered\nWaiting to try again" %(detail)
            time.sleep(30)
            continue
        break
    
    #Populate an object with the source html
    url_html = search_url.read()
    output_html_to_file(url_html, dest_dir)
    #Regular expression used to find valid wallpaper urls within the index.html
    matchs = re.findall(r'http://wallbase.cc/wallpaper/\d+', url_html)
    active_walls = re.search(r'a\sactive"><span>(\d+)\D*(\d*)', url_html)
#    active_walls = re.search(r'>(\d+)\D*(\d*)', url_html)
    try:
        if active_walls.group(2) == '0':
            num_of_walls = active_walls.group(1) 
        else:
            num_of_walls = active_walls.group(1) + active_walls.group(2)
    except AttributeError:
        try:
            active_walls = re.search(r'count\s\S\s(\d+)', url_html)
            num_of_walls = active_walls.group(1)
        except AttributeError:
            print 'number of wallpapers not found'
 
    print 'Currently processing matches'
    if int(num_of_walls) > max_range:
        print '%d wallpapers found\n%d queued for dl, out of %d' %(int(num_of_walls), max_range - start_range, max_range)
    elif (max_range > int(num_of_walls)) and (int(num_of_walls)-start_range) > 0:
#        print 'Found %d wallpapers\nDownloading %d wallpapers' % (int(num_of_walls), int(num_of_walls)) 
        print 'Found %d wallpapers\nDownloading %d wallpapers' % (int(num_of_walls), int(num_of_walls)-start_range) 

    for match in matchs:
        while True and start_range <= max_range:
            try:
                #Time delay to try and stop 503 messages
                time.sleep(.25)
                img_src_req = urllib2.Request(match, blank_data, search_headers)
                img_src_open = urllib2.urlopen(img_src_req)
                img_src_html = img_src_open.read()
                #Locating the wallpapers img src url and appending the src and name to lists
                img_match_src = re.search(r'http://[^www]\S+(wallpaper-*\d+\S+\w+)', img_src_html)
                if img_match_src:
                    img_names_dict[img_match_src.group(1)] = img_match_src.group(0)
                    
#                    print img_names_dict.get(img_match_src.group(1))
#                    print 100 * int(matchs.index(match) +1)/(start_range), '% complete'
#                    if int(matchs.index(match+1))
#                    print 100 * int(matchs.index(match) +1)/int(len(matchs)), '% complete'
                    if max_range < int(num_of_walls):
                        print "matched: ",  start_range +1 , '/', max_range
                    else:
                        print "matched: ", start_range +1, '/', int(num_of_walls)
                    start_range +=1
                else:
                    print 'Error: No img_src\'s found. Make sure you logged in.'
            except urllib2.URLError as detail:
                print "%s error encounted\nWaiting to try again" %(detail)
                time.sleep(30)
                continue
            break
    if start_range >= 0 and len(img_names_dict) == 0:
        print 'All wallpapers downloaded or already exist\n:"END OF LINE, TRON"'
        sys.exit()
    else: print len(img_names_dict), " Matches successfully made."
    if len(img_names_dict) < 32:
        return (start_range + (32 - len(img_names_dict)))
    else:
        return start_range
def get_imgs(img_names_dict, start_range, dest_dir = ''):
    """This method is used to retrieve images from a list of urls,
    saves them to your hard drive, and if they already exist skips the download."""
    #If the chosen directory doesn't exist, create it
    dir_check(dest_dir)
    match_count = 0
    success_count = 0
    #The 32 below is because the thpp is set to 32, should make this dynamic
    if start_range < 32:
        start_range -=  start_range
    elif start_range >= 32:
        start_range -= 32
    #Iterate through the loop and download images in the lists
    for img in img_names_dict:
        #Check whether the file already exists or not, if yes, skip
        if os.path.isfile(os.path.join(dest_dir, img)):
            print 'File %d, %s already exists' % (start_range +1, img)
        else:
            print 'Retrieving wallpaper %d' %(start_range +1)
            urllib.urlretrieve(img_names_dict.get(img), os.path.join(dest_dir, img))
            #Time delay to help with 503 errors
            time.sleep(1)
            success_count += 1
        start_range +=1
        match_count +=1
    if success_count:
        print success_count, 'successful downloads'
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
    #Needed for wallbase to recognize that I"m logged in
    resp = urllib2.urlopen(req)
    #Save cookie with login info
    cj.save(COOKIEFILE)
    print 'User %s logged in' %(username)
def dl_favorites(dest_dir = ''):
    '''Calls to this method download a category of favorites wallpapers from 
    a users wallbase account. The only argument it takes is a destination directory. 
    Once this directory is checked it downloads the images to a directory matching the 
    name of the category within the directory'''
    #Code to set variables for login and search functions
    #This is needed here becuase you can't download images from favorites without loggin in
    #Should probably move this to a method of it's own to just return the fav_list_html file
    print "#" * 95 + '\n' + "+" * 32 + 'Login required to dl favorites' + "+" *33 + "\n" + "#" * 95 + '\n' + 'Please enter your username:'
    user = raw_input()
    print "Please enter your password:"
    passw = raw_input()
    wallbase_auth(user, passw)
    login_vals = {'usrname': 'andrusk', 'pass': 'p0w3rus3r', 'nopass_email': 'TypeInYourEmailAndPressEnter', 'nopass': '0', '1': '1'}
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
        print "#" * 95 + '\n' + ('Please enter the path you wish to use for your favorites e.g. c:\\favorites\nLeave blank use the current directory of the Python interpreter\n') + "#" * 95  
        dest_dir = raw_input()
    print "#" * 95 + '\n' + 'Please type the name of the favorites folder you would like to download now e.g. Minimalist\n' +"#" * 95
    print fav_src_dict.keys()
    user_choice = raw_input() 
    print  "#" * 95
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
#def dl_search(dest_dir, query_string, board = '', nsfw = '111', res='0', res_opt='0', aspect='0',
#               orderby='0', orderby_opt='0', thpp='32', start_range = 0, max_range = 2000):
def dl_search(dest_dir, query_string ='', ):
    '''This method let's you pick search options for your query. 
    You can leave both arguments blank and you will be asked to provide a query and a destination directory during the selection process.
    usage: dl_search('c:\wallbase', 'Kate Beckinsale') or dl_search()'''
    encoded_query, query, start_range, max_range = search_options(query_string)
    #If dest_dir is blank, enter a custom dir
    if dest_dir == '':
        print ("#" * 95 + '\n' + 'What directory would you like to save your queries to?\nQueries will automatically be saved in a folder named after the query\ne.g. c:\\"searches"\n' + "#" * 95)
        dest_dir = raw_input()
    query_string = query
    if query_string.isalnum() == False:
        new_query_dir = ''.join(e for e in query_string if e.isalnum())
        dir_check(os.path.join(dest_dir, new_query_dir))   
        dest_dir = os.path.join(dest_dir, new_query_dir)
    else:
        dir_check(os.path.join(dest_dir, query_string)) 
        dest_dir = os.path.join(dest_dir, query_string)
    download_walls(dest_dir, encoded_query, 'http://wallbase.cc/search', start_range, max_range)
def logout():
    '''This sub-method when invoked will clear all cookies
        stored by this method and effectively log the user out.
        Run this method when you're down downloading if you want to 
        clear your cookies'''
    cj.clear_session_cookies()
    print 'You have been logged out'
    
#dl_favorites('')
#dl_search('','')
def main():    
    # Make a list of command line arguments, omitting the [0] element
    # which is the script itself.
    args = sys.argv[1:]
    if not args:
        print "\nProper usage: [--favorites][--search]\nDefaulting to search..."; 
        dl_search('','')
    # todir and tozip are either set from command line
    # or left as the empty string.
    # The args array is left just containing the dirs.
    fdest_dir = ''
    sdest_dir = ''
    query_string = ''
    if len(args) == 0:
        dl_search('','')
    elif args[0] == '--favorites':
        dl_favorites(fdest_dir)
        del args[0:0]
    elif args[0] == '--search':
        dl_search(sdest_dir, query_string)
        del args[0:0]
        
if __name__ == "__main__":
        main()

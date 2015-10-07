'''
Created on Aug 1, 2012

@author: kandrus
The purpose of this script is to allow a user to automatically download
all wallpapers that match a user specified query, or wallpapers that are 
contained within their custom favorites collections from the website http://alpha.wallhaven.cc
The downloading of favorites, or nsfw images is restricted to registered users.
'''
import ConfigParser
import cookielib
import operator
import os 
import re 
import shutil
import sys 
from time import sleep
import urllib 
import urllib2
import ws_sql
try:
    from bs4 import BeautifulSoup
except:
    print "You need to install BeautifulSoup.\nGo here to download it\nhttp://www.crummy.com/software/BeautifulSoup/bs4/download/"
    sys.exit()
class WallScraper(object):
    def match_images(self):
        '''This method is used to parse the thumbnail page, then request each image in the query. Once that's done, img src, purity, tag info etc...
        is parsed from the img src page and handed off to be downloaded.'''       
        if self.num_of_walls == 'over 9000!':  #new toplist doesn't list number of results, so just set to user's max range
            self.num_of_walls = int(tools.user_vars['max_range'])
    
        if self.num_of_walls == "":
            print "No wallpapers found, try a different query"
            sys.exit(1)
        
        #The number of wallpapers is used to limit the matches as well as determine start and stop ranges in this method
        print 'Currently processing matches'
        if int(self.num_of_walls) > int(tools.user_vars['max_range']):
            print '%s wallpapers found' % self.num_of_walls
            #print '%s wallpapers found\n%s queued for dl, out of %s' % self.num_of_walls,  tools.user_vars['max_range'] - tools.user_vars['start_range'],  tools.user_vars['max_range']
        elif (int(tools.user_vars['max_range']) > self.num_of_walls) and (self.num_of_walls - int(tools.user_vars['start_range'])) > 0:
            print 'Found %d wallpapers\nDownloading %d wallpapers' % (self.num_of_walls, self.num_of_walls - int(tools.user_vars['start_range'])) 
        
        #For each img url, find the source url of that img in it's own html file
        for match in self.wall_links:
            #print match
            sleep_count = 1
            #while loop used stop matching once the max is reached
            #while True and self.match_count < int(tools.user_vars['max_range']):
            try: #and request the img src url, if http error, wait and try again
                sleep(.15)
                #request for src html of matched image
                img_src_req = urllib2.Request(match, headers=self.http_headers)
                self.html_from_url_request(img_src_req)
                parse.make_soup(self.html_from_url_request(img_src_req), True)
                #Parsing of the html for the source url, image name, and purity setting and tags. 
                #source_soup = parse.make_soup(temp_file_loc, True)
                img_match_src, img_name, purity_match = parse.find_img_source()
                #img_tags = parse.find_img_tags(parse.soup)
                #print img_match_src, img_name, purity_match, img_tags
                #Sorting of downloads based on image purity e.g. Sketchy, NSFW etc...
                if img_match_src:
                    if tools.user_vars['dl_to_diff_folders'] == 'True':
                        self.img_names_dict[img_name] = img_match_src, purity_match
                    else:
                        self.img_names_dict[img_name] = img_match_src
                    self.match_count +=1
                    if int(tools.user_vars['max_range']) < self.num_of_walls:
                        print "matched: ",  self.match_count, '/', self.num_of_walls
                    else: print "matched: ", self.match_count, '/',  int(tools.user_vars['max_range'])                            
                    #Code for checking DB for existance and updating DB with image info
                    #===============================================================
                    # skip = ws_sql.check_db(img_name, img_match_src, purity_match)
                    # if not skip:
                    #     ws_sql.insert_wall_to_db(img_name, img_match_src, purity_match, img_tags)
                    #===============================================================
                    tools.user_vars['start_range'] = int(tools.user_vars['start_range']) + 1     #increment start number that's then returned to the other method for counting
                    os.unlink(self.temp_file_loc)    #delete html after each match to keep directory clean
                else:
                    print 'Error: No img_src\'s found. Make sure you logged in.'
            except Exception as detail:
                print "%s error encounted\nWaiting to try again" %(detail)
                print "retry attempt %s/%s" %(sleep_count, 3)
                sleep(20)
                sleep_count += 1
                if sleep_count >= 20:
                    print "There's a problem with matching this URL, skipping wallpaper"
                    break
                continue
                #break
        #Stop matching process if there are no more matches available
        if int(tools.user_vars['start_range']) >= 0 and len(self.img_names_dict) == 0: 
            print 'All wallpapers downloaded or already exist'
            print 'Would you like to reset the start range in the confiruation file and start the downloads again?[Yes]'
            #code for allowing a user to reset the download counter and start over, so they don't have to do it manually
            choice = raw_input()
            if choice == '' or choice in self.yes_list:
                tools.search_query['start_range'] = 0
                #Now that tools is a class, i shouldn't need to write and read the config to change the value
                #tools.write_config(dest_dir, tools.search_query, tools.user_vars)
                #search_options, user_options = tools.load_config(dest_dir)
                tools.user_vars['start_range'] = int(tools.user_vars['start_range']) - int(self.thpp)
            if choice != '' and choice not in self.yes_list:
                print "END OF LINE, TRON"
                sys.exit()
                
        else: print len(self.img_names_dict), " Matches successfully made."
        
        #used for returning the proper number of matches if the number of matches is less than the thumbnails per page
        #=======================================================================
        # if len(self.img_names_dict) < int(self.thpp):
        #     return (int(tools.user_vars['start_range']) + (int(self.thpp) - len(self.img_names_dict)))
        # else:
        #     #start number returned that's used for incrementing elsewhere
        #     return int(tools.user_vars['start_range'])
        #=======================================================================
    def retrieve_images(self):
        """This method is used to retrieve images from a dictionary of wallpapers and urls,
        saves them to your hard drive, and if they already exist skips the download."""
        #If the chosen directory doesn't exist, create it
        dest_dir = tools.downloads_directory
        tools.directory_checker(dest_dir)

        #logic is such that if the passed in start number is less than the thumbnails per page, it downlaods the correct # of imgs
        #=======================================================================
        # if int(tools.user_vars['start_range']) < int(tools.user_vars['thpp']):
        #     tools.user_vars['start_range'] -= tools.user_vars['start_range']
        # elif int(tools.user_vars['start_range']) >= int(tools.user_vars['start_range']):
        #     tools.user_vars['start_range'] -= tools.user_vars['thpp']
        #=======================================================================
        
        #Iterate through the loop and download images in the dictionary
        for img in self.img_names_dict:

            #Setting the file name and directory in case of purity download filtering
            query_dir_name = str(tools.search_query['query'])
            query_dir_name = query_dir_name.replace(' ', '_').strip().title()
            query_dir_name = os.path.join(dest_dir, query_dir_name)
            if self.img_names_dict[img][1] in self.purity_list:
                purity_dir = os.path.join(query_dir_name,  self.img_names_dict[img][1])
            else: purity_dir = os.path.join(query_dir_name)
            purity_file = os.path.join(purity_dir, img)
            tools.directory_checker(purity_dir)            

            if self.img_names_dict[img][1] in self.purity_list:
                #else if image exists in purity directory, don't move it
                if os.path.isfile(purity_file):
                    self.already_exist +=1
                    print "File %d, %s exists in %s folder, not moving" % ((self.img_names_dict.keys().index(img)+1) *(self.match_count/int(self.thpp)) , img, self.img_names_dict[img][1])
                #If image exists is in main directory, and dl to diff true, move image to purity folder
                elif os.path.isfile(os.path.join(dest_dir, img)):
                    self.already_exist +=1
                    print "File %d, %s exists, moving to %s folder" % ((self.img_names_dict.keys().index(img)+1) *(self.match_count/int(self.thpp)), img, self.img_names_dict[img][1])
                    shutil.move(os.path.join(dest_dir, img), purity_dir)
                #else if image doesn't exist in purity direcotry, download that shit
                elif not os.path.isfile(purity_file):
                    print 'File %d, %s downloading to %s folder' %((self.img_names_dict.keys().index(img)+1) *(self.match_count/int(self.thpp)), img, self.img_names_dict[img][1])
                    sleep_count = 0
                    while True:
                        try:
                            #new url retrieve code
                            #self.opener.open(self.img_names_dict[img][0])
                            #print img
                            self.html_from_url_request(url=self.img_names_dict[img][0])
                            #print self.temp_file_loc
                            shutil.move(self.temp_file_loc, purity_file)        
                            #Old url retrieve code
                            #urllib.urlretrieve(self.img_names_dict[img][0], purity_file)
                            self.success_count += 1
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
            if self.img_names_dict[img][1] not in self.purity_list:
                if os.path.isfile(os.path.join(dest_dir, img))  :
                    self.already_exist +=1
                    print 'File %d, %s exists in %s, not moved' % ((self.img_names_dict.keys().index(img)+1) *(self.match_count/int(self.thpp)+1), img, os.path.basename(dest_dir))
                elif not os.path.isfile(os.path.join(dest_dir, img)):
                    self.already_exist +=1
                    print 'File %d, %s downlaoding to %s folder' % ((self.img_names_dict.keys().index(img)+1) *(self.match_count/int(self.thpp)+1), img, os.path.basename(dest_dir))
                    sleep_count = 0
                    while True:
                        try:
                            #print self.img_names_dict[img]
                            self.html_from_url_request(url=self.img_names_dict[img])
                            #print self.temp_file_loc
                            shutil.move(self.temp_file_loc, os.path.join(purity_file))
                            #old urlretrieve code
                            #urllib.urlretrieve(self.img_names_dict[img][0], os.path.join(dest_dir, img))
                            self.success_count += 1
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
            tools.user_vars['start_range'] +=1
        if self.success_count: print self.success_count, 'successful downloads, %d files already existed' % self.already_exist
        #clear the dictionary for the next run
        self.img_names_dict.clear()
    def query_generator(self, dest_dir = '.', search_query='', url = '', start_range = 0, max_range = 2000, dl_to_diff_folders = "False", thpp = 32): #This method is formerly called download_walls
        """
        This method initiates: downloads, html matches, urls creation, and uses a counter and range to limit the downloads
        """
        #check if the directory exists or not
        tools.directory_checker( self.destination_directory)
        print 'Files being saved to:\n', os.path.abspath(self.destination_directory) 
        
        #Pull the query information from the download config file. Useful for being verbose
        search_option, user_option= tools.load_config(self.destination_directory)
        
        ##################
        ################
        #Need to rewrite this whole section for wallhaven, below is an example of the new search url format
        #http://alpha.wallhaven.cc/search?q=kate%20beckinsale&categories=111&purity=111&resolutions=1280x960&ratios=21x9&sorting=relevance&order=desc
        ################
        #Uses the start number and max number to limit the amount of wallpapers you download
        while start_range <= max_range: 
            
            #Used as a placeholder for the url so we can reset it after the loop
            temp_url = url
            
            #If the query is tagged as a users colleciton query, modify the url to match favorites downloaded    
            if 'collection' in url:
                url = url + '/0/' +str(start_range)
                encoded_query = search_query
                print "The collection you are downloading is: %s\nThe name of the directory is %s" %(search_option['collection_name'], os.path.abspath(dest_dir)) 
                
            #If the query is tagged as a favorites query, modify the url to match favorites downloaded    
            elif 'favorites' in url:
                url = url + '/' + str(start_range)
                encoded_query = search_query
                print 'Downloading from favorites'
                
            #if the toplist is in the url, match this template http://wallbase.cc/toplist/0/12/eqeq/0x0/0/100/32/2d
            elif 'toplist' in url:
                    url = url + 'index/' + str(start_range) + '?section=wallpapers&q=' + '&board=' + search_query['board'] +\
                    '&res_opt=' + search_query['res_opt'] + '&res=' + search_query['res'] + '&aspect=' + search_query['aspect'] +\
                    '&purity=' + search_query['nsfw']+'&thpp=' +str(search_query['thpp']) +'&ts=' +search_query['toplist_time']  
                    encoded_query = urllib.urlencode(search_query)        #Modify the url to retrieve the current range of wallpapers
                    print 'Downloading from toplist'
            #If a default encoded search_uery, use the default url modifier for wallbase searches
    #        else:
    #            url = url + '/' + str(start_range)
    #            encoded_query = search_query
            else:
                ###################
                #Updating for current wallhaven search sceme
                #http://alpha.wallhaven.cc/search?q=kate%20beckinsale&categories=111&purity=111&resolutions=1280x960&ratios=21x9&sorting=relevance&order=desc
                ######################
                #url = url + 'search' + str(start_range) + '?q=' + search_query
                print type(search_query)
                if start_range/32== 0 : start_page = '?page=1' 
                else: start_page = '?page=%s' % str(start_range)/str(search_query['thpp'])
                url = url + 'search' + start_page + '&categories' + search_query['board'] + '&purity' + search_query['nsfw'] +'&resolutions' +\
                search_query['res'] + '&ratios' + search_query['res_opt'] + '&sorting' + search_query['orderby'] +'&order' + search_query['orderby_opt']
                encoded_query = urllib.urlencode(search_query)
                print search_query
                print 'Downloading a search_query'
                
            #verbose, verification to the user of which page they're on. not needed
            #print "We are looking for wallpapers in the url:\n%s\nNumber of concurrent dl's set to %d" %(url, thpp)
            if not 'collection' or 'search' in url:
                #use info from config file to be more specific during the download
                print "The query for this download is: %s\nThe name of the directory is %s" %(search_option['query'], os.path.abspath(dest_dir)) 
            
            #Begin matching imgs in the html and pull the start number out of the resultant matches
            start_range = self.match_images(url, dest_dir, encoded_query, start_range, max_range, dl_to_diff_folders, thpp)
            
            #reset the url since the match is completed
            url = temp_url
            
            #Call to method used to actually download the images from the match
            #Uses dictionary of names:sources
            print "Deploying ninjas to steal wallpapers"
            self.retrieve_images(self.img_names_dict, start_range, dest_dir, thpp)
            
            #set the start range in the config_file to match the current start range, this makes it easier to pickup where you left off
            if dest_dir != ".":
                search_option['start_range']= start_range
                tools.write_config(dest_dir, search_option, user_option)
        
        if start_range >= max_range: #Stop downloads if max range is reached
            print 'Max range reached, stopping downloads'
            sys.exit(1)
    def user_login(self, username, password):
        '''Logs the user in and saves the users session in a cookie for use when making web requests
        Also uses custom headers to pass to the web server to allow image downloads. If the user
        doesn't login, they will be unable to download private collections'''
        login_vals = {'username': username, 'password': password}
        login_url = 'http://alpha.wallhaven.cc/auth/login'
        login_data = urllib.urlencode(login_vals)
        http_headers =  {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'referer': 'http://alpha.wallhaven.cc'}   
        req = urllib2.Request(login_url, login_data, http_headers)
        resp = self.opener.open(req)
        login_html = resp.read()
        #Need to update for WallHaven
        find_logged_in = re.search('logged\-in', login_html)
        if find_logged_in.group():
            print 'User %s successfully logged in!' %(username)
            print 'Saving cookie'
            #Save cookie with login info
            self.cj.save(self.COOKIEFILE)
        else:
            print 'Login failed for %s\nCheck for csrf/username/password problems' %(username)
    
        print 'User %s logged in' %(username)
    def user_settings(self):
        '''Used to parse the users setting from the Wallhaven site. Useful for making 
        queries based on the users preferences'''
        #Url request for user settings page, then make soup and delete html file
        self.html_from_url_request(url=self.settings_url)
        soup = parse.make_soup(self.temp_file_loc, True)
        os.unlink(self.temp_file_loc)        
        #Swim through soup and find thpp setting
        for s in soup.find_all('select', id='thumbsPer'):
            for i in s.select('option'):
                if i.get('selected') == 'selected':
                    self.thpp = i.get_text('value').strip()
                    print \
                    'Successfully set thumbnails/page to user setting of %s\n'\
                    'Login to wallhaven to change your thpp setting. This \n'\
                    'determines the number of wallpapers you download at a time.\n'\
                    'http://alpha.wallhaven.cc/settings/browsing'\
                    %self.thpp
                    return self.thpp
    def new_download_generator(self):
        '''Check the dest directory, if not default, create missing dir
        then start scraping the thumbnail page for image'''
        #Load config using tools class - set search query and user variables
        #to the settings in the file. 
        tools.search_query, tools.user_vars = tools.load_config(tools.config_file)
        if tools.search_query['nsfw'][2] == '1' and (tools.user_vars['username'] or tools.user_vars['password'] )== '':
            print 'type your username and press enter'
            tools.user_vars['username'] = raw_input()
            print 'type your password and press enter'
            tools.user_vars['password'] = raw_input()
        #elif tools.search_query['nsfw'][2] != '1' and (tools.user_vars['username'] and tools.user_vars['password']) != '':
        self.user_login(tools.user_vars['username'], tools.user_vars['password'])
        self.user_settings()

        
        #Make sure the destionation directory exists
        tools.directory_checker(tools.user_vars['destination_directory'])
        self.destination_directory = tools.user_vars['destination_directory']
        tools.downloads_directory = tools.user_vars['destination_directory']        
        #Loop for retrieving images
        #Build query url from user_vars
        #http://alpha.wallhaven.cc/search?q=anime&categories=111&purity=111&resolutions=1600x900,2560x1600,3840x1080&ratios=16x9&sorting=date_added&order=asc
        while self.run:#self.success_count <= tools.user_vars['max_range']:
            try:
                #Adding support for searches first
                #Need to fix the start page number for multiple pages, get rid of start range and use something else
                if self.match_count/int(self.thpp) == 0 : start_page = '?page=1' 
                else: start_page = '?page=%s' % str(self.match_count/int(self.thpp)+1)
                self.query_url = self.wallhaven_search_url + start_page + '&categories=' + tools.search_query['board'] +\
                 '&purity=' + tools.search_query['nsfw'] +'&resolutions=' + tools.search_query['res'] + '&ratios=' +\
                 tools.search_query['res_opt'] + '&sorting=' + tools.search_query['orderby'] +'&order=' +\
                 tools.search_query['orderby_opt'] + '&q=' + tools.search_query['query'].replace(' ', '+').replace('"', '')
                print self.query_url
                print 'Downloading a search_query'
                 
                #Generate url for thumbnail match
                #should put in a loop for each page of requests
                #Below is the proper order or things!
                parse.make_soup(self.html_from_url_request(), True)
                self.num_of_walls = parse.number_of_results()
                tools.thpp = self.thpp
                self.wall_links = parse.match_imgs()
                self.match_images()
                self.retrieve_images()
                if self.success_count or self.match_count >= self.num_of_walls:
                    print 'All wallpapers downloaded or already exist'
                    print 'Would you like to reset the start range in the confiruation file and start the downloads again?[Yes]'
                    #code for allowing a user to reset the download counter and start over, so they don't have to do it manually
                    choice = raw_input()
                    if choice == '' or choice in self.yes_list:
                        self.success_count = 0
                        tools.user_vars['start_range'] = 0
                    if choice != '' and choice not in self.yes_list:
                        print "END OF LINE, TRON"
                        self.run = False
                        if os.path.exists(self.temp_file_loc): #cleanup the deleteme.html if it still exists
                            os.unlink(self.temp_file_loc)
                        sys.exit()
            except IOError as detail:
                print detail, 'occured. Fix your shit!'
    def html_from_url_request(self, search_req=None, url=None):
        if search_req==None and url == None:
            #print 'if entered'
            search_req = urllib2.Request(self.query_url, headers=self.http_headers)
        elif url:
            #print 'elif entered'
            search_req = urllib2.Request(url, headers=self.http_headers)
        url_html = self.opener.open(search_req).read()
        temp_file_loc = os.path.join(tools.user_vars['destination_directory'], 'deleteme.html')
        tools.html_to_file(url_html, tools.user_vars['destination_directory'])
        self.temp_file_loc = temp_file_loc
        return temp_file_loc
    def __init__(self):
        self.run = True
        self.user_directory = ''
        self.destination_directory  = ''
        self.username = ''
        self.password = ''
        self.temp_file_loc = ''
        self.thpp = 24
        #Settings related to logging in to the wallhaven servers, header data and password etc...
        self.wallhaven_search_url = "http://alpha.wallhaven.cc/search"
        self.settings_url = 'http://alpha.wallhaven.cc/settings/browsing'

        self.query_url = ''
        self.login_vals = {'username' : self.username, 'password' :self.password}
        self.http_headers = {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',\
                           'referer': 'http://alpha.wallhaven.cc'} 
        #Global dictionary used to store the source of a wallpaper, it's name, and it's purity
        #As well as other dictionaries used for comparisons sake
        self.img_names_dict = {}
        self.match_count = 0
        self.success_count = 0
        self.already_exist = 0
        self.num_of_walls = 0
        self.wall_links = []
        self.purity_list = ('NSFW','SKETCHY', 'SFW')
        self.purity_bits = ('001', '011', '111')
        self.toplist_dict = {"0": "AllTime", "3m": '3Months', '2m':'2Months', '1m':'1Month', \
                             '2w':'2Weeks', '1w':'1Week', '3d':'3Days', '1d':'1Day'}
        self.yes_list = {'yes', 'y', 'Y', 'Yes', 'YES', 'YEs', 'yeS','yES'}
        #Installing the CookieJar - This will make the urlopener bound to the CookieJar.
        #This allows each urlopen to use the cookies for the user session, essential for accessing NSFW images
        self.COOKIEFILE = 'cookies.lwp'
        self.urlopen = urllib2.urlopen
        self.Request = urllib2.Request
        self.cj = cookielib.LWPCookieJar()
        self.cj.save(self.COOKIEFILE)
        if self.cj is not None:
            if os.path.isfile(self.COOKIEFILE):
                #If there is already a cookoie file, load from it
                self.cj.load(self.COOKIEFILE)
            if cookielib is not None:
                #This installs the cookie Jar into the opener for fetching URLs
                self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
                urllib2.install_opener(self.opener)    
class SoupParse(object):
    def make_soup(self, html_file, clean_html=False):
        '''This method is used to make prettified soup out of a users html file. This soup
        can then be used to parse using the other parse methods. If an html file is
        particurlary dirty, you can clean optionally clean it.
        '''
        #Read wallpaper into string for parsing
        a = open(html_file).read()
        
        #Clean html if requested (necessary for Wallhaven)
        if clean_html == True:
            #Find all Span class tags in html, plus junk tags for css
            span_class = re.findall('\<*span class=\"\S+\"\>', a) 
            #print span_class
            #Remove span class markers and replace unicode with to fix html
            for span in span_class:
                a = a.replace(span,'')
            a = a.replace('</span>', '')
            a = a.replace('&lt;', '<')
            a = a.replace('&gt;', '>')
            a = a.replace('&amp;', '&')
        #Turn new html source into beautiful soup for easy parsing, html5lib if html.parser gives you trouble
        self.soup = BeautifulSoup(BeautifulSoup(a, 'html.parser').prettify(), 'html.parser')

        return self.soup
    def parse_collection(self):
        '''This method takes as input either soup and parses the soup for 
        images from a users collection. These collections must be public to 
        be parsed. NOTE: Users can parse their private collections using the 
        parse_private_collection method.'''
        #If I'm parsing a users collections, use the following parsing code
        #Opening an html_file for parsing
        self.soup
        count = 0
        for link in self.soup.find_all('a', href=re.compile('wallbase.cc/user/collection/\d+')):
            coll_url = link.get('href')
            title_string = link.contents[3].contents
            #Code for finding number of walls in the collection
            num_count = re.search(r'class="numcount"\W(\d+)\W', str(link.contents[1].contents))
            self.src_dict[str(title_string)] = [count, str(coll_url), num_count.group(1)]
            count +=1
        sorted_dict = sorted(self.src_dict.iteritems(), key=operator.itemgetter(1))
        return sorted_dict    
    def parse_private_collection(self, soup):
        '''Used to download a users private collection. Note, user must be logged
        in order to access their collection. If the user is not logged in, this will 
        fail'''
        pass
    def match_imgs(self):
        wall_links = []
        for link in self.soup.find_all('a', href=re.compile('wallhaven.cc/wallpaper/\d+')):
            if link.get('target') == '_blank': wall_links.append(link.get('href'))#append source link to wall_links list
        return wall_links
    def find_img_source(self):
        '''Used to find the src url of a wallpaper from the wallpapers landing page
        ex: http://linktopicture.wallhaven/wallpaper-xxxx.jpg'''
        img_name = ''
        img_src = ''
        #print self.soup
        for src in self.soup.find_all('img', src=re.compile('\S+wallhaven\-\d+.\w{,4}')):
            #print 'image source ' +'http:' + src.get('src')
            if src.get('id') == 'wallpaper': img_src = 'http:' + src.get('src')
            s = re.search('.*/wallhaven\-\d+.\w{,4}', img_src)
            if s: img_name = re.search('\w+\-\d+.\w{,4}', img_src)
            #print img_name.group(0)
        purity = self.soup.find_all('input')
        for p in purity:
            if p.get('name') == 'purity' and p.get('checked') == 'checked':
                purity_v = p.get('id').upper()
                break
            else: purity_v = 'SFW'
        return img_src , img_name.group(0), purity_v    
    def number_of_results(self):
        '''Find the number of wallpapers available for downloading, useful for limiting 
        your downloads'''
        find_num = self.soup.find('h1')
        active_walls = re.search(r'(\d+\,*\d*\,*\d*\,*\d*)(\sWallpapers\sfound)', str(find_num))
        self.num_of_walls = active_walls.group(1).replace(',', '')
        return self.num_of_walls
    def find_img_tags(self, soup):
        '''Used to parse tag data from wallpapers. '''
        #Need to add parsing for tag matching in the dl_config folder
        for link in self.soup.find_all('a', class_='tagname'):
            #print link.get('href')
            tag = re.search('/tag/\d+', link.get('href'))
            #print tag.group().replace('/tag/', '')
            #tag = re.search(r'tag=\d+', link.get('href'))
            #print 'contents', link.contents[0], 'title', link.get('title')
            for link in link.contents:
                print link.replace('\n', '').strip()
            #if link.contents[0]:
                #file_tags[link.get('title')] = tag.group()
                self.file_tags[link[0]] = tag.group().replace('/tag/', '')
        return self.file_tags
    def find_user(self, soup):
        #Opening an html_file for parsing
        self.soup
        count = 0
        for link in self.soup.find_all('a', href=re.compile('wallbase.cc/user/profile/\d+')):
            if link.contents[1]:
                user_url = link.get('href')
                user_name = link.contents[1]
                self.src_dict[user_name] = [count, user_url]
                count +=1
        sorted_dict = sorted(self.src_dict.iteritems(), key=operator.itemgetter(1))
        return sorted_dict    
    def __init__(self):
        self.html_file = ''
        self.thpp = 24
        self.user_directory = '.'
        self.soup = ''
        self.src_dict = {} 
        self.img_name=''
        self.img_src = ''
        self.num_of_walls = ''
        self.file_tags = {}
class WallTools(object): 
    '''ex: WallTools(self, user_directory=None, destination_directory=None)

    This class is used to hold tools related to files and configuration
    data related to WallScraper
    If no directories are passed, default it to assume the directory the script was run from    '''
    def directory_checker(self, destination_directory=None):
        '''
        This method will check for the existence of a directory, and if
        it doesn't exist, it will create the directory. 
        '''
        #Essentially do nothing if the path exists
        #print os.path.exists(os.path.abspath(destination_directory))
        #print os.path.abspath(destination_directory)
        if os.path.exists(os.path.abspath(destination_directory)):
            return destination_directory
        else: #create the path for the user and tell the user the name of the path
            print '%s | didn\'t exist, creating...' %(os.path.abspath(destination_directory))
            os.makedirs(os.path.join(destination_directory))            
    def load_config(self, configuration_file):
        '''
        Takes as input the location of a *.ini file, and returns two tuples
        one for search query data, one for user data
        '''
        print 'Loading settings from %s' %(os.path.basename(self.config_file))
        self.config_file = configuration_file
        FILE = open(self.config_file, "rb")
        self.c.readfp(FILE)
        for option in self.c.options("Search Query"):
            self.search_query[option] = self.c.get("Search Query", option)
        for option in self.c.options("User Options"):
            self.user_vars[option] = self.c.get("User Options", option)
        
        #Return the variables set from the config file to the dl_search method
        FILE.close()   
        return self.search_query, self.user_vars
    def write_config(self, config_dir, search_contents, user_contents ):
        '''
        Takes as input a search query (tuple), and user options (tuple)
        Then output a *.ini file matching the name of the configuration_file string. 
        '''
        self.config_file = config_dir
        #if the config file doesn't exist, create one from the passed in variables, otherwise, update it like normal
        if not os.path.isfile(self.config_file):
            
            #Set the variables in the search_query and user_vars to match the updated ones that were passed in
            self.c.add_section("Search Query")
            self.c.add_section("User Options")
            for each in search_contents:
                self.search_query[each] = search_contents[each]
            for each in user_contents:
                self.user_vars[each] = user_contents[each]
            for each in self.search_query:
                self.c.set("Search Query", each, self.search_query[each])
            for option in self.user_vars:
                self.c.set("User Options", option, self.user_vars[option])
            FILE = open(self.config_file, "w")
            self.c.write(FILE)
            FILE.close()   
    
        #Update the config file with the latest variables 
        FILE = open(os.path.abspath(self.config_file), "rb")
        self.c.readfp(FILE)
        for option in self.c.options("Search Query"):
            self.search_query[option] = self.c.get("Search Query", option)
        for option in self.c.options("User Options"):
            self.user_vars[option] = self.c.get("User Options", option)
            
        #Set the variables in the search_query and user_vars to match the updated ones that were passed in
        for each in search_contents:
            self.search_query[each] = search_contents[each]
        for each in user_contents:
            self.user_vars[each] = user_contents[each]
            
        #Set the options to match the fields in the query and the changes being written in with this method
        for each in self.search_query:
            self.c.set("Search Query", each, self.search_query[each])
        for option in self.user_vars:
            self.c.set("User Options", option, self.user_vars[option])
        FILE = open(self.config_file, "w")
        self.c.write(FILE)
        FILE.close()   
        print "Config file updated"
    def html_to_file(self, html_file, destination_directory):
        #This code will output the html of the search page, needs fed a req.open()
        tools.directory_checker(destination_directory)
        filename = 'deleteme.html'
        FILE = open(os.path.join(destination_directory,filename), "wb")
        FILE.writelines(html_file)
        #print "HTML file written to:\n", os.path.abspath(os.path.join(dest_dir, filename))
        FILE.close()
    def __init__(self):
            self.user_directory = '.'
            self.downloads_directory = '.'
            self.html_file = '.'
            self.search_query = {}
            self.user_vars = {}
            self.config_file = ''
            self.config_file =  os.path.join(self.downloads_directory, os.path.basename(self.downloads_directory) + '.ini')
            self.c = ConfigParser.ConfigParser()
            self.q = ''
            self.nsfw = '110'
            self.aspect = '0'
            self.orderby = 'date'
            self.start_range = 0
            self.max_range = 2000
            self.board = '0' 
            self.res='0' 
            self.res_opt='0' 
            self.orderby_opt='0'
            self.thpp='32'
            self.section= 'wallpapers'
            self.username = 'andrusk'
            self.password = 'p0w3rus3r'
            self.dest_dir = ''
            self.query_name = ''
            self.toplist_time = ''
            self.dl_to_diff_folders = 'False'
            self.search_query = ({'query': self.q, 'board': self.board, 'nsfw': self.nsfw, 'res': self.res, 'res_opt': self.res_opt, 'aspect':self.aspect, 
                       'orderby':self.orderby, 'orderby_opt': self.orderby_opt, 'thpp':self.thpp, 'section': self.section, '1': 1,
                        'start_range' : self.start_range, 'max_range' : self.max_range, 'query_name': self.query_name, 'dl_to_diff_folders' : self.dl_to_diff_folders, 'toplist_time': self.toplist_time})
            self.user_vars = ({'destination_directory': self.dest_dir, 'username': self.username, 'password': self.password})

def main():
    '''This function is used to call the rest of the methods from the command line'''
        
    # Make a list of command line arguments, omitting the [0] element which is the script itself.
    args = sys.argv[1:]
    
    #If no argruments are given, print proper usage and call the search method
    if not args:
        print "\nProper usage:\n\n\t[Wallscraper.py --favorites  'This allows you to download your own favorites collections from wallbase(username and password required!)]\n\n\t[Wallscraper.py --search 'This prompts the user to enter in specific search options and performs a query based on those options]\n\n\t[Wallscraper.py --config (directory where the CustomSearch_ini is located, or where you wish to create one. Leave blank for default e.g. c:\\Wallbase\\)]"; 
    
    #Default values passed to the method when called through a command line argument
    config_dir = '.'
    if len(args) == 0:
        print "\n\nYou must enter an argument to proceed!"
    elif args[0] == '--favorites':
        try:
            fdest_dir = args[1]
        except IndexError:
            fdest_dir = ''
        scrape.favorites_download(fdest_dir)
        del args[0:0]
    elif args[0] == '--config':
        try:
            config_dir = args[1]
#            wallbase_auth('andrusk', 'p0w3rus3r')
            scrape.config_download(config_dir)
        except IndexError:
            print 'Using default directory of', os.path.abspath(config_dir)
            scrape.config_download(config_dir)
if __name__ == "__main__":
    '''If the scripts initiates itself, run the main method
    this prevent the main from being called if this module is 
    imported into another script'''
    scrape = WallScraper()
    tools = WallTools()
    parse = SoupParse()
    tools.config_file = './Custom_Search.ini'
    scrape.new_download_generator()
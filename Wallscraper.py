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
    #Default path for WallScraper to use
#===============================================================================
#     def config_download(self, config_dir):
#         '''This method allows you to kick off a query without going through any user prompts
#         by simply feeding it a configuration file location and telling it to go.
#         Can ONLY be called via the command line. If a config file isn't found, it creates a default
#         that you fill in and can use. Depending on options, it will download whereever you want
#         as well as sort your wallpapers based on purity level.'''
#     
#         #instantiate c as a configparser class
#         c = ConfigParser.ConfigParser()
#       
#     
#         
#             
#         #Populate a list with the names of files and directories in the dest_dir
#         if os.path.exists(os.path.join(config_dir, 'Custom_Search.ini')):
#             #Code to read the configuration file and set variables to match what's in the config
#             print 'Custom_Search.ini found\nLoading settings from %s' %(os.path.join(config_dir, 'Custom_Search.ini'))
#             FILE = open(os.path.join(config_dir, 'Custom_Search.ini'), "rb")
#             c.readfp(FILE)
#             if c.has_section('User Options'):
#                 print 'User Options'
#                 for option in c.options('User Options'):
#                     user_vars[option] = c.get('User Options', option)
#                     print "\t", option, '=', c.get('User Options', option)
#             
#     
#             print '#'*40 + '\nQuery file contents\n' + '#' *40
#             if c.has_section('Search Query'):
#                 print 'Search Query'
#                 for option in c.options('Search Query'):
#                     search_query[option] = c.get('Search Query', option)
#                     print "\t", option, "=", c.get('Search Query', option)
#                     
#                 #Grabbing thpp setting from the server, you can't set it manually it I force it here
#                 login_vals = {'usrname': user_vars['username'], 'pass': user_vars['password'], 'nopass_email': 'TypeInYourEmailAndPressEnter', 'nopass': '0', '1': '1'}
#                 #search_query['thpp'] = img_parse('', 'user_settings', login_vals)
#                 search_query['thpp'] = 32
#     
#     
#             
#             if (c.get('Search Query', 'nsfw') in self.purity_bits) and (c.get("User Options", 'password') == ''):
#                 print "NSFW query detected:\nMake sure your username and password is in the ini file, save the changes, then come back and press enter"
#                 raw_input()
#             self.user_login(c.get("User Options", 'username'), c.get("User Options", 'password'))
#             #print '#'*40
#             #Return the variables set from the config file to the dl_search method
#             FILE.close() 
#             
#         #If a Custom_Search.ini file doesn't exist in the given path, create one   
#         if not os.path.exists(os.path.join(config_dir, 'Custom_Search.ini')):
#             print 'No Custom_Search.ini file found, creating new default .ini'
#             #Make sure the directory exists that we'll be saving the ini file to
#             tools.directory_checker(config_dir)
#             
#             #Grabbing thpp setting from the server, you can't set it manually it I force it here
#     #        search_query['thpp'] = img_parse('', 'user_settings', login_vals)
#             search_query['thpp'] = 32
#                     
#             c.add_section("Search Query")
#             for each in search_query:
#                 print each, search_query[each], 
#                 c.set("Search Query", each, search_query[each])
#             c.add_section('User Options')
#             for var in user_vars:
#                 c.set('User Options', var, user_vars[var])
#             c.set('User Options', 'destination_directory', (os.path.abspath(os.path.join(config_dir, 'CustomSearch' ))))       
#             FILE = open(os.path.join(config_dir, 'Custom_Search.ini'), 'w')
#             c.write(FILE)
#             print "Config file stored at:\n", os.path.abspath(config_dir), '\n\n' + '#'*80 + '\nEdit the Custom_Search.ini file and press enter to begin your downloads\n' + '#'*80
#             FILE.close()  
#             raw_input()
#             
#         
#        
#         
#         #Code to base the downloads on the BEST OF TOPLIST on wallbase
#         print c.get('Search Query', 'toplist_time')
#         if c.get("Search Query", 'toplist_time') in self.toplist_dict:
#             print "BestOf Download found! Ignoring search queries..."
#             if config_dir != '.' and user_vars['destination_directory'] == "":
#                 toplist_dir = os.path.abspath(os.path.join(config_dir, "BestOf%s" %(self.toplist_dict[search_query['toplist_time']])))  
#             elif user_vars['destination_directory'] != "":
#                 toplist_dir = os.path.abspath(os.path.join(user_vars['destination_directory'], "BestOf%s" %(self.toplist_dict[search_query['toplist_time']])))        
#             else:
#                 toplist_dir = os.path.abspath(os.path.join("BestOf%s" %(self.toplist_dict[search_query['toplist_time']])))
#             tools.directory_checker(toplist_dir)
#             new_config_dir = os.path.join(toplist_dir, ("BestOf%s" %(self.toplist_dict[search_query['toplist_time']] + '.ini')))
#             
#             #if config file has been read, read from it instead of re-doing the custom_search.
#             if os.path.isfile(new_config_dir):
#                 print "%s already exists. Edit it if you want to change this query.\nPicking up where it left off" %((os.path.join(os.path.basename(toplist_dir), os.path.basename(new_config_dir))))
#             else:
#                 shutil.copyfile((os.path.join(config_dir, 'Custom_Search.ini')), new_config_dir)   
#             
#             #reading the search file from the config file for the download_walls method   
#             search_query, user_vars = tools.load_config(toplist_dir)
#             #Writing the new destination directory to the config file
#             user_vars['destination_directory'] = toplist_dir
#             tools.write_config(toplist_dir, search_query, user_vars)
#             
#             #set the download url to toplist and download walls. This url doesn't need an encoded query
#             download_url = 'http://alpha.wallhaven.cc/toplist/'
#     #        wallbase_auth(user_vars['username'], user_vars['password'])
#             #Grabbing thpp setting from the server, you can't set it manually it I force it here
#             login_vals = {'usrname': user_vars['username'], 'pass': user_vars['password'], 'nopass_email': 'TypeInYourEmailAndPressEnter', 'nopass': '0', '1': '1'}
#     #        search_query['thpp'] = img_parse('', 'user_settings', login_vals)
#             search_query['thpp'] = 32
#     
#             self.query_generator(toplist_dir, search_query, download_url, int(search_query['start_range']), int(search_query['max_range']), search_query['dl_to_diff_folders'], int(search_query['thpp']))
#         
#         #If the search query is based on a tag: query, then the destionation directory will be created using the name of the tag, not the tag number.
#         elif "tag=" in c.get("Search Query", 'query'):
#             #Search headers and query necessary to get the search name of a tag: query
#             search_headers = {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'referer': 'alpha.wallhaven.cc/search'}
#             tag_query = urllib.urlencode(search_query)
#             search_req = urllib2.Request('http://alpha.wallhaven.cc/search', headers=search_headers)
#             #Initial html request, in a while loop in case of http errors
#             while True:
#                 try:
#                     search_url = urllib2.urlopen(search_req)
#                 except urllib2.HTTPError as detail:
#                     print "%s error encountered\nWaiting to try again" %(detail)
#                     sleep(30)
#                     continue
#                 break
#             
#             #attempts to set the name of the tag using regex 
#             tag_html = search_url.read()
#             tag_match = re.search(r'search\s\S(\w+)\s*(\w+)\s*(\w+)\S', tag_html)
#             try:
#                 if tag_match.group(2) == '0' and tag_match.group(3) == '0':
#                     tag_name = tag_match.group(1)
#                 if tag_match.group(3) == '0' and tag_match.group(2) != '0':
#                     tag_name = tag_match.group(1) + tag_match.group(2)
#                 else: 
#                     tag_name = tag_match.group(1) + tag_match.group(2) + tag_match.group(3)
#             except AttributeError:
#                 try:
#                     tag_match = re.search(r'search\s\S(\w+\s*\w+)\S', tag_html)
#                     tag_name = tag_match.group(1)
#                 except AttributeError:
#                     print 'no tag name found'
#                     tag_name = 'Unknown Tag'
#             
#             #The following code creates a destination directory based on whether or not
#             #the user has specified one in the custom_search.ini and whether or not
#             print "Tag: query found!! Download directory will be based on the tag's actual name, not number."
#             alnum_name = ''.join(e for e in tag_name if e.isalnum())
#             if config_dir != '.' and user_vars['destination_directory'] == "":
#                 new_dir = os.path.abspath(os.path.join(config_dir, alnum_name))
#             elif user_vars['destination_directory'] != "":
#                 new_dir = os.path.abspath(os.path.join(c.get("User Options", 'destination_directory'), alnum_name))
#             else:
#                 new_dir = os.path.abspath(alnum_name)
#                 tools.directory_checker(alnum_name)
#             tools.directory_checker(new_dir)
#             
#             new_config_dir = os.path.join(new_dir, (alnum_name + '.ini'))
#             #if config file has been read, read from it instead of re-doing the custom_search.
#             if os.path.isfile(new_config_dir):
#                 print "%s already exists. Picking up where it left off" %(os.path.join(os.path.basename(new_dir), os.path.basename(new_config_dir)))
#             else:
#                 shutil.copyfile((os.path.join(config_dir, 'Custom_Search.ini')), new_config_dir)
#                    
#             #reading the search file from the config file for the download_walls method   
#             search_query, user_vars = tools.load_config(new_dir)
#             #Writing the new destination directory to the config file
#             user_vars['destination_directory'] = new_dir
#             tools.write_config(new_dir, search_query, user_vars)
#             
#             #encode the query and download the wallpapers
#             encoded_query = urllib.urlencode(search_query)
#     #        wallbase_auth(user_vars['username'], user_vars['password'])
#             #Grabbing thpp setting from the server, you can't set it manually it I force it here
#             login_vals = {'usrname': user_vars['username'], 'pass': user_vars['password'], 'nopass_email': 'TypeInYourEmailAndPressEnter', 'nopass': '0', '1': '1'}
#             #search_query['thpp'] = img_parse('', 'user_settings', login_vals)
#             search_query['thpp'] = 32
#     
#             self.query_generator(new_dir, encoded_query, 'http://alpha.wallhaven.cc/search', int(search_query['start_range']), int(search_query['max_range']), search_query['dl_to_diff_folders'], int(search_query['thpp']))
#         
#         #This code creates the directories based on the Query name
#         elif c.get("Search Query", 'query') != '':
#             print "Non-blank query found\nCreating custom directory for the query and copying the .ini file.."
#             alnum_name = ''.join(e for e in c.get("Search Query", 'query') if e.isalnum())
#             if config_dir != '.' and user_vars['destination_directory'] == "":
#                 new_dir = os.path.abspath(os.path.join(config_dir, alnum_name))
#             elif user_vars['destination_directory'] != "":
#                 new_dir = os.path.abspath(os.path.join(c.get("User Options", 'destination_directory'), alnum_name))
#             else:
#                 new_dir = os.path.abspath(alnum_name)
#                 tools.directory_checker(alnum_name)
#             tools.directory_checker(new_dir)
#             new_config_dir = os.path.join(new_dir, (alnum_name + '.ini'))
#             tools.config_file = new_config_dir
# 
#             #if config file has been read, read from it instead of re-doing the custom_search.
#             if os.path.isfile(new_config_dir):
#                 print "%s already exists. Picking up where it left off" %(os.path.join(os.path.basename(new_dir), os.path.basename(new_config_dir)))
#             else:
#                 shutil.copyfile((os.path.join(config_dir, 'Custom_Search.ini')), new_config_dir)
#                 
#             #reading the search file from the config file for the download_walls method   
#             search_query, user_vars = tools.load_config(new_dir)
#             
#             ##
#             #print search_query, '\n', user_vars
#             ##
#             #Writing the new destination directory to the config file
#             user_vars['destination_directory'] = new_dir
#             tools.write_config(new_dir, search_query, user_vars)
#             
#             #encode the query and download the wallpapers
#             #ref_list = wallbase_auth(user_vars['username'], user_vars['password'])
#             #print ref_list
#     #        search_query['csrf'] = ref_list['csrf']
#     #        search_query['ref'] = ref_list['ref']
#             #encoded_query = urllib.urlencode(search_query)
#     
#             #Grabbing thpp setting from the server, you can't set it manually it I force it here
#             #login_vals = {'usrname': user_vars['username'], 'pass': user_vars['password'], 'nopass_email': 'TypeInYourEmailAndPressEnter', 'nopass': '0', '1': '1'}
#     #        search_query['thpp'] = img_parse('', 'user_settings', login_vals)
#             search_query['thpp'] = 32
#             
#             ###
#             #print encoded_query
#             self.query_generator(new_dir, search_query, 'http://alpha.wallhaven.cc/', int(search_query['start_range']), int(search_query['max_range']), search_query['dl_to_diff_folders'], int(search_query['thpp']))
#     
#             ###
#     #        download_walls(new_dir, encoded_query, 'http://alpha.wallhaven.cc/search', int(search_query['start_range']), int(search_query['max_range']), search_query['dl_to_diff_folders'], int(search_query['thpp']))
#     
#         #Else, if the search query is blank, it's not a toplist download, and it's not a tag: download
#         else:
#             print "Blank query found:\nDL'ing the newest walls that match your options..."
#             if user_vars['destination_directory'] == "":
#                 dest_dir = os.path.join(config_dir, 'BlankQuerySearch')
#             else:
#                 dest_dir = os.path.join(user_vars['destination_directory'], 'BlankQuerySearch')
#             tools.directory_checker(dest_dir)
#             #if config file has been read, read from it instead of re-doing the custom_search.
#             new_config_dir = os.path.join(dest_dir, os.path.basename(dest_dir)+'.ini')
#             if os.path.isfile(new_config_dir):
#                 print "%s already exists. Picking up where it left off" %(os.path.join(os.path.basename(dest_dir), os.path.basename(dest_dir) + '.ini'))
#             else:
#                 shutil.copyfile(os.path.join(config_dir, 'Custom_Search.ini'),os.path.join(dest_dir, 'BlankQuerySearch.ini'))
#             
#             #reading the search file from the config file for the download_walls method   
#             search_query, user_vars = tools.load_config(dest_dir)
#             #Writing the new destination directory to the config file
#             user_vars['destination_directory'] = dest_dir
#             tools.write_config(dest_dir, search_query, user_vars)
#             
#             #encode the query and download the wallpapers
#             encoded_query = urllib.urlencode(search_query)
#             #wallbase_auth(user_vars['username'], user_vars['password'])
#             #Grabbing thpp setting from the server, you can't set it manually it I force it here
#             #login_vals = {'usrname': user_vars['username'], 'pass': user_vars['password'], 'nopass_email': 'TypeInYourEmailAndPressEnter', 'nopass': '0', '1': '1'}
#     #        search_query['thpp'] = img_parse('', 'user_settings', login_vals)
#             search_query['thpp'] = 32
#             self.query_generator(dest_dir, encoded_query, 'http://alpha.wallhaven.cc/', int(search_query['start_range']), int(search_query['max_range']), search_query['dl_to_diff_folders'])
#===============================================================================
    #===========================================================================
    # def favorites_download(self, destination_directory):
    #     '''Calls to this method download a category of favorites wallpapers from 
    #     a users wallbase account. The only argument it takes is a destination directory. 
    #     Once this directory is checked it downloads the images to a directory matching the 
    #     name of the category within the directory'''
    #    
    #     #Code to set variables for login and search functions
    #     #This is needed here becuase you can't download images from favorites without logging in
    #     #Should probably move this to a method of it's own to just return the fav_list_html file
    #     print "#" * 80 + '\n' + "+" * 26 + 'Login required to dl favorites' + "+" *24 + "\n" + "#" * 80 + '\n' + 'Please enter your username:'
    #     user_name = raw_input()
    #     print "Please enter your password:"
    #     passw = raw_input()
    # #    wallbase_auth(user_name, passw)
    #     login_vals = {'usrname': user_name, 'pass': passw, 'nopass_email': 'TypeInYourEmailAndPressEnter', 'nopass': '0', '1': '1'}
    #     login_data = urllib.urlencode(login_vals)
    #     http_headers =  {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'referer': 'wallbase.cc http://wallbase.cc/user/adult_confirm/1 '} 
    #     user_collection_user = {}
    # 
    #     #Code to the let the user download a different users collection
    #     print 'Would you like to download somebody else\'s favorites collections?(y or n):'
    #     choice = raw_input()
    #     if choice in self.yes_list:
    #         print "Please type the name of the user whos favorites you would like to download:"
    #         user_collection_user['user_title'] = raw_input()
    #     else:
    #         user_collection_user['user_title'] = user_name  
    #     encoded_user = urllib.urlencode(user_collection_user)
    #     user_list_headers =  {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'referer': 'wallbase.cc http://wallbase.cc/users/all/ '} 
    #     user_list_url = "http://wallbase.cc/users/all"
    #     user_req = urllib2.Request(user_list_url, encoded_user, user_list_headers)    
    #     user_list_resp = urllib2.urlopen(user_req)
    #     user_list_html = user_list_resp.read()
    #     #new code to match user names using parsing
    #     temp_user_html_file = os.path.join(self.destination_directory, 'deleteme.html')
    #     tools.html_to_file(user_list_html, self.destination_directory)
    #     soup = SoupParse.make_soup(temp_user_html_file, clean_html=True)
    #     match_user = SoupParse.find_user(soup)
    #     choose_user = True 
    #     #If you want to download your own wallpapers, skip the user selection process
    #     if user_name in match_user[1][0]:
    #         user_num = 1
    #         choose_user=False
    #     else:
    #         print "\nChoose the number of the user that matches the one you want to download from:"
    #         for user in match_user:
    #             match_user_name = ''.join(e for e in user[0] if e.isalnum())
    #             #Your own url profile is always matched, so ignore it. If it's not longer than that exit
    #             if len(match_user) == 1:
    #                 print "That user could not be found. Check your spelling and try again"
    #                 sys.exit()
    #             if match_user_name !='':
    #                 print 'User#:', user[1][0], "User:", match_user_name
    #         
    #     #Code to validate the input of the user
    #     count = 0
    #     while choose_user:
    #         try:
    #             user_num = raw_input() 
    #             user_num = int(user_num)
    #             match_user_name = ''.join(e for e in user[0] if e.isalnum())
    #             choose_user = False
    #         except ValueError:
    #             print "Please type a valid number"
    #             count +=1
    #             if count ==3:
    #                 print 'Please try again when you learn how to type'
    #                 sys.exit(1)
    #             else:
    #                 continue   
    #             
    #     favorites_url = match_user[user_num][1][1] + '/favorites'
    #     os.unlink(os.path.join(self.destination_directory, 'deleteme.html'))
    #     fav_req = urllib2.Request(favorites_url, login_data, http_headers)
    #     fav_resp = urllib2.urlopen(fav_req)
    #     fav_list_html = fav_resp.read()
    #     tools.html_to_file(self, fav_list_html, destination_directory)
    #     html_file_loc = os.path.join(self.destination_directory, 'deleteme.html')
    #     #If dest_dir is blank, enter a custom dir
    #     if self.destination_directory == '':
    #         print  ('\nPlease enter the path you wish to use for your favorites e.g. c:\\favorites\nLeave blank use the current directory of the Python interpreter\n') 
    #         dest_dir = raw_input()
    #     
    #     #Call the img_parse method and get the dict with collection urls and names
    #     SoupParse.make_soup(self, html_file_loc, True)
    #     fav_src_dict = SoupParse.parse_collection(self, self.soup)
    #     os.unlink(html_file_loc)
    # 
    #     #Display menu with collection name and number of wallpapers for the user to choose from
    #     #e.g. 0 Artistic, 100 Walpapers
    #     temp_coll_list = []
    #     print 'Please type the number of the favorites folder you would like to download now e.g. 1, 2, 3, etc...\n'
    #     for collection in fav_src_dict:
    #         print collection[1][0], ''.join(e for e in collection[0][3:] if e.isalnum()), ", " + collection[1][2] + ' Wallpapers'
    #         temp_coll_list.append(str(collection[1][0]))
    #         
    #     #Code to validate the input of the user
    #     count = 0
    #     val_input = True   
    #     while val_input:
    #         try:
    #             collection_number = raw_input() 
    #             collection_number = int(collection_number)
    #             collection_name = ''.join(e for e in fav_src_dict[collection_number][0][3:] if e.isalnum())
    #             dl_url = fav_src_dict[collection_number][1][1]
    #             #print 'Valid number found. Moving on...'
    #             val_input = False
    #         except ValueError:
    #             print "Please type a valid number"
    #             count +=1
    #             if count ==3:
    #                 print 'Please try again when you learn how to type'
    #                 sys.exit(1)
    #             else:
    #                 continue
    #     dest_dir = os.path.join(os.path.join(dest_dir, user_collection_user['user_title'] ), collection_name)
    #     tools.directory_checker(dest_dir)
    #     
    #     #Prompt for organizing folders by purity
    #     choices = ['False', 'True']
    #     print ('Would you like to organize your images in folders based on purity level?\nOptions: True or False. (default is True)\n') 
    #     dl_to_diff_folders = raw_input()
    #     if dl_to_diff_folders == '':
    #         dl_to_diff_folders = 'True'
    #     del count
    #     count = 0
    #     while dl_to_diff_folders not in choices and count < 2:
    #         print "Please enter True or False without quotes to make your choice."
    #         dl_to_diff_folders = raw_input()
    #         count +=1
    #         if count == 2 and dl_to_diff_folders not in choices:
    #             print "Please try again when you learn how to type"
    #             sys.exit(1)
    #     
    #     #User these variables to populate a config file if it doesn't already exist
    #     search_contents = {}
    #     user_contents = {}
    #     search_contents['dl_user_name'] = user_collection_user['user_title']
    #     search_contents['dl_user_number'] = 'n/a'
    #     search_contents['dl_to_diff_folders'] = dl_to_diff_folders
    #     search_contents['collection_name'] = collection_name
    #     search_contents['start_range'] = '0'
    #     search_contents['max_range'] = '6000'
    #     #Set the max range to the range for the collection folder being downloaded
    #     search_contents['max_range'] = str(fav_src_dict[collection_number][1][2])
    #     search_contents['thpp'] = ""
    #     user_contents ['username'] = user_name
    #     user_contents['password'] = passw
    #     user_contents['destination_directory'] = os.path.abspath(dest_dir)
    #     user_contents['collection_query'] = 'True'
    #     
    #     #If it already exists, read from it and download from there
    #     if os.path.isfile(os.path.join(dest_dir, collection_name + '.ini')):
    #         print '%s exists already, resuming from it. ' %(collection_name+ '.ini')
    #         search_contents, user_contents = tools.load_config(self, dest_dir)
    #     
    #     #Updating the config file if one doesn't exists
    #     search_contents['thpp'] = self.user_settings(self)
    #     
    #     tools.write_config(self, dest_dir, search_contents, user_contents)
    #     
    #     #call to actually begin downloads of the favorites
    #     self.query_generator(dest_dir, '&', dl_url, int(search_contents['start_range']) , int(search_contents['max_range']), dl_to_diff_folders, int(search_contents['thpp']))
    #===========================================================================
    def match_images(self):
        '''This method is used to parse the thumbnail page, then request each image in the query. Once that's done, img src, purity, tag info etc...
        is parsed from the img src page and handed off to be downloaded.'''
        
        num_of_walls = parse.number_of_results()
        if num_of_walls == 'over 9000!':  #new toplist doesn't list number of results, so just set to user's max range
            num_of_walls = int(tools.user_vars['max_range'])
    
        if num_of_walls == "":
            print "No wallpapers found, try a different query"
            sys.exit(1)
        
        #The number of wallpapers is used to limit the matches as well as determine start and stop ranges in this method
        print 'Currently processing matches'
        if int(num_of_walls) > int(tools.user_vars['max_range']):
            print '%s wallpapers found' % num_of_walls
            #print '%s wallpapers found\n%s queued for dl, out of %s' % num_of_walls,  tools.user_vars['max_range'] - tools.user_vars['start_range'],  tools.user_vars['max_range']
        elif (int(tools.user_vars['max_range']) > num_of_walls) and (num_of_walls - int(tools.user_vars['start_range'])) > 0:
            print 'Found %d wallpapers\nDownloading %d wallpapers' % (num_of_walls, num_of_walls - int(tools.user_vars['start_range'])) 
        
        #For each img url, find the source url of that img in it's own html file
        for match in parse.wall_links:
            #print match
            sleep_count = 20
            #while loop used stop matching once the max is reached
            while True and int(tools.user_vars['start_range']) < int(tools.user_vars['max_range']):
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
        
                        if int(tools.user_vars['max_range']) < num_of_walls:
                            print "matched: ",  int(tools.user_vars['start_range']) +1 , '/', int(tools.user_vars['max_range'])
                        else:
                            print "matched: ", int(tools.user_vars['start_range']) +1, '/', num_of_walls
                            
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
                    print "retry attempt %s/%s" %(sleep_count/20, 3)
                    sleep(20)
                    sleep_count += 20
                    if sleep_count >= 60:
                        print "There's a problem with matching this URL, skipping wallpaper"
                        break
                    continue
                break
            print self.img_names_dict
            self.retrieve_images()
            
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
                tools.user_vars['start_range'] = int(tools.user_vars['start_range']) - int(tools.user_vars['thpp'])
            if choice != '' and choice not in self.yes_list:
                print "END OF LINE, TRON"
                sys.exit()
                
        else: print len(self.img_names_dict), " Matches successfully made."
        
        #used for returning the proper number of matches if the number of matches is less than the thumbnails per page
        if len(self.img_names_dict) < int(tools.user_vars['thpp']):
            return (int(tools.user_vars['start_range']) + (int(tools.user_vars['thpp']) - len(self.img_names_dict)))
        else:
            #start number returned that's used for incrementing elsewhere
            return int(tools.user_vars['start_range'])
    def retrieve_images(self):
        """This method is used to retrieve images from a dictionary of wallpapers and urls,
        saves them to your hard drive, and if they already exist skips the download."""
        #If the chosen directory doesn't exist, create it
        dest_dir = tools.destination_directory
        tools.directory_checker(dest_dir)

        #logic is such that if the passed in start number is less than the thumbnails per page, it downlaods the correct # of imgs
        if int(tools.user_vars['start_range']) < int(tools.user_vars['thpp']):
            tools.user_vars['start_range'] -= tools.user_vars['start_range']
        elif int(tools.user_vars['start_range']) >= int(tools.user_vars['start_range']):
            tools.user_vars['start_range'] -= tools.user_vars['thpp']
        
        #Iterate through the loop and download images in the dictionary
        for img in self.img_names_dict:

            #Setting the file name and directory in case of purity download filtering
            purity_dir = os.path.join(dest_dir, (self.img_names_dict[img])[1])
            purity_file = os.path.join(purity_dir, img)
            #Create purity directory if it's needed
            if self.img_names_dict[img][1] in self.purity_list:
                tools.directory_checker(purity_dir)            
                #else if image exists in purity directory, don't move it
                if os.path.isfile(purity_file):
                    print "File %d, %s exists in %s folder, not moving" %(int(tools.user_vars['start_range']) +1, img, self.img_names_dict[img][1])
                #If image exists is in main directory, and dl to diff true, move image to purity folder
                elif os.path.isfile(os.path.join(dest_dir, img)):
                    print "File %d, %s exists, moving to %s folder" %(int(tools.user_vars['start_range']) +1, img, self.img_names_dict[img][1])
                    shutil.move(os.path.join(dest_dir, img), purity_dir)
                #else if image doesn't exist in purity direcotry, download that shit
                elif not os.path.isfile(purity_file):
                    print 'File %d, %s downloading to %s folder' %(int(tools.user_vars['start_range']) +1, img, self.img_names_dict[img][1])
                    sleep_count = 0
                    while True:
                        try:
                            #new url retrieve code
                            #self.opener.open(self.img_names_dict[img][0])
                            print img
                            self.html_from_url_request(url=self.img_names_dict[img][0])
                            print self.temp_file_loc
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
                    print 'File %d, %s exists in %s, not moved' % (int(tools.user_vars['start_range']) +1, img, os.path.basename(dest_dir))
                elif not os.path.isfile(os.path.join(dest_dir, img)):
                    print 'File %d, %s downlaoding to %s folder' %(int(tools.user_vars['start_range']) +1, img, os.path.basename(dest_dir))
                    sleep_count = 0
                    while True:
                        try:
                            print self.img_names_dict[img]
                            self.html_from_url_request(url=self.img_names_dict[img])
                            print self.temp_file_loc
                            shutil.move(self.temp_file_loc, os.path.join(dest_dir, img))
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
            tools.user_vars['match_count'] = int(tools.user_vars['match_count']) + 1
        if self.success_count: print self.success_count, 'successful downloads'
    
        #Image dictionary is cleaned up after each run and re-used for the next series of matches
        print "End of list! Flushing temporary urls..."
        self.img_names_dict.clear()
        return self.success_count
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
        #Should probably merge this into above for ease of parsing. 
        login_data = urllib.urlencode(self.login_vals)
        #http_headers =  {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'referer': 'wallbase.cc http://wallbase.cc/user/adult_confirm/1 '} 
        settings_url = 'http://wallbase.cc/user/settings'
        settings_req = urllib2.Request(settings_url, login_data, self.http_headers)
        settings_resp = urllib2.urlopen(settings_req)
        settings_html = settings_resp.read()
        tools.html_to_file(self, settings_html, self.destination_directory)
        html_file_loc = ('./deleteme.html')
        self.soup = SoupParse.make_soup(self, html_file_loc, clean_html=True)
        os.unlink(html_file_loc)
        for link in self.soup.find_all('input', id="filter_set_thpp"):
            return link.get('value')       
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
        
        #Make sure the destionation directory exists
        tools.directory_checker(tools.user_vars['destination_directory'])
        
        #Build query url from user_vars
        #http://alpha.wallhaven.cc/search?q=anime&categories=111&purity=111&resolutions=1600x900,2560x1600,3840x1080&ratios=16x9&sorting=date_added&order=asc
        while tools.user_vars['start_range'] <= tools.user_vars['max_range']:
            #Adding support for searches first, collectoin come later
            if int(tools.user_vars['start_range'])/32== 0 : start_page = '?page=1' 
            else: start_page = '?page=%s' % str(int(tools.user_vars['start_range'])/int(tools.search_query['thpp']))
            self.query_url = self.wallhaven_search_url + start_page + '&categories=' + tools.search_query['board'] +\
             '&purity=' + tools.search_query['nsfw'] +'&resolutions=' + tools.search_query['res'] + '&ratios=' +\
             tools.search_query['res_opt'] + '&sorting=' + tools.search_query['orderby'] +'&order=' +\
             tools.search_query['orderby_opt'] + '&q=' + tools.search_query['query'].replace(' ', '+').replace('"', '')
            #print self.query_url
            print 'Downloading a search_query'
            #Create soup and parse for images
            #print self.html_from_url_request()
            parse.make_soup(self.html_from_url_request(), True)
            parse.match_imgs()
            self.match_images()
            #parse.find_img_source()
            #print "Deploying ninjas to steal wallpapers"
            #self.retrieve_images()  
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
    def __init__(self, destination_directory=None, user_directory=None, username=None, password=None):
        self.user_directory = user_directory
        self.destination_directory = destination_directory
        self.username = username
        self.password = password
        self.temp_file_loc = ''
        self.wallhaven_search_url = "http://alpha.wallhaven.cc/search"
        self.query_url = ''
        self.login_vals = {'username' : self.username, 'password' :self.password}
        self.http_headers = {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',\
                           'referer': 'http://alpha.wallhaven.cc'} 
        #Global dictionary used to store the source of a wallpaper, it's name, and it's purity
        self.img_names_dict = {}
        self.match_count = 0
        self.success_count = 0
        self.purity_list = ('NSFW','SKETCHY', 'SFW')
        self.purity_bits = ('001', '011', '111')
        self.toplist_dict = {"0": "AllTime", "3m": '3Months', '2m':'2Months', '1m':'1Month', \
                             '2w':'2Weeks', '1w':'1Week', '3d':'3Days', '1d':'1Day'}
        self.yes_list = {'yes', 'y', 'Y', 'Yes', 'YES', 'YEs', 'yeS','yES'}
        #Installing the CookieJar - This will make the urlopener bound to the CookieJar.
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
            
        #Turn new html source into beautiful soup for easy parsing
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
        #Opening an html_file for parsing
        for link in self.soup.find_all('a', href=re.compile('wallhaven.cc/wallpaper/\d+')):
            if link.get('target') == '_blank': 
                self.wall_links.append(link.get('href'))
        return self.wall_links
    def find_img_source(self):
        '''Used to find the src url of a wallpaper from the wallpapers landing page
        ex: http://linktopicture.wallhaven/wallpaper-xxxx.jpg'''
        #####Updated for Wallhaven##############
        #new method for getting the src, name, and purity for a source wallpaper file
        #Use this code to match img sources to the img link
        #########################################        
        img_name = ''
        img_src = ''
        #print self.soup
        for src in self.soup.find_all('img', src=re.compile('\S+wallhaven\-\d+.\w{,4}')):
            print 'image source ' +'http:' + src.get('src')
            if src.get('id') == 'wallpaper': img_src = 'http:' + src.get('src')
            s = re.search('.*/wallhaven\-\d+.\w{,4}', img_src)
            if s: img_name = re.search('\w+\-\d+.\w{,4}', img_src)
            #print img_name.group(0)

        purity = self.soup.find_all('input')
        for p in purity:
            if p.get('name') == 'purity' and p.get('checked') == 'checked':
                purity_v = p.get('id').upper()
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
        self.user_directory = '.'
        self.soup = ''
        self.src_dict = {} 
        self.wall_links = []
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
            self.destination_directory = '.'
            self.html_file = '.'
            self.search_query = {}
            self.user_vars = {}
            self.config_file = ''
            self.config_file =  os.path.join(self.destination_directory, os.path.basename(self.destination_directory) + '.ini')
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
#ws_sql.create_db()
if __name__ == "__main__":
    '''If the scripts initiates itself, run the main method
    this prevent the main from being called if this module is 
    imported into another script'''
    #main()
    scrape = WallScraper()
    tools = WallTools()
    parse = SoupParse()
    tools.config_file = './Custom_Search.ini'
    scrape.new_download_generator()
    #===========================================================================
    # tools.load_config(r'C:\Users\kyle\workspace\wall_scraper\test\config.ini')
    # #scrape.user_login(tools.user_vars['username'], tools.user_vars['password'])
    # tools.directory_checker(tools.user_vars['destination_directory'])
    # if int(tools.user_vars['start_range'])/32== 0 : start_page = '?page=1' 
    # else: start_page = '?page=%s' % str(int(tools.user_vars['start_range'])/int(tools.search_query['thpp']))
    # query_url = scrape.wallhaven_search_url + start_page + '&categories=' + tools.search_query['board'] +\
    # '&purity=' + tools.search_query['nsfw'] +'&resolutions=' + tools.search_query['res'] + '&ratios=' +\
    # tools.search_query['res_opt'] + '&sorting=' + tools.search_query['orderby'] +'&order=' +\
    # tools.search_query['orderby_opt'] + '&q=' + tools.search_query['query'].replace(' ', '+').replace('"', '')
    # print query_url
    # 
    #===========================================================================
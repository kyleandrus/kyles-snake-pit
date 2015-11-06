"""
Created on Aug 1, 2012

@author: kandrus
The purpose of this script is to allow a user to automatically download
all wallpapers that match a user specified query, or wallpapers that are 
contained within their custom favorites collections from the website http://alpha.wallhaven.cc
The downloading of favorites, or nsfw images is restricted to registered users.
"""
import ConfigParser
import cookielib
import os
import re
import shutil
import sys
import urllib
import urllib2
import Queue
import threading
import random
try:
    from bs4 import BeautifulSoup
except ImportError:
    print 'You need to download beautfulsoup for this script to work\n'
    'e.g. from C:\Python27\Scripts\ directory at the cmd line, run c:\pip install beautifulsoup4'
    sys.exit()

# TODO Merge the SoupParse and WallTools into the WallScraper class and reconfigure the variables. Could save a lines


class WallScraper(object):
    def match_counter(self):
        if self.num_of_walls == "":
            print "No wallpapers found, try a different query"
            sys.exit(1)
        # trim the number of images from the dictionary to match number of downloads left in queue
        if (self.match_count + int(self.thpp)) >= self.max_range:
            trim = int(self.thpp) - self.max_range
            # print len(self.img_names_dict)
            # print self.match_count, self.thpp, self.max_range, len(self.img_names_dict), trim
            n = 1
            while n <= trim:
                for k in sorted(self.img_names_dict.iterkeys(), reverse=True):
                    if n <= trim:
                        self.img_names_dict.pop(k)
                    n += 1
        if len(self.img_names_dict) != 0:
            self.start_range += len(self.img_names_dict)
            self.match_count = self.start_range
        else:
            self.main_loop = False  # Exit main loop since there are no downlaods to be had
        print "Matching new images...\n", len(self.img_names_dict), "Matches Successfully made."

    def img_threads(self, q, img_names_dict, img_name):
        q.put_nowait(self.retrieve_images(img_names_dict, img_name))

    def check_file_ext(self, file_loc, ext_list):
        """Look for a file with the extension jpg, if not found, cycle through the extension list and return the
        file that matches the extension of the file."""
        if not os.path.isfile(file_loc):
            for ext in ext_list:
                if os.path.isfile(file_loc.replace('jpg', ext)):
                    # print 'Checking file  %s' % file_loc.replace('jpg', ext)
                    self.file_ext = ext
                    return ext
        else:
            self.file_ext = ext_list[0]
            return ext_list[0]

    def retrieve_images(self, img_names_dict, img_name):
        """call this from the dictionary using img_names_dict and img_names_dict[img]
        """
        if tools.user_vars['dl_to_diff_folders'] == 'True':
            purity_dir = os.path.join(self.query_dir_name, img_names_dict[img_name][1])
            img_url = img_names_dict[img_name][0]
        else:
            purity_dir = os.path.join(self.query_dir_name)
            img_url = img_names_dict[img_name][0]
        purity_file = os.path.join(purity_dir, img_name)
        tools.directory_checker(purity_dir)
        ext_list = ['jpg', 'png', 'PNG', 'JPG', 'JPEG', 'jpeg']
        file_number = ((self.page_number - 1) * int(self.thpp) + img_names_dict.keys().index(img_name) % int(self.thpp) + 1)
        file_name = (img_name.replace('jpg', self.file_ext))
        if tools.user_vars['dl_to_diff_folders'] == 'True':
            if self.check_file_ext(purity_file, ext_list):
                self.already_exist += 1
                print "File %-5d %-23s exists in %s folder, not moving" % (file_number, file_name, os.path.basename(purity_dir))
            elif self.check_file_ext(os.path.join(self.query_dir_name, img_name), ext_list):
                self.already_exist += 1
                print "File %-5d %-23s exists, moving to %s folder" % (file_number, file_name, os.path.basename(purity_dir))
                shutil.move(os.path.join(self.query_dir_name, img_name.replace('jpg', self.file_ext)), purity_file.replace('jpg', self.file_ext))
        elif tools.user_vars['dl_to_diff_folders'] == 'False':
            if self.check_file_ext(os.path.join(self.query_dir_name, img_name), ext_list):
                self.already_exist += 1
                print 'File %-5d %-23s exists in %s, not moved' % (file_number, file_name, os.path.basename(purity_dir))
        if not self.check_file_ext(purity_file, ext_list):
            sleep_count = 0
            error_count = 0
            while True:
                for ext in ext_list:
                    try:
                        img_url = img_url.replace('jpg', ext)
                        self.html_from_url_request(url=img_url)
                        file_name = file_name[:-4] + '.' + ext
                        print 'File %-5d %-23s downloading to %s folder' % (file_number, file_name, os.path.basename(purity_dir))
                        shutil.move(self.temp_file_loc, purity_file.replace('jpg', ext))
                        self.success_count += 1
                        break
                    except IOError as detail:
                        if '404' in detail:
                            error_count += 1
                            if error_count == 6:
                                print '\t', detail, '\n\tNo wallpaper image found, check your dictionary parsing'
                                break
                            continue
                        if 'timeout' in detail:
                            if sleep_count == 3:
                                sleep_count += 1
                                print '\t', detail, '\n\tURL unresponsive, skipping file'
                                break
                            continue
                    continue
                break

    def user_login(self, username, password):
        """Logs the user in and saves the users session in a cookie for use when making web requests
        Also uses custom headers to pass to the web server to allow image downloads. If the user
        doesn't login, they will be unable to download private collections"""
        login_vals = {'username': username, 'password': password}
        login_url = 'http://alpha.wallhaven.cc/auth/login'
        login_data = urllib.urlencode(login_vals)
        http_headers = {'User-agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
                        'referer': 'http://alpha.wallhaven.cc'}
        req = urllib2.Request(login_url, login_data, http_headers)
        resp = self.opener.open(req)
        login_html = resp.read()
        # Need to update for WallHaven
        find_logged_in = re.search('logged\-in', login_html)
        if find_logged_in.group():
            print 'User %s successfully logged in!' % username
            print 'Saving cookie'
            # Save cookie with login info
            self.cj.save(self.COOKIEFILE)
        else:
            print 'Login failed for %s\nCheck for csrf/username/password problems' % username
        print 'User %s logged in' % username

    def user_settings(self):
        """Used to parse the users setting from the Wallhaven site. Useful for making 
        queries based on the users preferences"""
        # Url request for user settings page, then make soup and delete html file
        self.html_from_url_request(url=self.settings_url)
        soup = parse.make_soup(self.temp_file_loc, True)
        # Swim through soup and find thpp setting
        for s in soup.find_all('select', id='thumbsPer'):
            for i in s.select('option'):
                if i.get('selected') == 'selected':
                    self.thpp = i.get_text('value').strip()
                    print \
                        'Successfully set thumbnails/page to user setting of %s\n' \
                        'Login to wallhaven to change your thpp setting. This \n' \
                        'determines the number of wallpapers you download at a time.\n' \
                        'http://alpha.wallhaven.cc/settings/browsing' \
                        % self.thpp
                    return self.thpp

    def build_query(self):
        # check config value if query existed, and set match_count to pick up where it left off. Only do this once per scrape.
        if self.run_once:
            self.run_once = False
            self.start_range = int(tools.user_vars['start_range'])
            self.max_range = int(tools.user_vars['max_range'])
            if self.start_range != 0:
                self.match_count = self.start_range
        if 'toplist' in tools.search_query['query']:
            self.query_string = ''
        else:
            self.query_string = tools.search_query['query']
        self.page_number = (self.match_count / int(self.thpp) + 1)
        self.query_url = self.wallhaven_search_url + '?&page=' + str(self.page_number) + '&categories=' + \
            tools.search_query['board'] + \
            '&purity=' + tools.search_query['nsfw'] + '&resolutions=' + tools.search_query[
            'res'] + '&ratios=' + \
            tools.search_query['res_opt'] + '&sorting=' + tools.search_query['orderby'] + '&order=' + \
            tools.search_query['orderby_opt'] + '&q=' + self.query_string.replace(' ', '%20').strip()
        return self.query_url

    def run_check(self):
        # print ' thpp', self.thpp, 'success', self.success_count, 'already down', self.already_exist, 'numofwall',  self.num_of_walls, 'start range', self.start_range, 'max range', self.max_range
        if int(self.num_of_walls) and int(self.max_range):
            if (int(self.success_count) + int(self.already_exist)) >= int(self.num_of_walls):
                self.main_loop = False
            elif (int(self.success_count) + int(self.already_exist)) >= int(self.max_range):
                self.main_loop = False
            elif int(self.start_range) >= int(self.num_of_walls):
                self.main_loop = False
            elif int(self.start_range) >= int(self.max_range):
                self.main_loop = False
            elif int(self.thpp) >= int(self.num_of_walls):
                if int(self.start_range) >= int(self.thpp) - (self.success_count + self.already_exist):
                    self.main_loop = False

    def set_query_config_file_name(self):
        # If the chosen directory doesn't exist, create it
        tools.directory_checker(tools.downloads_directory)
        # Setting the file name and directory in case of purity download filtering
        if tools.search_query['query']:
            self.clean_query_name = tools.search_query['query'].replace(' ', '_').replace('"', '').strip().title()
        self.query_dir_name = os.path.join(tools.downloads_directory, self.clean_query_name)
        self.query_config_file = os.path.abspath(os.path.join(self.query_dir_name, self.clean_query_name + '.ini'))

    def html_from_url_request(self, search_req=None, url=None):
        if search_req is None and url is None:
            # print 'if entered'
            search_req = urllib2.Request(self.query_url, headers=self.http_headers)
        elif url:
            search_req = urllib2.Request(url, headers=self.http_headers)
        url_html = self.opener.open(search_req).read()
        self.temp_file_loc = os.path.join(os.path.abspath('.'), '.temp_' + str(random.randint(10000, 20000)))
        html_to_file(url_html, os.path.abspath('.'), temp_file_loc=self.temp_file_loc)
        return self.temp_file_loc

    def download_loop(self, dest_dir, config_file):
        """Check the dest directory, if not default, create missing dir
        then start scraping the thumbnail page for image"""
        # Load config using tools class - set search query and user variables
        # to the settings in the file.
        # I'm really over utilizing class variables. There's no need to use so many tools instance variables. need to clean up.
        self.user_directory = dest_dir
        self.query_config_file = config_file
        tools.search_query, tools.user_vars = tools.load_config(
            os.path.join(os.path.abspath(self.user_directory), config_file))
        if tools.search_query['nsfw'][2] == '1' and \
                (tools.user_vars['username'] == '' or tools.user_vars['password'] == ''):
            print 'type your username and press enter'
            tools.user_vars['username'] = raw_input()
            print 'type your password and press enter'
            tools.user_vars['password'] = raw_input()
        elif tools.search_query['nsfw'][2] == '1' and \
                (tools.user_vars['username'] != '' and tools.user_vars['password'] != ''):
            self.user_login(tools.user_vars['username'], tools.user_vars['password'])
        self.user_settings()
        # Make sure the destination directory exists
        tools.directory_checker(tools.user_vars['destination_directory'])
        self.destination_directory = tools.user_vars['destination_directory']
        tools.downloads_directory = tools.user_vars['destination_directory']
        scrape.set_query_config_file_name()
        # TODO Add the ability to overwrite an excising query ini file with new information from the custom search
        if os.path.exists(self.query_config_file):
            print 'Pre-existing query found, picking up where it left off'
            tools.search_query, tools.user_vars = tools.load_config(self.query_config_file)
        self.start_range = tools.user_vars['start_range']
        self.max_range = tools.user_vars['max_range']
        # get number of walls from query outside of loop to prevent over matching
        self.build_query()
        parse.make_soup(self.html_from_url_request(), True)
        self.num_of_walls = parse.number_of_results()
        self.run_check()
        # Loop for retrieving images
        while self.main_loop:
            try:
                # Generate urls from thumbnail thumbnail match
                self.build_query()
                parse.make_soup(self.html_from_url_request(), True)
                self.run_check()
                # Check for existence of query in download directory, if exists, load it
                if self.num_of_walls <= self.max_range:
                    print 'Number of wallpapers is lower than max range, downloading %s wallpapers' % str(
                        self.num_of_walls)
                elif self.max_range >= self.num_of_walls:
                    print 'Number of wallpapers is higher than max range, limiting download to %s wallpapers' % str(
                        self.max_range)
                # Bail out of loop if you've reached max number of downloads
                tools.thpp = self.thpp
                self.img_names_dict, self.match_count = parse.match_img_info()
                self.match_counter()
                q = Queue.Queue()
                print 'Downloading Page #%s' % str(self.page_number)
                for img in self.img_names_dict:
                    t = threading.Thread(target=self.img_threads(q, self.img_names_dict, img))
                    t.daemon = True
                    t.start()
                    q.get_nowait()
                if self.success_count or self.already_exist:
                    print self.success_count, 'successful downloads, %d files already existed' % self.already_exist
                self.img_names_dict.clear()
                tools.user_vars['start_range'] = self.start_range
                tools.user_vars['max_range'] = self.max_range
                tools.write_config(self.query_config_file, tools.search_query, tools.user_vars)
                if os.path.exists(self.temp_file_loc):
                    os.unlink(self.temp_file_loc)
                self.run_check()
            except IOError as detail:
                print detail, 'occured. Fix your shit!'
        else:
            print 'All wallpapers downloaded or already exist'
            print 'Would you like to reset the start range in the configuration file and start the downloads again?[Yes]'
            # code for allowing a user to reset the download counter and start over, so they don't have to do it manually
            choice = raw_input()
            if choice == '' or choice in self.yes_list:
                tools.user_vars['start_range'] = 0
                tools.write_config(self.query_config_file, tools.search_query, tools.user_vars)
                self.success_count = 0
                self.already_exist = 0
                self.start_range = 0
                self.match_count = 0
                self.start_range = 0
                self.main_loop = True
                self.run_once = True
                self.download_loop(os.path.abspath(self.user_directory), self.query_config_file)
            if choice != '' and choice not in self.yes_list:
                print "END OF LINE, TRON"
                if os.path.exists(self.temp_file_loc):
                    os.unlink(self.temp_file_loc)
                    sys.exit()

    def __init__(self):
        super(WallScraper, self).__init__()
        self.clean_query_name = 'Toplist'
        self.main_loop = True
        self.user_directory = ''
        self.destination_directory = ''
        self.username = ''
        self.password = ''
        self.temp_file_loc = ''
        self.thpp = 24
        self.page_number = 0
        self.start_range = 0
        self.max_range = 0
        self.file_ext = 'jpg'
        self.run_once = True
        # Settings related to logging in to the wallhaven servers, header data and password etc...
        self.wallhaven_search_url = "http://alpha.wallhaven.cc/search"
        self.settings_url = 'http://alpha.wallhaven.cc/settings/browsing'
        self.query_dir_name = ''
        self.query_config_file = ''
        self.query_url = ''
        self.query_string = ''
        self.http_headers = {'User-agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
                             'referer': 'http://alpha.wallhaven.cc'}
        # Global dictionary used to store the source of a wallpaper, it's name, and it's purity
        # As well as other dictionaries used for comparisons sake
        self.img_names_dict = {}
        self.match_count = 0
        self.success_count = 0
        self.already_exist = 0
        self.num_of_walls = 0
        self.yes_list = {'yes', 'y', 'Y', 'Yes', 'YES', 'YEs', 'yeS', 'yES'}
        # Installing the CookieJar - This will make the urlopener bound to the CookieJar.
        # This allows each urlopen to use the cookies for the user session, essential for accessing NSFW images
        self.COOKIEFILE = 'cookies.lwp'
        self.urlopen = urllib2.urlopen
        self.Request = urllib2.Request
        self.cj = cookielib.LWPCookieJar()
        self.cj.save(self.COOKIEFILE)
        if self.cj is not None:
            if os.path.isfile(self.COOKIEFILE):
                # If there is already a cookoie file, load from it
                self.cj.load(self.COOKIEFILE)
            if cookielib is not None:
                # This installs the cookie Jar into the opener for fetching URLs
                self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
                urllib2.install_opener(self.opener)


class SoupParse(object):
    def make_soup(self, html_file, clean_html=False):
        """This method is used to make prettified soup out of a users html file. This soup
        can then be used to parse using the other parse methods. If an html file is
        particurlary dirty, you can clean optionally clean it.
        """
        # Read wallpaper into string for parsing
        a = open(html_file).read()
        # Clean html if requested (necessary for Wallhaven)
        if clean_html:
            # Find all Span class tags in html, plus junk tags for css
            span_class = re.findall('<*span class=\"\S+\">', a)
            # print span_class
            # Remove span class markers and replace unicode with to fix html
            for span in span_class:
                a = a.replace(span, '')
            a = a.replace('</span>', '')
            a = a.replace('&lt;', '<')
            a = a.replace('&gt;', '>')
            a = a.replace('&amp;', '&')
        # Turn new html source into beautiful soup for easy parsing, html5lib if html.parser gives you trouble
        self.soup = BeautifulSoup(BeautifulSoup(a, 'html.parser').prettify(), 'html.parser')
        os.unlink(html_file)
        return self.soup

    def match_img_info(self):
        """This method should replace both the find_img_source and match_img methods"""
        # self.make_soup('wallpaper_thumbs.html', clean_html=True)
        # print self.soup
        proper_link = ''
        name_strings = []
        source_links = []
        purity_tags = []
        img_info_dict = {}
        # Obtaining the source link of the image
        for s in self.soup.find_all('img'):
            # print s
            if 'None' not in str(s.get('data-src')).replace(' ', ''):
                proper_link = str(s.get('data-src')).replace('thumb/small/th', 'full/wallhaven')
            source_links.append(proper_link)
            name_strings.append(proper_link.split('/')[-1])
        # Obtaining the purity of the image
        for li in self.soup.find_all('figure'):
            purity_tags.append(li.get('class')[1].replace('thumb-', '').upper())
        n = 0
        while n < len(name_strings):
            if source_links[n] == '':
                source_links.pop(n)
            if name_strings[n] == '':
                name_strings.pop(n)
            img_info_dict[name_strings[n]] = source_links[n], purity_tags[n]
            n += 1
        return img_info_dict, len(img_info_dict)

    def number_of_results(self):
        """Find the number of wallpapers available for downloading, useful for limiting 
        your downloads"""
        find_num = self.soup.find('h1')
        active_walls = re.search(r'(\d+,*\d*,*\d*,*\d*)(\sWallpapers\sfound)', str(find_num))
        self.num_of_walls = active_walls.group(1).replace(',', '')
        print self.num_of_walls, 'wallpapers found'
        return self.num_of_walls

    def find_img_tags(self, soup):
        """Used to parse tag data from wallpapers. """
        # Need to add parsing for tag matching in the dl_config folder
        for link in self.soup.find_all('a', class_='tagname'):
            tag = re.search('/tag/\d+', link.get('href'))
            for s in link.contents:
                print s.replace('\n', '').strip()
                self.file_tags[link[0]] = tag.group().replace('/tag/', '')
        return self.file_tags

    def __init__(self):
        super(SoupParse, self).__init__()
        self.html_file = ''
        self.thpp = 24
        self.soup = ''
        self.img_name = ''
        self.num_of_walls = ''
        self.file_tags = {}


class WallTools(object):
    """ex: WallTools(self, user_directory=None, destination_directory=None)

    This class is used to hold tools related to files and configuration
    data related to WallScraper
    If no directories are passed, default it to assume the directory the script was run from    """

    @staticmethod
    def directory_checker(destination_directory=None):
        """
        This method will check for the existence of a directory, and if
        it doesn't exist, it will create the directory. 
        """
        # Essentially do nothing if the path exists
        if os.path.exists(os.path.abspath(destination_directory)):
            return destination_directory
        else:  # create the path for the user and tell the user the name of the path
            print '%s | didn\'t exist, creating...' % (os.path.abspath(destination_directory))
            os.makedirs(os.path.join(destination_directory))

    def load_config(self, configuration_file):
        """
        Takes as input the location of a *.ini file, and returns two tuples
        one for search query data, one for user data
        """
        print 'Loading settings from %s' % (os.path.abspath(configuration_file))
        self.config_file = configuration_file
        f = open(self.config_file, "rb")
        self.c.readfp(f)
        for option in self.c.options("Search Query"):
            self.search_query[option] = self.c.get("Search Query", option)
        for option in self.c.options("User Options"):
            self.user_vars[option] = self.c.get("User Options", option)
        # Return the variables set from the config file to the dl_search method
        f.close()
        return self.search_query, self.user_vars

    def write_config(self, config_file, search_query=None, user_vars=None):
        """
        Takes as input a search query (tuple), and user options (tuple)
        Then output a *.ini file matching the name of the configuration_file string. 
        """
        # if the config file doesn't exist, create one from the passed in variables, otherwise, update it like normal
        if not os.path.isfile(config_file):
            # Set the variables in the search_query and user_vars to match the updated ones that were passed in
            if not self.c.has_section('Search Query'):
                self.c.add_section("Search Query")
            if not self.c.has_section('User Options'):
                self.c.add_section("User Options")
            for query in self.search_query:
                self.c.set("Search Query", query, self.search_query[query])
            for option in self.user_vars:
                self.c.set("User Options", option, self.user_vars[option])
            f = open(config_file, "w")
            self.c.write(f)
            f.close()
            # Update the config file with the latest variables
        f = open(os.path.abspath(config_file), "rb")
        self.c.readfp(f)
        # Set the options to match the fields in the query and the changes being written in with this method
        for query in self.search_query:
            self.c.set("Search Query", query, self.search_query[query])
        for option in self.user_vars:
            self.c.set("User Options", option, self.user_vars[option])
        f = open(config_file, "w")
        self.c.write(f)
        f.close()
        print "Config file updated"

    def __init__(self):
        super(WallTools, self).__init__()
        self.user_directory = '.'
        self.downloads_directory = '.'
        self.html_file = '.'
        self.config_file = ''
        self.c = ConfigParser.ConfigParser()
        self.search_query = ({'query': '', 'board': '111', 'nsfw': '110', 'res': '0', 'res_opt': 'eqeq',
                              'aspect': '0', 'orderby': 'desc', 'orderby_opt': 'views', 'thpp': '24',
                              'toplist_time': ''})
        self.user_vars = ({'destination_directory': '.', 'username': '', 'password': '', 'start_range': '0',
                           'max_range': '2000', 'dl_to_diff_folders': 'true', })


def html_to_file(html_file, destination_directory, temp_file_loc=None):
    # This code will output the html of the search page, needs fed a req.open()
    tools.directory_checker(destination_directory)
    if not temp_file_loc:
        temp_file_loc = '.temp'
    f = open(os.path.join(destination_directory, temp_file_loc), "wb")
    f.writelines(html_file)
    # print "HTML file written to:\n", os.path.abspath(os.path.join(dest_dir, filename))
    f.close()


def main():
    """This function is used to call the rest of the methods from the command line"""
    # Make a list of command line arguments, omitting the [0] element which is the script itself.
    args = sys.argv[1:]
    # If no arguments are given, print proper usage and call the search method
    if not args:
        print "\nProper usage:\n\n\t[Wallscraper.py --config (directory where the CustomSearch_ini is located," \
              " or where you wish to create one. Leave blank for default e.g. c:\\Wallbase\\)]"
    if len(args) == 0:
        print "\n\nYou must enter an argument to proceed!"
    # ===========================================================================
    # elif args[0] == '--favorites':
    #     try:
    #         fdest_dir = args[1]
    #     except IndexError:
    #         fdest_dir = ''
    #     scrape.favorites_download(fdest_dir)
    #     del args[0:0]
    # ===========================================================================
    elif args[0] == '--config':
        try:
            config_dir = args[1].replace(args[1].split('\\')[-1], '')
            config_file = args[1].split('\\')[-1]
            scrape.download_loop(config_dir, config_file)
        except IndexError:
            config_dir = '.'
            config_file = 'Custom_Search.ini'
            print 'Using default directory of', os.path.abspath(os.path.join(config_dir, config_file))
            scrape.download_loop(config_dir, config_file)


if __name__ == "__main__":
    """If the scripts initiates itself, run the main method
    this prevent the main from being called if this module is 
    imported into another script"""
    scrape = WallScraper()
    tools = WallTools()
    parse = SoupParse()
    main()

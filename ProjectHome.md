This is where I will be hosting all the different things I'll be trying with python.

The main project on this page is currently my Wallbase Wallpaper Scraper. The "Wallscraper" is a batch download tool written in python, it's used to create custom queries and automatically download any image files that match the query from the wallpaper website Wallbase.cc.

_**Wallscraper has numerous features** and is continually growing..._

  * **Favorites Folder and User Collections Downloading** All you need is a wallbase.cc username and password and you can download all of the pictures in your hand chosen collections directly to your hard drive. You are also able to search for a user of your choice, from there you are presented with a list of that user's collections, at that point you can choose to download whichever of that users collections that you wish. If you do not put in a different users name for the favorites download, you will automatically be presented with a list of your personal favorites folders to download from.

  * **Bestof and Toplist downloads!** By putting in a corresponding timeframe into the CustomSearch configuration file, you are able to download the global toplist of wallpapers from wallbase. You can change all of the criteria for the toplist by specifying your options in the Custom\_Search file.

  * **Configuration File Downloading** This file allows a user to specify all the options of a search query and download them automatically. A template CustomSearch is provided to make understanding your options more simple and allow you to better filter your search results. If you start the wallscraper and don't have the ini file in the same directory as the script, a default one will be created for you, once you fill that in, you're off to the races!

  * **Purity Level File Sorting** If the user so wishes, when images are downloaded they can be automatically sorted into folders based on the purity level of that particular image. If the user has previously downloaded images into a directory and they are not sorted, upon running the query a second time with sorting turned on, the images will be moved into the appropriate directories automatically

  * **Automatic Download Resume** Wallscraper will keep track of your progress as you download your queries, so if you're downloading a large query and need to stop the process for some reason, it will automatically resume where it left off before it was closed.


  * **Cross Platform Support** Since Wallscraper is written in Python 2.7.3, it is cross platform compliant and should function identically on Linux, cygwin, and Windows environments. All you need installed is the Python 2.7.3 interpreter, the BeautifulSoup4 libraries, and you should be able to use Wallscraper
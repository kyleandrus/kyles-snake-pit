'''
Created on Jan 27, 2013
SQLite database connector for WallScraper

@author: kyle
'''
import sys
import os
import sqlite3 as lite
import subprocess


def create_db():
    
        
    #connect to the database
    con = lite.connect('ws.db')
    
    #code to create tables
    with con:
        cur = con.cursor()
        print "Populating database tables..."
        
        #Populate tables with proper columns for data
        cur.execute("CREATE TABLE Images\
            (id INTEGER PRIMARY KEY, img_name TEXT, img_src TEXT, img_purity TEXT)")
        
        cur.execute("CREATE TABLE Queries\
            (id INTEGER PRIMARY KEY, query_name TEXT, query_total_results INT, \
            query_previous_start INT, query_max_run INT)")
        
        cur.execute("CREATE TABLE Tags\
            (id INTEGER PRIMARY KEY, img_name TEXT, tag_name TEXT, tag_text TEXT)")
            
def clean_db():
    '''This function will be used to clean the tables as specified by the user'''
    con = lite.connect('ws.db')
    with con:
        cur = con.cursor()
        cur.executescript("""
        DROP TABLE IF EXISTS Images;
        DROP TABLE IF EXISTS Queries;
        DROP TABLE IF EXISTS Tags;
        """)
    print 'Tables cleared'
    
def query_db():
    pass

def insert_wall_to_db(name, src, purity, tags):
    '''This function will take the image source information and insert the entries into the database'''
    #Create connector for sqlite database
    con = lite.connect('ws.db')
    with con:
        cur = con.cursor() 
    
        #turn wallpaper data into a list for injection
        wall_list = []
        wall_list.append(name)
        wall_list.append(src)
        wall_list.append(purity)
        print "%s\t |added to DB" % (name)
        #Insert wallpaper data into Images table
        cur.executemany('insert into Images (img_name, img_src, img_purity) values (?,?,?)', (wall_list,))
        
        #Verbose output of queries
        #for row in cur.execute("select * from Images"):
        #       print'database row', row    
        
        #Create list out of tag data and insert into Tag table with the originating image name to tie it together
        for tag in tags:
            tags_list = []
            tags_list.append(name)
            tags_list.append(tag)
            tags_list.append(tags[tag])
            cur.executemany('insert into Tags (img_name, tag_name, tag_text) values (?,?,?)', (tags_list,))
        
        #Verbose output
        #for row in cur.execute("select * from Tags"):
        #    print 'tags row', row
    
            

def check_db(name, src, purity):
    '''use this function to check whether the image exists in the database or not'''
    skip = False
    #Create connector for sqlite database
    con = lite.connect('ws.db')
    with con:
        cur = con.cursor() 
        for row in cur.execute('select * from Images where img_name=(?)', (name,)):
            if row:
                print '%s \t |already in DB' % (row[1])
                skip = True
                return skip
            else:
                return

###Test data###
#img_tags = {}
#img_tags[0] = 'sexy', 'tag:12345'
#img_tags[1]=  'nude', 'tag:15432'
#img_tags[2] = 'textbook', 'school'
#clean_db()
#create_db()
#insert_wall_to_db('wallpaper-123.jpg', 'http://testurl.jpg','NSFW', img_tags)

        
    
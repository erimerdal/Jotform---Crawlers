import urllib.request
import http.client
from bs4 import BeautifulSoup
import csv
import json
import socket
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import pandas as pd
import pymysql
import time
import cProfile
import sys
import argparse
import threading
import ssl
import os.path

def is_wordpress_tags(url):
    f = open("errors.txt","a+")
    # Return type: tuple as
    # (integers for specific error code or success code, themes if site is created by wordpress)
    keywords = ['wp-content','wp-includes']
    try:
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')] # Set search agent
        response = opener.open(url,timeout=60) # Timeout after 60 seconds

        html = response.read()
        soup = BeautifulSoup(html, 'html.parser', from_encoding = "iso-8859-1")
        themes = []

        # Traverse img/src, script/src or linl/href to check if keywords exist
        # which are the Most common places that these tags exist.
        notFound = True
        # try searching for 'wordpress' in whole html

        try:
            if 'wordpress' in html.decode("utf-8").lower():
                notFound = False
                # Try to find wordpress theme here
                themes = find_theme(html,url)
        except UnicodeDecodeError:
            print("Decoding failed of url: ", url)
            pass

        if notFound:
            for classes in soup.find_all('img'):
                flag = False
                if classes.get('src') is not None:
                    for key in keywords:
                        if key in classes.get('src'):
                            flag = True
                            notFound = False
                            # Try to find wordpress theme here
                            themes = find_theme(html,url)
                            break
                if flag:
                    break

        # could not find anything that proves website is created by wordpress.
        """
        Scheme of the database table to be created
        col 1              / col 2 / col 3 / col 4
        id (primary key/varchar)   /  url (varchar) / is_wp (integer) / themes (list,varchar)
        is_wp -> 0 : not wordpress
              -> 1 : wordpress
              -> 2 : unavailable link
              -> 3 : broken link
              -> 4 : http.client.BadStatusLine
              -> 5 : socket.error
              -> 6 : http.client.mysql.connector.errors.InterfaceError: 2003: Can't connect to MySQL server on 'localhost:3306' (61 Connection refused)HTTPException
              -> 7 : content too short error.
              -> -1 : timeout
        """
        if notFound:
            return (0,None,None,None)
        return (1,themes)
    except urllib.error.HTTPError as http_err:
        write_into = "url: " +url+ "In URL: HTTPError has occured, continuing.." + str(http_err) + "\n"
        f.write(write_into)
        print(write_into)
        return (2,None)
    except urllib.error.URLError as url_err:
        write_into = "url: " +url+ "In URL: URLError has occured, continuing.." + str(url_err) + "\n"
        f.write(write_into)
        print(write_into)
        return (3,None)
    except (http.client.BadStatusLine,http.client.HTTPException) as http_exp: # Subclass of HTTPException
        write_into = "url: " +url+ "In URL: BadStatusLine has occured, continuing.." + str(http_exp) + "\n"
        f.write(write_into)
        print(write_into)
        return (4,None)
    except (socket.error,socket.herror,socket.gaierror,socket.timeout) as socket_err:
        write_into = "url: " +url+ "In URL: %s Socket Error has occured, continuing.." + str(socket_err) + "\n"
        f.write(write_into)
        print(write_into)
        return (5,None)
    except urllib.error.ContentTooShortError as content_err:
        write_into = "url: " +url+ "In URL: ContentTooShortError has occured, continuing.." + str(content_err) + "\n"
        f.write(write_into)
        print(write_into)
        return(-1,None)



def find_theme(html,url):
    f = open("errors.txt","a+")
    soup = BeautifulSoup(html, 'html.parser')
    theme_url = ""
    theme_info = {}
    theme_names = []
    theme_uris = []
    authors = []
    author_uris = []

    # Traverse through tags to find the style.css?
    for classes in soup.find_all('link'):
        if classes.get('href') is not None:
            if "style.css?" in classes.get('href'):
                theme_url = str(classes.get('href'))
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-Agent', 'Mozilla/5.0')]

                try:
                    response = opener.open(theme_url,timeout=60)
                except ValueError:
                    # Fix the link and try again
                    # Extract the beautiful part of URL
                    http_prefix = url[:8]
                    domain_name = (url[8:].split('/'))[0]
                    theme_url = http_prefix + domain_name + theme_url
                    try:
                        response = opener.open(theme_url,timeout=60)
                    except ValueError as value_err:
                        write_into = "url: " +url+ " ValueError occured finding theme, " + str(value_err) + "\n"
                        f.write(write_into)
                        print(write_into)
                        pass
                    except (urllib.error.HTTPError,urllib.error.URLError,urllib.error.ContentTooShortError) as http_err:
                        write_into = "url: " +url+ " Urllib error occured finding theme, " + str(http_err) + "\n"
                        f.write(write_into)
                        print(write_into)
                        pass
                    except (http.client.BadStatusLine,http.client.HTTPException) as http_exp: # BadStatusLine is a Subclass of HTTPException
                        write_into = "url: " +url+ " HTTP.Client error occured finding theme, " + str(http_exp) + "\n"
                        f.write(write_into)
                        print(write_into)
                        pass
                    except (socket.error,socket.herror,socket.gaierror,socket.timeout) as socket_err:
                        write_into = "url: " +url+ " Socket Error occured finding theme, " + str(value_err) + "\n"
                        f.write(write_into)
                        print(write_into)
                        pass
                except (urllib.error.HTTPError,urllib.error.URLError,urllib.error.ContentTooShortError) as http_err:
                    write_into = "url: " +url+ "Urllib error occured finding theme, " + str(http_err) + "\n"
                    f.write(write_into)
                    print(write_into)
                    pass
                except (http.client.BadStatusLine,http.client.HTTPException) as http_exp: # BadStatusLine is a Subclass of HTTPException
                    write_into = "url: " +url+ " HTTP.Client error occured finding theme, " + str(http_exp) + "\n"
                    f.write(write_into)
                    print(write_into)
                    pass
                except (socket.error,socket.herror,socket.gaierror,socket.timeout) as socket_err:
                    write_into = "url: " +url+ " Socket Error occured finding theme, " + str(value_err) + "\n"
                    f.write(write_into)
                    print(write_into)
                    pass

                try:
                    theme_html = response.read()
                except:
                    pass
                else:
                    line_count = 0
                    for line in theme_html.splitlines():
                        line = line.decode('utf-8')
                        # Parse and take the name of theme
                        if line_count == 10:
                            break # if information is not in first 10 lines, not there
                        line_count += 1
                        try:
                            indice = line.index("Theme Name:")
                            line = line[indice:len(line)]
                            theme_name = line.replace("Theme Name:", "")

                            theme_names.append(theme_name)
                        except ValueError: # theme name does not exist in line
                            pass
                        try:
                            indice = line.index("Theme URI:")
                            line = line[indice:len(line)]
                            theme_uri = line.replace("Theme URI:", "")

                            theme_uris.append(theme_uri)
                        except ValueError: # theme uri does not exist in line
                            pass
                        try:
                            indice = line.index("Author:")
                            line = line[indice:len(line)]
                            author = line.replace("Author:","")

                            authors.append(author)
                        except ValueError: # No author is found
                            pass
                        try:
                            indice = line.index("Author URI:")
                            line = line[indice:len(line)]
                            author_uri = line.replace("Author:","")

                            author_uris.append(author_uri)
                        except ValueError: # No author uri is found
                            pass

        if classes.get('rel') is not None:
            if "style.css?" in classes.get('href'):
                theme_url = str(classes.get('href'))
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-Agent', 'Mozilla/5.0')]

                try:
                    response = opener.open(theme_url,timeout=60)
                except ValueError:
                    # Fix the link and try again
                    # Extract the beautiful part of URL
                    http_prefix = url[:8]
                    domain_name = (url[8:].split('/'))[0]
                    theme_url = http_prefix + domain_name + theme_url
                    try:
                        response = opener.open(theme_url,timeout=60)
                    except ValueError as value_err:
                        write_into = "url: " +url+ " ValueError occured finding theme, " + str(value_err) + "\n"
                        f.write(write_into)
                        print(write_into)
                        pass
                    except (urllib.error.HTTPError,urllib.error.URLError,urllib.error.ContentTooShortError) as http_err:
                        write_into = "url: " +url+ " Urllib error occured finding theme, " + str(http_err) + "\n"
                        f.write(write_into)
                        print(write_into)
                        pass
                    except (http.client.BadStatusLine,http.client.HTTPException) as http_exp: # BadStatusLine is a Subclass of HTTPException
                        write_into = "url: " +url+ " HTTP.Client error occured finding theme, " + str(http_exp) + "\n"
                        f.write(write_into)
                        print(write_into)
                        pass
                    except (socket.error,socket.herror,socket.gaierror,socket.timeout) as socket_err:
                        write_into = "url: " +url+ " Socket Error occured finding theme, " + str(value_err) + "\n"
                        f.write(write_into)
                        print(write_into)
                        pass
                except (urllib.error.HTTPError,urllib.error.URLError,urllib.error.ContentTooShortError) as http_err:
                    write_into = "url: " +url+ "Urllib error occured finding theme, " + str(http_err) + "\n"
                    f.write(write_into)
                    print(write_into)
                    pass
                except (http.client.BadStatusLine,http.client.HTTPException) as http_exp: # BadStatusLine is a Subclass of HTTPException
                    write_into = "url: " +url+ " HTTP.Client error occured finding theme, " + str(http_exp) + "\n"
                    f.write(write_into)
                    print(write_into)
                    pass
                except (socket.error,socket.herror,socket.gaierror,socket.timeout) as socket_err:
                    write_into = "url: " +url+ " Socket Error occured finding theme, " + str(value_err) + "\n"
                    f.write(write_into)
                    print(write_into)
                    pass

                try:
                    theme_html = response.read()
                except:
                    pass
                else:
                    line_count = 0
                    for line in theme_html.splitlines():
                        line = line.decode('utf-8')
                        # Parse and take the name of theme
                        if line_count == 10:
                            break # if information is not in first 10 lines, not there
                        line_count += 1
                        try:
                            indice = line.index("Theme Name:")
                            line = line[indice:len(line)]
                            theme_name = line.replace("Theme Name:", "")

                            theme_names.append(theme_name)
                        except ValueError: # theme name does not exist in line
                            pass
                        try:
                            indice = line.index("Theme URI:")
                            line = line[indice:len(line)]
                            theme_uri = line.replace("Theme URI:", "")

                            theme_uris.append(theme_uri)
                        except ValueError: # theme uri does not exist in line
                            pass
                        try:
                            indice = line.index("Author:")
                            line = line[indice:len(line)]
                            author = line.replace("Author:","")

                            authors.append(author)
                        except ValueError: # No author is found
                            pass
                        try:
                            indice = line.index("Author URI:")
                            line = line[indice:len(line)]
                            author_uri = line.replace("Author:","")

                            author_uris.append(author_uri)
                        except ValueError: # No author uri is found
                            pass

        theme_info['theme_names'] = theme_names
        theme_info['theme_uris'] = theme_uris
        theme_info['authors'] = authors
        theme_info['author_uris'] = author_uris
    return theme_info

def controller(args,offset):
    f = open("errors.txt","a+")
    print("Will start the day from offset: " , offset)
    # connect to mysql database default: 127.0.0.1, root, root,
    try:
        read_db = pymysql.connect(
            host = args.r_host,
            user = args.r_username,
            passwd = args.r_password,
            database = args.r_db_name
        )

        write_db = pymysql.connect(
            host = args.w_host,
            user = args.w_username,
            passwd = args.w_password,
            database = args.w_db_name
        )

    except pymysql.Error as db_error:
        write_into = "Database connection error while reading: " + str(db_error) + "\n"
        f.write(write_into)
        print("Database connection error while reading: ", db_error)
    else:

        # Determine chunk size to use in file
        chunksize = 200
        chunk_id = 0
        args.cores = int(args.cores) # Need this as an integer

        try:
            read_cursor = read_db.cursor()
            sql = "SELECT * FROM summary_%s WHERE summary_%s.key = 'referer' AND summary_%s.from >= %s AND summary_%s.from < %s AND summary_%s.item != '' GROUP BY summary_%s.formID HAVING summary_%s.value > 4 LIMIT 100000 OFFSET %s"
            val = (int(args.r_table_id),int(args.r_table_id),int(args.r_table_id),args.day_from,int(args.r_table_id),args.day_to,int(args.r_table_id),int(args.r_table_id),int(args.r_table_id),int(offset))
            read_cursor.execute(sql,val) # Retrieved data
            rows = read_cursor.fetchall()
            read_cursor.close()
            read_db.close()
            # Divide rows equally into seperate cores 25*60*4 = 6000
            size_per_core = int(len(rows)/args.cores) # 6000 / 4 = 1500
            # Calculate how many chunks will be needed
            needed_chunk_iterations = int(len(rows)/chunksize) # 6000 / 100 = 60
            # Get size
            divide_into = int(chunksize/args.cores)
            # Divide data into seperate sets for each core
            seperated_rows = list(chunks(rows,divide_into)) # Seperated rows has 6000 / 25 = 240 lists each has 25 elements
            # Divide data further for each core the number of chunk iterations
            seperated_rows = list(chunks(seperated_rows,args.cores)) # Now yields 60 lists that have size 4 each has 25 elements

            # Now seperated_rows should be a 2D list. a list of 4 elements (for each core)
            # Where each element seperated_rows[0,1,2,3] has 60(needed_chunk_iterations) lists that has 25(divide_into) elements in them
            for j in range(len(seperated_rows)):
                insert_sql = []
                insert_sql.append("INSERT IGNORE INTO wordpress_data (formID, url, is_wp, theme_names, theme_uris, authors, author_uris) VALUES ")
                # Create threads
                threads = []
                for i in range(len(seperated_rows[j])):
                    x = threading.Thread(target=generate_sql, args=(seperated_rows[j][i],insert_sql,i,))
                    threads.append(x)
                    x.start()
                for index,thread in enumerate(threads):
                    thread.join()
                write_into = "Iteration " + str(j) + " / " + str(len(seperated_rows)) + " Completed, Inserted into Database" + "\n"
                f.write(write_into)
                print("Iteration %d / %d Completed, Inserted into Database", (j,len(seperated_rows)))
                # Transform insert_sql back into a write_into
                insert_sql = ''.join(insert_sql)
                # Execute the SQL created
                insert_sql = insert_sql[:len(insert_sql)-2]
                write_into = "Inserted " + str(chunksize) + " lines" + "\n"
                f.write(write_into)
                print("Inserted %d lines" % chunksize)
                write_cursor = write_db.cursor()
                write_cursor.execute(insert_sql)
                write_cursor.close()
                write_db.commit()

        except (AttributeError,pymysql.Error) as error:
            write_into = "Database Error occured: " + str(error) + "\n"
            f.write(write_into)
            print("Database Error occured: ", error)

        # Analyse results through mysql
        analyse_results(args.w_host,args.w_username,args.w_password,args.w_db_name)
        write_db.close()


def generate_sql(rows,insert_sql,i):
    f = open("errors.txt","a+")
    write_into = "Thread "+str(i)+" working on data of size "+str(len(rows)) + "\n"
    f.write(write_into)
    print("Thread %d working on data of size %d" % (i,len(rows)))
    start_time = time.time()
    sql = ""
    count = 0
    for row in rows:
        count += 1
        # Do something with data
        write_into = "Thread "+str(i)+": Completed: "+str(count)+" / "+str(len(rows)) + "\n"
        f.write(write_into)
        print("Thread %d: Completed: %d / %d" % (i,count,len(rows)))
        result = is_wordpress_tags(row[2]) # Input is the link
        if result[0] == 1: # Means it is created by wordpress
            try:
                val = (str(row[0]), str(row[2]), str(1), str(result[1]['theme_names']).strip('[]').replace('\'','') , str(result[1]['theme_uris']).strip('[]').replace('\'','') , str(result[1]['authors']).strip('[]').replace('\'','') , str(result[1]['author_uris']).strip('[]').replace('\'',''))
                sql += "('%s', '%s', '%s', '%s', '%s', '%s', '%s'), " % val
            except KeyError:
                val = (str(row[0]), str(row[2]))
                sql += "('%s', '%s', '1', '-', '-', '-', '-'), " % val
        else:
            val = (str(row[0]), str(row[2]), str(result[0]))
            sql += "('%s', '%s', '%s', '-', '-', '-', '-'), " % val # Insert error code or non_wp

    # delete the last comma and space to have a correct sql statement
    insert_sql.append(sql)
    write_into = "Thread "+str(i)+" took --- "+str((time.time()-start_time))+" seconds ---" + "\n"
    f.write(write_into)
    print("Thread %d took --- %s seconds ---" % (i,time.time() - start_time))

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def analyse_results(host,username,password,db_name):
    mydb = pymysql.connect(
        host = host,
        user = username,
        passwd = password,
        database = db_name
    )
    mycursor = mydb.cursor()
    # Will have problems if wordpress_data is not the db name, can fix
    mycursor.execute("SELECT count(*) as broken FROM wordpress_data WHERE is_wp = 3")
    broken = mycursor.fetchone()
    broken = broken[0]
    mycursor.execute("SELECT count(*) as timeout FROM wordpress_data WHERE is_wp = -1")
    timeout = mycursor.fetchone()
    timeout = timeout[0]
    mycursor.execute("SELECT count(*) as unavailable FROM wordpress_data WHERE is_wp = 2")
    unavailable = mycursor.fetchone()
    unavailable = unavailable[0]
    mycursor.execute("SELECT count(*) as wp FROM wordpress_data WHERE is_wp = 1")
    wp = mycursor.fetchone()
    wp = wp[0]
    mycursor.execute("SELECT count(*) as non_wp FROM wordpress_data WHERE is_wp = 0")
    notwp = mycursor.fetchone()
    notwp = notwp[0]
    labels = 'WordPress', 'not WordPress', 'Unavailable Link', 'Broken Link', 'Timeout'
    total = wp + notwp + unavailable + broken + timeout
    wp_perc = wp*100/total
    notwp_perc = notwp*100/total
    broken_perc = broken*100/total
    unavailable_perc = unavailable*100/total
    timeout_perc = timeout*100/total

    sizes = [wp_perc, notwp_perc, broken_perc, unavailable_perc, timeout_perc]
    explode = (0.1, 0, 0, 0, 0)
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.savefig('result_pie.png')
    plt.close()
    mycursor.close()

def calculate_offset(args):
    if os.path.isfile('cur_state.txt'):
        total_rows = -1
        f = open('cur_state.txt', 'r')
        contents = f.readlines()
        for x in contents: # Get the integer only which is how many lines left that we need not traverse
            total_rows = int(x)
            print("First row in txt: %s", total_rows)
            break
        if total_rows == 0:
            print("Total rows is equal to 0 so not skipping the day")
            return (True,0) # Offset should be zero we are not skipping the day

    # First connect to both databases
    r_mydb = pymysql.connect(
        host = args.r_host,
        user = args.r_username,
        passwd = args.r_password,
        database = args.r_db_name
    )
    r_mycursor = r_mydb.cursor()

    sql = "SELECT * FROM summary_%s WHERE summary_%s.key = 'referer' AND summary_%s.from >= %s AND summary_%s.from < %s AND summary_%s.item != '' GROUP BY summary_%s.formID HAVING summary_%s.value > 4"
    val = (int(args.r_table_id),int(args.r_table_id),int(args.r_table_id),args.day_from,int(args.r_table_id),args.day_to,int(args.r_table_id),int(args.r_table_id),int(args.r_table_id))
    r_mycursor.execute(sql,val) # Retrieved data
    rows = r_mycursor.fetchall()
    rows_of_day = 0
    for line in rows:
        rows_of_day += 1

    w_mydb = pymysql.connect(
        host = args.w_host,
        user = args.w_username,
        passwd = args.w_password,
        database = args.w_db_name
    )
    w_mycursor = w_mydb.cursor()
    # If first run ever create the table

    w_mycursor.execute("CREATE TABLE IF NOT EXISTS wordpress_data (formID VARCHAR(255) PRIMARY KEY, url VARCHAR(255), is_wp VARCHAR(255), theme_names VARCHAR(255), theme_uris VARCHAR(255), authors VARCHAR(255), author_uris VARCHAR(255))")

    if os.path.isfile('cur_state.txt'): # If such file exists
        # Open file to see days_left
        f = open('cur_state.txt', 'r')
        contents = f.readlines()
        rows_left = -1
        for x in contents: # Get the integer only which is how many lines left that we need not traverse
            rows_left = int(x)
            print("First row in txt: %s", rows_left)
            f.close()
            break
        f = open('cur_state.txt', 'w+')
        if rows_left > rows_of_day:
            # This means we have already worked on this day, so skip
            rows_left = total_rows - rows_of_day
            f.write(str(rows_left))
            f.close()
            return (False,0) # Will skip the day
        else:
            # This means we have not worked on this day yet
            f.write('0')
            f.close()
            return (True,rows_left)

    else: # Create such file
        f = open('cur_state.txt', 'w+')
        w_mycursor.execute("SELECT COUNT(*) FROM wordpress_data")
        total_rows = w_mycursor.fetchone()
        total_rows = total_rows[0]
        if total_rows > rows_of_day:
            # This means we have already worked on this day, so skip
            rows_left = total_rows - rows_of_day
            f.write(str(rows_left))
            f.close()
            return (False,0) # Will skip the day
        else:
            # This means we have not worked on this day yet
            f.write('0')
            f.close()
            return (True,total_rows)

def main():
    ssl.match_hostname = lambda cert, hostname: True # Monkey Patching ssl to avoid errors
    f = open("errors.txt","w+")
    start_time = time.time()
    # Command line arguments:
    # host, username, password, read_db_name,
    parser = argparse.ArgumentParser()
    parser.add_argument('--r_host')
    parser.add_argument('--r_username')
    parser.add_argument('--r_password')
    parser.add_argument('--r_db_name')
    parser.add_argument('--r_table_id')
    parser.add_argument('--day_from') # 'YYYY-MM-DD HH:MM:SS'
    parser.add_argument('--day_to') # 'YYYY-MM-DD HH:MM:SS'
    parser.add_argument('--w_host')
    parser.add_argument('--w_username')
    parser.add_argument('--w_password')
    parser.add_argument('--w_db_name')
    parser.add_argument('--cores')
    args = parser.parse_args()

    result = calculate_offset(args)
    if result[0]: # Returns true
        controller(args,result[1]) # Result 1 will be offset
    else:
        sys.exit(0)

    f.close()
    print("--- %s seconds ---" % (time.time() - start_time))
if __name__ == '__main__':
    main()

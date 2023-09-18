#
# Title: Analyzing CTA2 L Data
# Name: Hamza Ali
# UID: 661440716
# URL: https://replit.com/@Prof-Hummel/CTA2-Python-hamzaali198#main.py
#

import sqlite3
import matplotlib.pyplot as figure


###########################################################  
#
# print_stats
#
# Given a connection to the CTA database, executes various
# SQL queries to retrieve and output basic stats.
#
# Command one: list the station and their ID from user input
def searchName(name, dbConn):
  dbCursor = dbConn.cursor()
  sql = "select station_id, station_name from stations where station_name like ? order by station_name asc;"
  dbCursor.execute(sql, [name])
  station = dbCursor.fetchall() # have a table station name and ID

  if(len(station) == 0): # checking if there is any station from the input
    print("**No stations found...\n")
    return

  i = 0
  while i < len(station): # prints the list of each station
    station_id, station_name = station[i]
    print(f"{station_id} : {station_name}")
    i = i + 1
  print()

# Commands 2, 3, and 4. Command 2 list all of the 
# stations with their name, total number of riders and 
# percentage to of all riders. Command 3 is the same as 
# 2 but shows only the top ten stations. Command 4 is 
# the same 2 but shows only the last 10 stations.
# isAll is when it's command 2, isTop is when it's command 3,
# and command 4 is when isAll and isTop are false
def allOrTopStation(dbConn,isAll,isTop):
  # gets the total of ridership from every station
  dbCursor = dbConn.cursor()
  dbCursor.execute("Select sum(num_riders) From Ridership")
  total_ridership = dbCursor.fetchone()

  if (isAll == True): # this is command 2
    sql = "select station_name, sum(Num_Riders) from stations join ridership on stations.station_id = ridership.station_id group by ridership.station_id order by stations.station_name asc;"
  elif (isTop == True): # this is command 3
    sql = "select station_name, sum(Num_Riders) from stations join ridership on stations.station_id = ridership.station_id group by ridership.station_id order by sum(num_riders) desc limit 10;"
  else: # this is command 4
    sql = "select station_name, sum(Num_Riders) from stations join ridership on stations.station_id = ridership.station_id group by ridership.station_id order by sum(num_riders) asc limit 10;"

  # gathers the stations and the total number of riders
  dbCursor.execute(sql)
  stations = dbCursor.fetchall()

  i = 0
  # prints the station name, total number of riders,
  # and the percentage to compare the total of all stations
  while i < len(stations): 
    station_name, num_riders = stations[i]
    station_Per = num_riders / total_ridership[0] * 100
    print(f"{station_name} : {num_riders:,} ({station_Per:.2f}%)")
    i = i + 1
  print()

# Command 5: list all of the station stop, direction, and accessiblity
# based on the color the user inputs
def lineColorList(dbConn):
  color = input("\nEnter a line color (e.g. Red or Yellow): ")

  # creates a table of stop names, directions, and accessiblities
  dbCursor = dbConn.cursor()
  sql = "select stop_name, Direction, ada from stops join stopDetails on stops.stop_id = stopDetails.stop_id join lines on stopDetails.line_id = lines.line_id where color like ? order by stop_name;"
  dbCursor.execute(sql, [color])
  stations = dbCursor.fetchall()

  if len(stations) == 0: # the color does not have stations
    print("**No such line...")
  else:
    i = 0
    while i < len(stations): # printing the stop name, direction, and accessiblity
      stop_name, direction, ada = stations[i]
      if (ada == 1): # station is accessible
        isAccessible = "yes"
      else: # station is not accessible
        isAccessible = "no"
      print(f"{stop_name} : direction = {direction} (accessible? {isAccessible})")
      i = i + 1
  print()

# Commands 6 and 7: command 6 prints and plots the total number of riders
#  for each month at any year or day while command 7 is the same but
# for each year at any day or month. It's command 6 when isMonth is
# true and it's command 7 when isMonth is false.
def totalMonthOrYearRide(dbConn, isMonth):
  dbCursor = dbConn.cursor()
  if(isMonth): # this is command 6
    sql = "select strftime('%m', Ride_Date) as Month, sum(num_riders) from Ridership group by Month order by Month asc;"
    print("** ridership by month **")
  else: # this is command 7
    sql = "select strftime('%Y', Ride_Date) as Year, sum(num_riders) from Ridership group by Year order by Year asc;"
    print("** ridership by year **")
  dbCursor.execute(sql)
  monthsOrYears = dbCursor.fetchall() # a table of total number of riders for each month or year

  for monthsOrYear in monthsOrYears: # print year or month with total of riders
    curMonthOrYear, ridership = monthsOrYear
    print(f"{curMonthOrYear} : {ridership:,}")

  isPlot = input("\nPlot? (y/n) \n") # use want to plot or not

  if(isPlot == 'y'): # user wants to plot
    if(isMonth): #this is for command 6
      xLabel = "month"
      yLabel = "number of riders (x * 10^8)"
      title = "monthly ridership"
    else: # this is for command 7
      xLabel = "year"
      yLabel = "number of riders (x * 10^8)"
      title = "yearly ridership"
    # plot the data
    singlePlot(monthsOrYears,xLabel, yLabel, title)

# to plot a single line for command 6 and 7
def singlePlot(Data, xLabel, yLabel, title):
    x = []
    y = []

    for row in Data:
      xAxis, yAxis = row
      if(len(xAxis)>2):
        x.append(xAxis[2:])
      else:
        x.append(xAxis)
      y.append(yAxis)

    figure.xlabel(xLabel)
    figure.ylabel(yLabel)
    figure.title(title)
    figure.plot(x,y)
    figure.show()

# Command 8: to print the first and last days of the year the user inputs
# and compare two stations by number of riders based on user input and plot
# a line graph if the user choose to plot them.
def compareStation(dbConn):
  year = input("\nYear to compare against? ")
  station1 = input("\nEnter station 1 (wildcards _ and %): ")
  dbCursor = dbConn.cursor()
  sql = "select Station_ID, Station_Name from Stations where Station_Name Like ?;"
  dbCursor.execute(sql,[station1])
  station = dbCursor.fetchall() 

  # check if the input for station 1 from the user is good
  if(len(station) == 0): # station does not exist
    print("**No station found...\n")
    return
  elif(len(station) > 1): # the input is not too specific enough for single station
    print("**Multiple stations found...\n")
    return
  station1ID, station1Name = station[0]

  station2 = input("\nEnter station 2 (wildcards _ and %): ")
  dbCursor.execute(sql,[station2])
  station = dbCursor.fetchall()
  
  # check if the input for station 1 from the user is good
  if(len(station) == 0): # station does not exist
    print("**No station found...\n")
    return
  elif(len(station) > 1): # the input is not too specific enough for single station
    print("**Multiple stations found...\n")
    return
  station2ID, station2Name = station[0]

  # get all the days in the year
  sql = "select date(Ride_Date), num_riders from Ridership where Station_ID = ? And strftime( '%Y', Ride_Date) = ? order by Ride_Date asc;" 
  # get the first 5 days of the year
  Top5 = "select date(Ride_Date), num_riders from Ridership where Station_ID = ? And strftime( '%Y', Ride_Date) = ? order by Ride_Date asc limit 5;"
  # get the last 5 days of the year
  Last5 = " select date(Ride_Date), num_riders from Ridership where Station_ID = ? And strftime( '%Y', Ride_Date) = ? order by Ride_Date desc limit 5;" 

  # geting all, first 5, and last 5 for station 1
  dbCursor.execute(sql,[station1ID, year])
  station1Data = dbCursor.fetchall()
  dbCursor.execute(Top5,[station1ID, year])
  station1Top = dbCursor.fetchall()
  dbCursor.execute(Last5,[station1ID, year])
  station1Last = dbCursor.fetchall()
  station1Last.reverse()

 # geting all, first 5, and last 5 for station 2 
  dbCursor.execute(sql,[station2ID, year])
  station2Data = dbCursor.fetchall()
  dbCursor.execute(Top5,[station2ID, year])
  station2Top = dbCursor.fetchall()
  dbCursor.execute(Last5,[station2ID, year])
  station2Last = dbCursor.fetchall()
  station2Last.reverse()

  # print the first and last 5 days of station 1
  print(f"Station 1: {station1ID} {station1Name}")
  for day in station1Top:
    curDay, ridership = day
    print(curDay, ridership)
  for day in station1Last:
    curDay, ridership = day
    print(curDay, ridership)
  
  # print the first and last 5 days of station 2
  print(f"Station 2: {station2ID} {station2Name}")
  for day in station2Top:
    curDay, ridership = day
    print(curDay, ridership)
  for day in station2Last:
    curDay, ridership = day
    print(curDay, ridership)

  isPlot = input("\nPlot? (y/n) \n") # does user want to plot?
  if(isPlot == 'y'): #user wants to plot
    doublePlot(station1Data, station2Data, station1Name, station2Name, year)

# plotting two lines for command 8 to compare two stations with x axis being
# days and y axis being number of riders
def doublePlot(data1, data2, station1Name, station2Name, year):
  # 1 is for station 1 and 2 is for station 2
  x1 = []
  x2 = []

  y1 = []
  y2 = []

  day1 = 1
  day2 = 1
  
  # inserting data for station 1
  for row in data1:
    day, ridership = row
    x1.append(day1)
    y1.append(ridership)
    day1 = day1 + 1
  
  # inserting data for station 2
  for row in data2:
    day, ridership = row
    x2.append(day2)
    y2.append(ridership)
    day2 = day2 + 1
  
  figure.xlabel("days")
  figure.ylabel("number of riders")
  figure.title(f"riders each day of {year}") 
  figure.plot(x1, y1, label = station1Name)
  figure.plot(x2, y2, label = station2Name)
  figure.legend()
  figure.show()

# Command 9: to print all the station's name, latitude, and longitude
# based on the color from user input and plots them in a map with
# the stations in the color
def mapStation(dbConn):
  dbCursor = dbConn.cursor()
  color = input("\nEnter a line color (e.g. Red or Yellow): ")

  sql = "select station_name, latitude, longitude  from stations  join stops on stations.Station_ID = stops.Station_ID join stopDetails on stops.stop_id = stopDetails.stop_id  join lines on stopDetails.line_id = lines.line_id where color like ? group by station_name;"

  dbCursor.execute(sql, [color])
  stations = dbCursor.fetchall() # table of all stations with lat and long in the color

  if len(stations) == 0: # no stations in that color
    print("**No such line...\n")
    return

  for station in stations: # print station name, lat, and long from the line color
    name, lat, long = station
    print(f"{name} : ({lat}, {long})")
  
  isPlot = input("\nPlot? (y/n) \n")

  if(isPlot == 'y'): # user want to plot
    mapPlot(stations, color)

# to plot a map for command 9 to show the locations of each station
def mapPlot(stations, color):
  x = []
  y = []
  for station in stations:
    name, lat, long = station
    x.append(long)
    y.append(lat)
  image = figure.imread("chicago.png")
  xydims = [-87.9277, -87.5569, 41.7012, 42.0868]
  figure.imshow(image, extent=xydims)
  figure.title(color + " line")

  if (color.lower() == "purple-express"):
    color = "Purple"

  figure.plot(x, y, "o", c = color)
  
  for station in stations:
    name, lat, long = station
    figure.annotate(name, (long, lat))
  
  figure.xlim([-87.9277, -87.5569])
  figure.ylim([41.7012, 42.0868])

  figure.show()


def command(dbConn):
  command = input("Please enter a command (1-9, x to exit): ")
  while (command != 'x'):
    if (command == '1'):
      name = input("\nEnter partial station name (wildcards _ and %): ")
      searchName(name,dbConn)
    elif (command == '2'):
      print("** ridership all stations **")
      allOrTopStation(dbConn, True, False)
    elif (command == '3'):
      print("** top-10 stations **\n")
      allOrTopStation(dbConn, False, True)
    elif (command == '4'):
      print("** least-10 stations **\n")
      allOrTopStation(dbConn, False, False)
    elif (command == '5'):
      lineColorList(dbConn)
    elif (command == '6'):
      totalMonthOrYearRide(dbConn, True)
    elif (command == '7'):
      totalMonthOrYearRide(dbConn, False)
    elif (command == '8'):
      compareStation(dbConn)
    elif (command == '9'):
      mapStation(dbConn)
    else:
      print("**Error, unknown command, try again...\n")
    command = input("Please enter a command (1-9, x to exit): ")



    

def print_stats(dbConn):
    dbCursor = dbConn.cursor()
    
    print("General stats:")
    
    dbCursor.execute("Select count(*) From Stations;")
    row = dbCursor.fetchone()

    dbCursor.execute("Select count(*) From Stops")
    total_stops = dbCursor.fetchone()

    dbCursor.execute("Select count(*) From Ridership")
    total_entries = dbCursor.fetchone()

    dbCursor.execute("select MIN(strftime('%Y-%m-%d -', Ride_Date)), max(strftime('%Y-%m-%d', Ride_Date)) from ridership;")
    range_Date = dbCursor.fetchone()

    dbCursor.execute("Select sum(num_riders) From Ridership")
    total_ridership = dbCursor.fetchone()

    dbCursor.execute("select sum(num_riders) from ridership where  Type_of_Day = 'W'")
    weekdayRidership = dbCursor.fetchone()
    weekdayPer = weekdayRidership[0] / total_ridership[0] * 100

    dbCursor.execute("select sum(num_riders) from ridership where  Type_of_Day = 'A'")
    satRidership = dbCursor.fetchone()
    satPer = satRidership[0] / total_ridership[0] * 100

    dbCursor.execute("select sum(num_riders) from ridership where  Type_of_Day = 'U'")
    sunRidership = dbCursor.fetchone()
    sunPer = sunRidership[0] / total_ridership[0] * 100

    print("  # of stations:", f"{row[0]:,}")
    print("  # of stops:", f"{total_stops[0]:,}")
    print("  # of ride entries:", f"{total_entries[0]:,}")
    print("  date range:", f"{range_Date[0]}",f"{range_Date[1]}")
    print("  Total ridership:", f"{total_ridership[0]:,}")
    print("  Weekday ridership:", f"{weekdayRidership[0]:,}",'({}%)'.format(round(weekdayPer,2)))
    print("  Saturday ridership:", f"{satRidership[0]:,}", '({}%)'.format(round(satPer,2)))
    print("  Sunday/holiday ridership:", f"{sunRidership[0]:,}", '({}%)'.format(round(sunPer,2)))
    print()
    



###########################################################  
#
# main
#
print('** Welcome to CTA L analysis app **')
print()

dbConn = sqlite3.connect('CTA2_L_daily_ridership.db')

print_stats(dbConn)
command(dbConn)

#
# done
#

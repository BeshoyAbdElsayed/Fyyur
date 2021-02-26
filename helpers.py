from datetime import datetime

#----------------------------------------------------------------------------#
# helper functions.
#----------------------------------------------------------------------------#

# get the number of upcoming shows 
# shows: list of shows
# return: integer of number of upcoming shows
def get_num_upcoming_shows(shows):
  num_upcoming_shows = 0
  for show in shows:
    start_time = datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S')
    now = datetime.now()
    # checking if start_time is in the future or not
    if start_time > now:
      num_upcoming_shows += 1
  return num_upcoming_shows

# get the number of past shows 
# shows: list of shows
# return: integer of number of past shows
def get_num_past_shows(shows):
  num_past_shows = 0
  for show in shows:
    start_time = datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S')
    now = datetime.now()
    # checking if start_time is in the past or not
    if start_time < now:
      num_past_shows += 1
  return num_past_shows

# get the upcoming shows 
# shows: list of shows
# return: list of upcoming shows
def get_upcoming_shows(shows):
  upcoming_shows = []
  for show in shows:
    start_time = datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S')
    now = datetime.now()
    # checking if start_time is in the future or not
    if start_time > now:
      upcoming_shows.append({
        "show_id": show.id,
        "venue_id": show.venue.id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time
      })
  return upcoming_shows

# get the past shows 
# shows: list of shows
# return: list of past shows
def get_past_shows(shows):
  past_shows = []
  for show in shows:
    start_time = datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S')
    now = datetime.now()
    # checking if start_time is in the past or not
    if start_time < now:
      past_shows.append({
        "show_id": show.id,
        "venue_id": show.venue.id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time
      })
  return past_shows

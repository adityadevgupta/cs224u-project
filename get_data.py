from YakGrabber import *

import numpy as np
import threading
import datetime

# Module that handles Yak retrieval, without any preprocessing.
# yg.fetch_yaks gets us all the yaks that would appear to a user.
# (usually on the order of the 100 most recent yaks)
# The location is set to Stanford's lat/long coords, because 
# that's the location we're interested in.
yg = YakGrabber()

# We were thinking about having some sort of time limit for yaks to accumulate
# upvotes, but that didn't seem objective, since this depends on the activity
# of yik yak at the time of the yak: for instance a yak posted at 2am might take
# more time to be upvoted properly than a yak posted at 6pm. 
# Waiting until yaks are no longer in the "new" section solves this because 
# the "new" section's size is fixed, and yaks don't leave after some specific time 
# period.

# Set of all yaks that are 'old' and aren't being voted on actively any more
# These are either yaks that have been voted off, or yaks that are no longer 
# found in the recents section. This is an array of tuples of the form 
# (messageID, handle, message, numberOfLikes)
# If the yak was voted off, the numberOfLikes is set to float("-inf")
completed_yaks = []

# Set of yaks that are still being actively voted on.
# This will be a dict, of type: messageID -> [handle, message, numberOfLikes]
current_yaks = {}

# if completed_yaks becomes super big, just make it a numpy array and pickle it or something
def handle_new_yak_set(completed_yaks, current_yaks, new_yaks_dict):
    # If completed_yaks is growing, store it in a numpy pickle file
    if len(completed_yaks) > 100:
        np.save(("data/yak_grab_" + str(datetime.datetime.now())), completed_yaks)
        completed_yaks = []
    # MOVE ALL OLD YAKS INTO completed_yaks
    keys_to_remove = set()
    for yak_id in current_yaks:
        if yak_id not in new_yaks_dict:
            # Then the yak is no longer in circulation. This could be for two 
            # reasons. Either the yak has been voted off, or it is too old.
            # it's not actually possible to know exactly which one it is, but 
            # we simply use the heuristic that if the yak's numberOfLikes 
            # when it is in current_yaks is negative, we assume that it was voted off
            if current_yaks[yak_id][2] < 0:
                completed_yaks.append((yak_id, 
                                       current_yaks[yak_id][0], 
                                       current_yaks[yak_id][1], 
                                       float("-inf")))
            else:
                completed_yaks.append((yak_id, 
                                       current_yaks[yak_id][0], 
                                       current_yaks[yak_id][1], 
                                       float(current_yaks[yak_id][2])))
            keys_to_remove.add(yak_id)
    for to_del in keys_to_remove:
        del current_yaks[to_del]

    # UPDATE ALL CURRENT YAKS THAT ARE LEFT
    for yak_id in new_yaks_dict:
        if yak_id in current_yaks:
            current_yaks[yak_id][2] = new_yaks_dict[yak_id][2]
        else:
            current_yaks[yak_id] = new_yaks_dict[yak_id]

# TEST CODE FOR THE ABOVE FUNCTION

# completed_yaks = []

# current_yaks = {}

# test_yaks_1 = {"1": ["", "message 1", 2],
#                "2": ["", "message 2", -2],
#                "3": ["", "message 3", 2],
#                "4": ["", "message 4", 2]}

# handle_new_yak_set(completed_yaks, current_yaks, test_yaks_1)
# print completed_yaks
# print current_yaks

# test_yaks_2 = {"1": ["", "message 1", 4],
#                "6": ["", "message 2", -2],
#                "3": ["", "message 3", -1],
#                "5": ["", "message 5", 10]}

# handle_new_yak_set(completed_yaks, current_yaks, test_yaks_2)
# print completed_yaks
# print current_yaks

def make_dict(yaks_arr):
    return {yak["messageID"]:[(yak['handle'] if ('handle' in yak) and yak['handle'] else ""), 
                              yak['message'], 
                              yak['numberOfLikes']] for yak in yaks_arr}


def update():
    most_recent_yaks = yg.fetch_yaks()
    new_yaks_dict = make_dict(most_recent_yaks)
    handle_new_yak_set(completed_yaks, current_yaks, new_yaks_dict)    

def continuously_grab_yaks():
    update()
    print "Archived Yaks this file: " + str(len(completed_yaks))
    # call f() again in 60 seconds
    threading.Timer(15, continuously_grab_yaks).start()

# start calling f now and every 60 sec thereafter
continuously_grab_yaks()
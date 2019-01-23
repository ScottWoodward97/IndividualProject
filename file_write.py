import os
import time

def write_game(dir_name, file_name):
    #dir_name unique to the grouping of test data,
    # can extract from this location and process data in bulk post training
    #file_name would need to be created so that the file name
    # is unique whilst also providing the require information for processing
    #   such as who each player is and in what position are they?
    print(time.strftime("%Y-%m-%d--%H-%M-%S", time.gmtime()))
    
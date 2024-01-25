import csv
import os
from functools import reduce

def getHelps():
    with open(os.path.join('data', 'helps.csv')) as f:
        helps_file = csv.reader(f, delimiter=',')
        helps = ""
        for row in helps_file:
            helps += f"{row[0]} : {row[1]}\n"
        return helps

flat_map = lambda f, xs: reduce(lambda a, b: a + b, *list(map(f, xs)))

def get_all_users(channels):
    res = []
    for channel in channels:
        res += channel.getConnectedUsers()
    return res
    
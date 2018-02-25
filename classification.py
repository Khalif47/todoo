# def profile_rank(post, profiles):
#     # word count

import ast
import numpy

t = "we love food more than anyone and food is the best"

'''
arbitrary weightings :

skills 30 points
experience 50 points
years in industry years * 50
job task 50
other experience 5
title 50 points

'''


def rank_employers(post, profiles):
    # title
    title = str(post[3])
    industry = str(post[2])
    # list of key features
    role = str(popular(post[4]))
    skills = list(post[5])
    positions = list(post[6])
    years = list(post[7])
    for item in range(len(profiles)):
        points = 0
        if not str(profiles[item][6]) == industry:
            profiles[item] += (points,)
            pass
        else:
            # check for title and check if it's in positions
            if profiles[item][11] is not None:
                for i in ast.literal_eval(profiles[item][11]):
                    if str(i) in title or title in str(i):
                        points += 50
                for i in ast.literal_eval(profiles[item][11]):
                    for j in positions:
                        if str(i) in str(j) or str(j) in str(i):
                            points += 50
            # skills
            employee_skill = popular(profiles[item][8])
            if employee_skill is not None:
                for i in skills:
                    for j in employee_skill:
                        if str(i) in str(j) or str(j) in str(i):
                            points += 30
            # role and skill in description
            employee_description = popular(profiles[item][7])
            if employee_description is not None:
                for i in employee_description:
                    for j in role:
                        if str(i) in str(j) or str(j) in str(i):
                            points += 50
            # experience in industry
            if profiles[item][13] is not None:
                for i in range(len(ast.literal_eval(profiles[item][13]))):
                    if str(ast.literal_eval(profiles[item][13])[i]) == industry:
                        points += 50
                        # also years with particular industry experience
                        points += int(ast.literal_eval(profiles[item][10])[i]) * 50
                    else:
                        # those other years not in industry will only acquire 5 points
                        points += int(ast.literal_eval(profiles[item][10])[i]) * 5
            profiles[item] += (points,)
    # sort by points
    profiles = sorted(profiles, key=lambda tup: tup[14], reverse=True)  # sorts in place
    return profiles


def popular(text):
    famous = []
    counter = {}
    list_count = []
    for word in text.split():
        word = word.strip(',')
        word = word.strip('.')
        word = word.strip('?')
        word = word.strip('-')
        word = word.strip(':')
        word = word.strip('"')
        word = word.strip("'")
        word = word.strip('[')
        word = word.strip(']')
        word = word.lower()
        try:
            counter[word] += 1
        except KeyError:
            counter[word] = 1
    for item in counter:
        list_count.append(counter[item])
    n = numpy.array(list_count)
    barrier = numpy.mean(n, axis=0) + numpy.std(n, axis=0)
    for item in counter:
        if counter[item] >= barrier and len(item) >= 4:
            famous.append(item)
    return famous

# lister = popular(t)
# points = 0
# names = {"food": 2, "leadership": 3}
# check = ["leadership", "leader"]
# for item in check:
#     for words in names:
#         if words in item or item in words:
#             points += names[words] * 50
# print(points)
#
# t = ["lister"]

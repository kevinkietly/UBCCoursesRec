from flask import Flask, request, render_template
import pandas as pd
import numpy as np
import urllib.request

app = Flask(__name__)

@app.route('/', methods = ["GET", "POST"])
def index():
    if request.method == "POST":
        course_code = request.form.getlist("course_code")
        subject_code = request.form.get("subject_code")
        subject_code = subject_code.split(", ")
        average = request.form.get("average")
        startyear = request.form.get("starting year")
        endyear = request.form.get("ending year")
        offered = request.form.getlist("offered")
        print(type(course_code))
        print(course_code)
        print(subject_code)
        print(average)
        print(startyear)
        print(endyear)
        print(offered)
        summer = False
        winter = False
        lvl1 = False
        lvl2 = False
        lvl3 = False
        lvl4 = False
        lvl5 = False
        if "summer" in offered:
            summer = True
            print(make_years(startyear, endyear, True, False))
            print(filter_overall_avg(pull_data(make_years(startyear, endyear, True, False), subject_code)))
        elif "winter" in offered:
            winter = True
            print(make_years(startyear, endyear, False, True))
            pull_data(make_years(startyear, endyear, False, True), subject_code)
        elif "summer" in offered and "winter" in offered:
            print(make_years(startyear, endyear, True, True))
            pull_data(make_years(startyear, endyear, True, True), subject_code)
        if "1" in course_code:
            lvl1 = True
        if "2" in course_code:
            lvl2 = True
        if "3" in course_code:
            lvl3 = True
        if "4" in course_code:
            lvl4 = True
        if "5" in course_code:
            lvl5 = True
        # probably should put this in a function
        # make years
        years = make_years(startyear, endyear, summer, winter)
        # pull data
        data = pull_data(years, subject_code)
        # filter for level
        filter_level = filter_lvls(data, lvl1, lvl2, lvl3, lvl4, lvl5)
        # filter for overall averages
        filter_ov = filter_overall_avg(filter_level)
        # convert to list of courses
        courses = find_courses(filter_ov)
        # find averages over years
        calc_avgs = avg_of_avgs(courses)
        # filter for courses w avg over user defined minimum
        filter_avgs = filter_avg(calc_avgs, average)
        print(filter_avgs)
    return render_template("index.html")

# creating list of terms to loop over
def make_years(start, stop, summer, winter):
    year_range = np.arange(int(start), int(stop)+1, 1)
    years = []
    for y in year_range:
        if summer:
            years.append(str(y) + "S")
        if winter:
            years.append(str(y) + "W")
    return years

# pull data
def pull_data(years, courses):
    dataframes = []
    for year in years:
        for course in courses:
            url_data = f'https://raw.githubusercontent.com/DonneyF/ubc-pair-grade-data/master/tableau-dashboard/UBCV/{year}/UBCV-{year}-{course}.csv'
            print(url_data)
            data_csv = pd.read_csv(url_data)
            dataframes.append(data_csv)
    return pd.concat(dataframes)

def filter_overall_avg(data):
    """
    filters dataframe for only overall averages
    """
    return data[data['Section'] == "OVERALL"]


def filter_lvl(data, lvl):
    """
    filters dataframe for classes of the given levels
    a) lvlplus == false: only one lvl ###this doesn't work for some reason?
    b) lvlplus == true: select all lvl above the given
    """
    data = data[(data['Course'] >= lvl) & (data['Course'] < lvl + 100)]
    return data


def filter_lvls(data, lvl1, lvl2, lvl3, lvl4, lvl5):
    """
    filters for only levels that user selects
    """
    dfs = []
    if lvl1:
        dfs.append(filter_lvl(data, 100))
    if lvl2:
        dfs.append(filter_lvl(data, 200))
    if lvl3:
        dfs.append(filter_lvl(data, 300))
    if lvl4:
        dfs.append(filter_lvl(data, 400))
    if lvl5:
        dfs.append(filter_lvl(data, 500))
        dfs.append(filter_lvl(data, 600))
        dfs.append(filter_lvl(data, 700))
    return pd.concat(dfs)


def find_courses(data):
    """
    converts pandas df to list of courses
    """
    loc = []
    for row in range(len(data)):
        # checks if detail is nan
        if pd.isnull(data.iloc[row]['Detail']):
            loc.append(("{} {} ".format(data.iloc[row]['Subject'],
                                        data.iloc[row]['Course']),
                        round(data.iloc[row]['Avg'], 1)))
        else:
            loc.append(("{} {}{}".format(data.iloc[row]['Subject'],
                                         data.iloc[row]['Course'],
                                         data.iloc[row]['Detail']),
                        round(data.iloc[row]['Avg'], 1)))

    return sorted(loc)


def avg_of_avgs(loc):
    """
    returns list of courses with averages that
    have been averaged out over the year range
    """
    if loc == []:
        return []
    loc_final = []
    course = loc[0][0]
    avg = [loc[0][1]]
    count = 1
    for c in loc[1:]:
        if c[0] == course:
            avg.append(c[1])
            count += 1
        else:
            mx = max(avg)
            mn = min(avg)
            loc_final.append((course, round(sum(avg) / count, 1), mx, mn))
            course = c[0]
            avg = [c[1]]
            count = 1
    return loc_final


def filter_avg(loc, avg):
    """
    returns courses that have an average over the given
    avg over all the years looked at
    """
    if loc == []:
        return []
    loc_final = []
    i = 0
    for c in loc:
        if loc[i][1] >= int(avg):
            loc_final.append(c)
        i += 1
    return loc_final

if __name__ == '__main__':
    app.run(debug=True)
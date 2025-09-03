import pandas as pd
import json
import datetime
from sportsdataverse.dl_utils import download, underscore

def espn_nhl_schedule(dates=None, season_type=None, limit=500) -> pd.DataFrame:
    """espn_nhl_schedule - look up the NHL schedule for a given date

    Args:
        dates (int): Used to define different seasons. 2002 is the earliest available season.
        season_type (int): season type, 1 for pre-season, 2 for regular season, 3 for post-season, 4 for all-star, 5 for off-season
        limit (int): number of records to return, default: 500.
    Returns:
        pd.DataFrame: Pandas dataframe containing
        schedule events for the requested season.
    """
    if dates is None:
        dates = ''
    else:
        dates = '&dates=' + str(dates)
    if season_type is None:
        season_type = ''
    else:
        season_type = '&seasontype=' + str(season_type)

    url = "http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard?limit={}{}{}".format(limit, dates, season_type)
    resp = download(url=url)

    ev = pd.DataFrame()
    if resp is not None:
        events_txt = json.loads(resp)

        events = events_txt.get('events')
        for event in events:
            event.get('competitions')[0].get('competitors')[0].get('team').pop('links',None)
            event.get('competitions')[0].get('competitors')[1].get('team').pop('links',None)
            if event.get('competitions')[0].get('competitors')[0].get('homeAway')=='home':
                event['competitions'][0]['home'] = event.get('competitions')[0].get('competitors')[0].get('team')
                event['competitions'][0]['away'] = event.get('competitions')[0].get('competitors')[1].get('team')
            else:
                event['competitions'][0]['away'] = event.get('competitions')[0].get('competitors')[0].get('team')
                event['competitions'][0]['home'] = event.get('competitions')[0].get('competitors')[1].get('team')

            del_keys = ['broadcasts','geoBroadcasts', 'headlines', 'series']
            for k in del_keys:
                event.get('competitions')[0].pop(k, None)
            x = pd.json_normalize(event.get('competitions')[0], sep='_')
            x['game_id'] = x['id'].astype(int)
            x['season'] = event.get('season').get('year')
            x['season_type'] = event.get('season').get('type')
            ev = pd.concat([ev,x],axis=0, ignore_index=True)
    ev = pd.DataFrame(ev)
    ev.columns = [underscore(c) for c in ev.columns.tolist()]
    return ev

def espn_nhl_calendar(season=None) -> pd.DataFrame:
    """espn_nhl_calendar - look up the NHL calendar for a given season

    Args:
        season (int): Used to define different seasons. 2002 is the earliest available season.

    Returns:
        pd.DataFrame: Pandas dataframe containing calendar dates for the requested season.

    Raises:
        ValueError: If `season` is less than 2002.
    """
    url = "http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard?dates={}".format(season)
    resp = download(url=url)
    txt = json.loads(resp)['leagues'][0]['calendar']
    datenum = list(map(lambda x: x[:10].replace("-",""),txt))
    date = list(map(lambda x: x[:10],txt))

    year = list(map(lambda x: x[:4],txt))
    month = list(map(lambda x: x[5:7],txt))
    day = list(map(lambda x: x[8:10],txt))

    data = {
        "season": season,
        "datetime" : txt,
        "date" : date,
        "year": year,
        "month": month,
        "day": day,
        "dateURL": datenum
    }
    df = pd.DataFrame(data)
    df['url']="http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?dates="
    df['url']= df['url'] + df['dateURL']
    return df

def most_recent_nhl_season():
    if int(str(datetime.date.today())[5:7]) >= 10:
        return int(str(datetime.date.today())[0:4]) + 1
    else:
        return int(str(datetime.date.today())[0:4])

def year_to_season(year):
    first_year = str(year)[2:4]
    next_year = int(first_year) + 1
    if int(next_year) < 10 and int(first_year) >= 0:
        next_year_formatted = f"0{next_year}"
    elif int(first_year) == 99:
        next_year_formatted = "00"
    else:
        next_year_formatted = str(next_year)
    return f"{year}-{next_year_formatted}"
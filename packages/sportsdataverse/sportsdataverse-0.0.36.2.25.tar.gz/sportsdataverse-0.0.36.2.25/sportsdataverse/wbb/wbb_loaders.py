import pandas as pd
import json
from tqdm import tqdm
from typing import List, Callable, Iterator, Union, Optional
from sportsdataverse.config import WBB_BASE_URL, WBB_TEAM_BOX_URL, WBB_PLAYER_BOX_URL, WBB_TEAM_SCHEDULE_URL
from sportsdataverse.errors import SeasonNotFoundError
from sportsdataverse.dl_utils import download

def load_wbb_pbp(seasons: List[int]) -> pd.DataFrame:
    """Load women's college basketball play by play data going back to 2002

    Example:
        `wbb_df = sportsdataverse.wbb.load_wbb_pbp(seasons=range(2002,2022))`

    Args:
        seasons (list): Used to define different seasons. 2002 is the earliest available season.

    Returns:
        pd.DataFrame: Pandas dataframe containing the
        play-by-plays available for the requested seasons.

    Raises:
        ValueError: If `season` is less than 2002.
    """
    data = pd.DataFrame()
    if type(seasons) is int:
        seasons = [seasons]
    for i in tqdm(seasons):
        if int(i) < 2002:
            raise SeasonNotFoundError("season cannot be less than 2002")
        i_data = pd.read_parquet(WBB_BASE_URL.format(season=i), engine='auto', columns=None)
        data = pd.concat([data, i_data], axis = 0, ignore_index = True)
    #Give each row a unique index
    data.reset_index(drop=True, inplace=True)
    return data

def load_wbb_team_boxscore(seasons: List[int]) -> pd.DataFrame:
    """Load women's college basketball team boxscore data

    Example:
        `wbb_df = sportsdataverse.wbb.load_wbb_team_boxscore(seasons=range(2002,2022))`

    Args:
        seasons (list): Used to define different seasons. 2002 is the earliest available season.

    Returns:
        pd.DataFrame: Pandas dataframe containing the
        team boxscores available for the requested seasons.

    Raises:
        ValueError: If `season` is less than 2002.
    """
    data = pd.DataFrame()
    if type(seasons) is int:
        seasons = [seasons]
    for i in tqdm(seasons):
        if int(i) < 2002:
            raise ValueError("season cannot be less than 2002")
        i_data = pd.read_parquet(WBB_TEAM_BOX_URL.format(season = i), engine='auto', columns=None)
        data = pd.concat([data, i_data], axis = 0, ignore_index = True)
    #Give each row a unique index
    data.reset_index(drop=True, inplace=True)

    return data

def load_wbb_player_boxscore(seasons: List[int]) -> pd.DataFrame:
    """Load women's college basketball player boxscore data

    Example:
        `wbb_df = sportsdataverse.wbb.load_wbb_player_boxscore(seasons=range(2002,2022))`

    Args:
        seasons (list): Used to define different seasons. 2002 is the earliest available season.

    Returns:
        pd.DataFrame: Pandas dataframe containing the
        player boxscores available for the requested seasons.

    Raises:
        ValueError: If `season` is less than 2002.
    """
    data = pd.DataFrame()
    if type(seasons) is int:
        seasons = [seasons]
    for i in tqdm(seasons):
        if int(i) < 2002:
            raise ValueError("season cannot be less than 2002")
        i_data = pd.read_parquet(WBB_PLAYER_BOX_URL.format(season = i), engine='auto', columns=None)
        data = pd.concat([data, i_data], axis = 0, ignore_index = True)
    #Give each row a unique index
    data.reset_index(drop=True, inplace=True)

    return data

def load_wbb_schedule(seasons: List[int]) -> pd.DataFrame:
    """Load women's college basketball schedule data

    Example:
        `wbb_df = sportsdataverse.wbb.load_wbb_schedule(seasons=range(2002,2022))`

    Args:
        seasons (list): Used to define different seasons. 2002 is the earliest available season.

    Returns:
        pd.DataFrame: Pandas dataframe containing the
        schedule for  the requested seasons.

    Raises:
        ValueError: If `season` is less than 2002.
    """
    data = pd.DataFrame()
    if type(seasons) is int:
        seasons = [seasons]
    for i in tqdm(seasons):
        if int(i) < 2002:
            raise ValueError("season cannot be less than 2002")
        i_data = pd.read_parquet(WBB_TEAM_SCHEDULE_URL.format(season = i), engine='auto', columns=None)
        data = pd.concat([data, i_data], axis = 0, ignore_index = True)
    #Give each row a unique index
    data.reset_index(drop=True, inplace=True)

    return data

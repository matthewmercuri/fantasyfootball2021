from bs4 import BeautifulSoup
import os
import pandas as pd
import requests
from tqdm import tqdm


class Data:
    def __init__(self) -> None:
        self.ffrank_df = None

    def _find_profile_links(self, html):
        soup = BeautifulSoup(html, 'lxml')
        player_table_rows = soup.find_all('td', {'data-stat': 'player'})

        profile_links_dict = {}
        for x in player_table_rows:
            data = x.find('a')
            name = data.contents[0].replace('*', ' ').replace('+', ' ').strip().upper()
            link = data['href']
            profile_links_dict[name] = str(link)

        return profile_links_dict

    def historical_ff_agg_data(self, force_update: bool = False,
                               MIN_GAMES: int = 8) -> pd.DataFrame:
        ''' TODO:
        - discrimate against oultiers in a new function
        - figure out a better way to manage min games
        '''

        if MIN_GAMES != 8:
            force_update = True

        # fetch and/or load historical FF performance data
        YEARS = [2020, 2019, 2018, 2017, 2016]
        URL_FF_START = 'https://www.pro-football-reference.com/years/'
        URL_FF_END = '/fantasy.htm'

        # checking if data already exists ========================================
        FETCH = False
        FOUND_YEARS = []

        for year in YEARS:
            if os.path.isfile(f'./data/{year}_ff_rankings.csv'):
                FOUND_YEARS.append(year)

        if set(FOUND_YEARS) != set(YEARS):
            GET_YEARS = []
            for year in YEARS:
                if year not in FOUND_YEARS:
                    GET_YEARS.append(year)
            FETCH = True

        if force_update is True:
            GET_YEARS = YEARS

        # ========================================================================
        if FETCH or force_update:
            print('Gathering data...')

            # check if folder exists, if not, create it
            if os.path.isdir('./data') is False:
                os.mkdir('data')

            for year in tqdm(GET_YEARS):
                r = requests.get(URL_FF_START + str(year) + URL_FF_END, 'lxml')
                df = pd.read_html(r.text, index_col=0)[0]
                profile_links_dict = self._find_profile_links(r.text)

                # fixing column names ============================================
                df.columns = df.columns.to_flat_index()
                df.columns = ["_".join(x) for x in df.columns]

                for col in df.columns:
                    if col[:3] == 'Unn':
                        df.rename(columns={col: col.split('_')[-1]}, inplace=True)
                # ================================================================

                # other various fixes
                df = df[df['Tm'] != 'Tm']

                df[df.columns[4:]] = df[df.columns[4:]].fillna(value=0)

                df['FantPos'] = df['FantPos'].fillna('UNKN')
                df['FantPos'] = df['FantPos'].apply(lambda x: str(x).upper())

                df['Player'] = df['Player'].apply(lambda x: x.replace('*', ' '))
                df['Player'] = df['Player'].apply(lambda x: x.replace('+', ' '))
                df['Player'] = df['Player'].apply(lambda x: x.strip().upper())

                # adding profootballref profile links to df
                df['Player_Profile_Link'] = df['Player'].map(profile_links_dict)

                df.to_csv(f'./data/{year}_ff_rankings.csv')

        # loading in data
        ffranks_dfs = []
        for year in YEARS:
            year_df = pd.read_csv(f'./data/{year}_ff_rankings.csv', index_col=0)
            year_df['for_year'] = year

            ffranks_dfs.append(year_df)

        ffrank_df = pd.concat(ffranks_dfs, ignore_index=True)

        # converting columns to necessary types - may be a bit overkill
        types_dict = {'Player': str, 'Tm': str, 'FantPos': str, 'Age': int,
                      'Games_G': int, 'Games_GS': int, 'Passing_Cmp': float,
                      'Passing_Att': int, 'Passing_Yds': float, 'Passing_TD': int,
                      'Passing_Int': int, 'Rushing_Att': int, 'Rushing_Yds': float,
                      'Rushing_Y/A': float, 'Rushing_TD': float, 'Receiving_Tgt': int,
                      'Receiving_Rec': int, 'Receiving_Yds': float,
                      'Receiving_Y/R': float,
                      'Receiving_TD': int, 'Fumbles_Fmb': int, 'Fumbles_FL': int,
                      'Scoring_TD': int, 'Scoring_2PM': int, 'Scoring_2PP': int,
                      'Fantasy_FantPt': float, 'Fantasy_PPR': float,
                      'Fantasy_DKPt': float, 'Fantasy_FDPt': float,
                      'Fantasy_VBD': float,
                      'Fantasy_PosRank': int, 'Fantasy_OvRank': int, 'for_year': int,
                      'Player_Profile_Link': str}

        ffrank_df = ffrank_df.astype(types_dict)

        ffrank_df = ffrank_df[ffrank_df['Games_G'] >= MIN_GAMES]
        ffrank_df['FantPt/G'] = ffrank_df['Fantasy_FantPt'] / ffrank_df['Games_G']

        '''
        Discriminating against large outliers here (optional).
        Not using data where FantPt/G is less than 2
        '''
        ffrank_df = ffrank_df[ffrank_df['FantPt/G'] >= 2]

        self.ffrank_df = ffrank_df

        return ffrank_df

    def get_player_gamelog(self, player: str) -> pd.DataFrame:
        player = player.strip().upper()

        if self.ffrank_df is None:
            main_df = self.historical_ff_agg_data()
        else:
            main_df = self.ffrank_df

    def get_depth_charts(self):
        pass

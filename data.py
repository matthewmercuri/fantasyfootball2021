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

    def _historical_ff_agg_data_add_cols(self, df):
        '''
        Discriminating against large outliers here (optional).
        Not using data where FantPt/G is less than 2
        '''

        df['FantPt/G'] = df['Fantasy_FantPt'] / df['Games_G']
        df = df[df['FantPt/G'] >= 2]

        return df

    def _clean_player_gamelog_df(self, df, player_pos):
        ''' Cleaning gamelog dataframes.
        - do I really need to condition cleaning on position? Is it
        possible to have a dict holding type for different possible columns?
        '''
        # cleaning columns
        df.columns = df.columns.to_flat_index()
        df.columns = ["_".join(x) for x in df.columns]
        for col in df.columns:
            if col[:3] == 'Unn':
                df.rename(columns={col: col.split('_')[-1]}, inplace=True)

        # dropping non-data rows
        df = df[df['Tm'] != 'Tm']
        df = df[:-1]

        if player_pos == 'QB':
            pass
        else:
            raise KeyError(f"{player_pos} is not a valid player_pos " +
                           "(can't clean gamelog)")

        return df

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

        ffrank_df = self._historical_ff_agg_data_add_cols(ffrank_df)
        self.ffrank_df = ffrank_df

        return ffrank_df

    def get_player_gamelog_df(self, player: str) -> pd.DataFrame:
        ''' Returns a DataFrame of a specific player's gamelogs.
        Example: https://www.pro-football-reference.com/players/P/PresDa01/gamelog/

        TODO:
        - handle for case during season (finding player gamelogs for new players).
          This currently only is able to pull for players that have played in
          the last few seasons.
        '''
        BASE_URL = 'https://www.pro-football-reference.com'

        player = player.strip().upper()

        if self.ffrank_df is None:
            df = self.historical_ff_agg_data()
        else:
            df = self.ffrank_df

        available_players = df['Player'].to_list()
        if player not in available_players:
            raise KeyError(f'{player} not in available players list.')

        player_df = df[df['Player'] == player]

        player_gamelog_url = (BASE_URL + player_df['Player_Profile_Link'].iloc[0][:-4]
                              + '/gamelog/')
        player_pos = player_df['FantPos'].iloc[0].strip().upper()

        r = requests.get(player_gamelog_url, 'lxml')
        gamelog_df = pd.read_html(r.text, index_col=0)[0]

        gamelog_df = self._clean_player_gamelog_df(gamelog_df, player_pos)
        gamelog_df.to_csv('gamelog_test.csv')

        return gamelog_df

    def get_depth_charts(self):
        ''' team depth charts '''
        pass

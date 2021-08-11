# from bs4 import BeautifulSoup
import os
import pandas as pd
import requests
from tqdm import tqdm


class Data:

    @staticmethod
    def historical_ff_agg_data(MIN_GAMES=8):

        # fetch and/or load historical FF performance data

        force_update = False

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
        # ========================================================================
        if FETCH or force_update:
            print('Gathering data...')

            # check if folder exists, if not, create it
            if os.path.isdir('./data') is False:
                os.mkdir('data')

            for year in tqdm(GET_YEARS):
                r = requests.get(URL_FF_START + str(year) + URL_FF_END, 'lxml')
                df = pd.read_html(r.text, index_col=0)[0]

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
                      'Fantasy_PosRank': int, 'Fantasy_OvRank': int, 'for_year': int}

        ffrank_df = ffrank_df.astype(types_dict)

        ffrank_df = ffrank_df[ffrank_df['Games_G'] >= MIN_GAMES]
        ffrank_df['FantPt/G'] = ffrank_df['Fantasy_FantPt'] / ffrank_df['Games_G']

        '''
        Discriminating against large outliers here (optional).
        Not using data where FantPt/G is less than 2
        '''
        ffrank_df = ffrank_df[ffrank_df['FantPt/G'] >= 2]

        return ffrank_df
import data
from scipy import stats


class Utils:
    def __init__(self) -> None:
        self.Data = data.Data()

    def fantasy_points_normality_test(self, position: str = 'ALL'):
        ''' checks if the fantasy points per game is normally
        dirstributed amongst players
        '''
        position = position.strip().upper()

        df = self.Data.historical_ff_agg_data()

        # clean outliers
        if position == 'ALL':
            # this is pretty useless ...
            df = df[df['FantPos'] == position]
            df = df[df['FantPt/G'] <= 25]

            print(stats.normaltest(df['FantPt/G']))
        elif position == 'QB':
            df = df[df['FantPos'] == position]
            df = df[df['FantPt/G'] <= 25]

            print(stats.normaltest(df['FantPt/G']))
        elif position == 'RB':
            df = df[df['FantPos'] == position]
            df = df[df['FantPt/G'] <= 21]

            print(stats.normaltest(df['FantPt/G']))
        elif position == 'WR':
            df = df[df['FantPos'] == position]
            df = df[df['FantPt/G'] <= 18]

            print(stats.normaltest(df['FantPt/G']))
        elif position == 'TE':
            df = df[df['FantPos'] == position]
            df = df[df['FantPt/G'] <= 14]

            print(stats.normaltest(df['FantPt/G']))

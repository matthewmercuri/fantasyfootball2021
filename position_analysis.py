import data


class PositionAnalysis:
    def __init__(self, MIN_GAMES: int = 8) -> None:
        self.data = data.Data()
        self.ffrank_df = self.data.historical_ff_agg_data(MIN_GAMES=MIN_GAMES)

    def get_average_points_position(self, position='ALL') -> dict:
        ''' Returns the average points by position as dict '''

        position = position.strip().upper()

        if position not in ['TE', 'WR', 'QB', 'RB', 'TOTAL', 'ALL']:
            raise TypeError('Please enter a valid position.')

        avg_points_pos_dict = {}

        if position == 'TOTAL' or position == 'ALL':
            _df = self.ffrank_df

            avg_points_pos_dict['ALL'] = {}
            avg_points_pos_dict['ALL']['Total_Average'] = _df['Fantasy_FantPt'].mean()
            avg_points_pos_dict['ALL']['Total_STD'] = _df['Fantasy_FantPt'].std()
            avg_points_pos_dict['ALL']['Game_Average'] = _df['FantPt/G'].mean()
            avg_points_pos_dict['ALL']['Game_STD'] = _df['FantPt/G'].std()

        if position == 'QB' or position == 'ALL':
            _df = self.ffrank_df[self.ffrank_df['FantPos'] == 'QB']

            avg_points_pos_dict['QB'] = {}
            avg_points_pos_dict['QB']['Total_Average'] = _df['Fantasy_FantPt'].mean()
            avg_points_pos_dict['QB']['Total_STD'] = _df['Fantasy_FantPt'].std()
            avg_points_pos_dict['QB']['Game_Average'] = _df['FantPt/G'].mean()
            avg_points_pos_dict['QB']['Game_STD'] = _df['FantPt/G'].std()

        if position == 'RB' or position == 'ALL':
            _df = self.ffrank_df[self.ffrank_df['FantPos'] == 'RB']

            avg_points_pos_dict['RB'] = {}
            avg_points_pos_dict['RB']['Total_Average'] = _df['Fantasy_FantPt'].mean()
            avg_points_pos_dict['RB']['Total_STD'] = _df['Fantasy_FantPt'].std()
            avg_points_pos_dict['RB']['Game_Average'] = _df['FantPt/G'].mean()
            avg_points_pos_dict['RB']['Game_STD'] = _df['FantPt/G'].std()

        if position == 'WR' or position == 'ALL':
            _df = self.ffrank_df[self.ffrank_df['FantPos'] == 'WR']

            avg_points_pos_dict['WR'] = {}
            avg_points_pos_dict['WR']['Total_Average'] = _df['Fantasy_FantPt'].mean()
            avg_points_pos_dict['WR']['Total_STD'] = _df['Fantasy_FantPt'].std()
            avg_points_pos_dict['WR']['Game_Average'] = _df['FantPt/G'].mean()
            avg_points_pos_dict['WR']['Game_STD'] = _df['FantPt/G'].std()

        if position == 'TE' or position == 'ALL':
            _df = self.ffrank_df[self.ffrank_df['FantPos'] == 'TE']

            avg_points_pos_dict['TE'] = {}
            avg_points_pos_dict['TE']['Total_Average'] = _df['Fantasy_FantPt'].mean()
            avg_points_pos_dict['TE']['Total_STD'] = _df['Fantasy_FantPt'].std()
            avg_points_pos_dict['TE']['Game_Average'] = _df['FantPt/G'].mean()
            avg_points_pos_dict['TE']['Game_STD'] = _df['FantPt/G'].std()

        return avg_points_pos_dict

import data
# import position_analysis

data = data.Data()
# print(data.historical_ff_agg_data(force_update=True))
print(data.get_player_gamelog_df('Dak Prescott'))

# PosAn = position_analysis.PositionAnalysis()
# print(PosAn.get_average_points_position(position='all'))

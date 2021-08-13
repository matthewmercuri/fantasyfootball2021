# import data
# import utils
# import position_analysis
import draftsim

# data = data.Data()
# print(data.historical_ff_agg_data(force_update=True))
# print(data.get_player_gamelog_df('Dak Prescott'))

# PosAn = position_analysis.PositionAnalysis()
# print(PosAn.get_average_points_position(position='all'))

# Utils = utils.Utils()
# Utils.fantasy_points_normality_test(position='WR')

DraftSimulator = draftsim.DraftSimulator()
print(DraftSimulator._get_draft_list())
# DraftSimulator._get_position_count_draftees()

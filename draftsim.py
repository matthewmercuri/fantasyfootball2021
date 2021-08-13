import data

''' Simulate drafts to see what the ideal draft order would be
- need a way to enforce contraints
- is it better to draft from a list of actual players? Or just use
simulated 'picks' based on statistical position data (then perhaps
create a simulated 'pool' of players)?
- I think I like the latter of the above approaches, perhaps try
both
- how to handle kickers?
- how much does value above peers influence results? How to tell
how good a draft order strategy is?
- How to maintain state of draft? What should be maintained in the
state?


-OTHER IDEA: Maximize the draft for excess value. This should be a function of
expected value above peers times the inverse of how many alternatives.
How to implement this? How does this coincide with our simulation? Measure this
in state for the draft sim?

METHODOLOGY:
- [x] Create draftees:
    - use data from last few years
    - create a data set of players and obfuscate their point totals
    - e.g. each row:
        - Position, Point_Total
    - try to balance the dataset by ensuring a representative count
      position
'''


class DraftSimulator:
    def __init__(self) -> None:
        self.Data = data.Data()

    def _get_draft_list(self, year: int = 2020):
        df = self.Data.historical_ff_agg_data()

        if year in [2016, 2017, 2018, 2019, 2020]:
            df = df[df['for_year'] == year]
        else:
            raise KeyError('Not a valid year entered for draft sim.')

        df = df[['FantPos', 'Fantasy_FantPt']]
        df = self._add_kickers_defense(df)

        return df

    def _add_kickers_defense(self, df):
        ''' adds kickers and defence to draftees '''
        return df

    def _get_position_count_draftees(self, year: int = 2020):
        df = self._get_draft_list(year)
        print(df['FantPos'].value_counts())

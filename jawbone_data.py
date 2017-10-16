import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from time import strptime, strftime
import statsmodels.api as sm

class JawboneData():
    def __init__(self, year):
        csv_file = year + '.csv'
        df = pd.read_csv(csv_file)

        # processing and cleaning jawbone data
        df_data = pd.DataFrame(
            [df.iloc[i,:] for i in df.index if df.iloc[i,:]['s_rem'] > 0])

        sleep_cols = [u's_light', u's_clinical_deep', u's_rem', u's_duration', u's_asleep_time']
        df_sleep = df_data[sleep_cols]
        df_sleep_mins = df_sleep[sleep_cols] / 60.

        df_sleep_percentages = df_sleep_mins.copy()
        for col in df_sleep_percentages.columns[:3]:
            df_sleep_percentages.loc[:,col] = 100. * df_sleep_mins.loc[:,col] / df_sleep_mins['s_duration']

        sleep_data_days = [strptime(year + '{:0=3}'.format(ind+1), '%Y%j') for ind in df_sleep_mins.index]

        self.sleep_cols = sleep_cols
        self.stage_cols = [u's_light', u's_clinical_deep', u's_rem']
        self.df_sleep_mins = df_sleep_mins
        self.df_sleep_percentages = df_sleep_percentages
        self.sleep_data_days = sleep_data_days

        # processing and cleaning lifestyle data
        df_lifestyle = pd.read_csv('lifestyle_variables.csv')

        lifestyle_var_names = list(df_lifestyle.columns[1:])

        date_after_formatted = ['/'.join([('0' * (2-len(s)) + s) for s in row])
          for row in [s.split('/') for s in df_lifestyle['date_after']]
          ]

        df_lifestyle['date_after'] = date_after_formatted

        day_of_year = [strptime(s,'%m/%d/%y').tm_yday - 1
                       for s in df_lifestyle['date_after']]

        df_lifestyle['day_of_year'] = day_of_year
        df_lifestyle = df_lifestyle.set_index('day_of_year')

        self.df_lifestyle = df_lifestyle

        # joining jawbone data to lifestyle data
        df_sleep_mins_full = df_sleep_mins.join(
            df_lifestyle, how='inner'
            ).drop('date_after', axis=1)

        df_sleep_percentages_full = df_sleep_percentages.join(
            df_lifestyle, how='inner'
            ).drop('date_after', axis=1)

        self.df_sleep_mins_full = df_sleep_mins_full
        self.df_sleep_percentages_full = df_sleep_percentages_full

        # computing a proxy for REM latency
        lr_rem = sm.OLS(df_sleep_mins['s_rem'], sm.add_constant(df_sleep_mins['s_duration'])).fit()
        rem_latency =  lr_rem.fittedvalues - df_sleep_mins['s_rem']

        df_sleep_mins_lat = df_sleep_mins.copy()
        df_sleep_mins_lat['rem_lat'] = rem_latency

        df_sleep_mins_full_lat = df_sleep_mins_lat.join(
            df_lifestyle, how='inner'
            ).drop('date_after', axis=1)

        self.df_sleep_mins_full_lat = df_sleep_mins_full_lat

    def summary_statistics(self):
        pd.set_option('precision',1)

        print 'Summary statistics for minutes spent in each phase\n'
        print self.df_sleep_mins[self.stage_cols].describe()

        print ''
        print 'Summary statistics for minutes of total sleep time\n'
        print self.df_sleep_mins[['s_duration']].describe()

        print ''
        print 'Summary statistics for time of sleep onset (midnight = 0)\n'
        print self.df_sleep_mins[['s_asleep_time']].describe()

        print ''
        print 'Summary statistics for percent of sleep spent in each phase\n'
        print self.df_sleep_percentages[self.stage_cols].describe()

        print ''
        print 'Summary statistics for lifestyle variables\n'
        print self.df_lifestyle.describe()

    def time_series_plots(self):
        plt.style.use('ggplot')

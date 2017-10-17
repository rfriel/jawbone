import numpy as np
import pandas as pd

from time import strptime, strftime
import statsmodels.api as sm

import warnings

class JawboneData():
    def __init__(self, year):
        csv_file = year + '.csv'
        try:
            df = pd.read_csv(csv_file)
        except IOError:
            print 'File {} not found.'.format(csv_file)

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
        self.lifestyle_flag = False
        csv_file = 'lifestyle_variables.csv'
        try:
            df_lifestyle = pd.read_csv(csv_file)
            self.lifestyle_flag = True
        except IOError:
            msg = 'File {} not found.  Lifestyle variable computations will not be performed.'.format(csv_file)
            warnings.warn(msg)

        if self.lifestyle_flag:
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
            self.lifestyle_var_names = lifestyle_var_names

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

        if self.lifestyle_flag:
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

        if self.lifestyle_flag:
            print ''
            print 'Summary statistics for lifestyle variables\n'
            print self.df_lifestyle.describe()

    def time_series_plots(self):
        import matplotlib.pyplot as plt

        plt.style.use('ggplot')

        plt.figure(figsize=(10,20))

        plt.subplot(211)
        for col in self.df_sleep_mins.columns[:3]:
            plt.plot(self.df_sleep_mins.loc[:,col],'o-',label=col[2:])
        plt.legend();
        plt.title('Minutes of each phase', size=16);
        plt.yticks(size=16)
        plt.xticks(self.df_sleep_mins.index[0::3],
                   [strftime('%m/%d', st) for st in self.sleep_data_days],
                  rotation=45, size=16);

        plt.subplot(212)
        for col in self.df_sleep_percentages.columns[:3]:
            plt.plot(self.df_sleep_percentages.loc[:,col],'o-',label=col[2:])
        plt.legend();
        plt.title('% of each phase', size=16);
        plt.yticks(size=16)
        plt.xticks(self.df_sleep_percentages.index[0::3],
                   [strftime('%m/%d', st) for st in self.sleep_data_days],
                  rotation=45, size=16);

        plots_file = 'time_series_plots.pdf'
        plt.savefig(plots_file)
        print 'Saved time series plots to {}'.format(plots_file)

    def regressions(self):
        if not self.lifestyle_flag:
            raise AttributeError('Cannot perform regressions because no lifestyle data was found when this object was created.')
        # regressions that treat independent vars as continuous
        cont_X  = self.df_sleep_mins_full[['s_asleep_time', 's_duration'] + self.lifestyle_var_names]

        tst_only_X = self.df_sleep_mins_full[['s_duration']]

        cont_Y = self.df_sleep_mins_full[['s_light', 's_clinical_deep', 's_rem']]

        lr_rem = sm.OLS(cont_Y['s_rem'], sm.add_constant(cont_X)).fit()
        lr_deep = sm.OLS(cont_Y['s_clinical_deep'], sm.add_constant(cont_X)).fit()
        lr_light = sm.OLS(cont_Y['s_light'], sm.add_constant(cont_X)).fit()

        lr_tst = sm.OLS(cont_X['s_duration'],
                           sm.add_constant(cont_X.drop('s_duration',axis=1))
                          ).fit()

        self.lr_rem = lr_rem
        self.lr_deep = lr_deep
        self.lr_light = lr_light
        self.lr_tst = lr_tst

        self.regression_names = ['REM sleep time (min)',
                                 'deep sleep time (min)',
                                 'light sleep time (min)',
                                 'total sleep time (min)']

        cont_regressions = [self.lr_rem, self.lr_deep, self.lr_light, self.lr_tst]

        pd.set_option('precision',3)

        for lr, name in zip(cont_regressions, self.regression_names):
            print 'Regression results for {}\n'.format(name)
            print lr.summary()
            pvals = lr.pvalues[self.lifestyle_var_names]
            print '\n\nP values for lifestyle effect coefficients:'
            print pvals
            print '\n\n'

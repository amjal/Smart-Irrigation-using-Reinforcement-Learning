import pandas
import numpy
from sklearn.cluster import OPTICS
import math
from matplotlib import pyplot as plt
from FileOperations import FileOperation


class SoilDataAnalyzer:
    dispatcher = {'mean': pandas.Series.mean, 'count': pandas.Series.count, 'std': pandas.Series.std}
    df = pandas.DataFrame([])

    def __init__(self, file_operator):
        self.df = pandas.read_csv(file_operator.path, dtype={'doy': 'int64'})
    def sm_avg_over_files(self, file_operator):
        # Given an instance of FileOperation with a specified path, this method calculates
        # average sm over all data files in that path
        sm = numpy.array([])
        csvs = file_operator.list_files(file_operator.path)
        for csv_file in csvs:
            # read a pandas data frame
            csv_data = pandas.read_csv(file_operator.path + csv_file)
            # add read pandas data frame's sm information to the existing numpy array
            sm = numpy.concatenate((sm, csv_data.iloc[:, 6].to_numpy()))
        # delete all nans from data set
        sm = sm[~pandas.isnull(sm)]
        return numpy.mean(sm), numpy.median(sm)

    def month2season(self):
        # Convert months to season in object's dataframe
        self.df.loc[(self.df['month'] == 1) | (self.df['month'] == 2) |
                    (self.df['month'] == 12), 'season'] = 'winter'
        self.df.loc[(self.df['month'] == 3) | (self.df['month'] == 4) |
                    (self.df['month'] == 5), 'season'] = 'spring'
        self.df.loc[(self.df['month'] == 6) | (self.df['month'] == 7) |
                    (self.df['month'] == 8), 'season'] = 'summer'
        self.df.loc[(self.df['month'] == 9) | (self.df['month'] == 10) |
                    (self.df['month'] == 11), 'season'] = 'autumn'

    # visualizes data based on parameters given. For networks parameter, an empty list means all the networks
    def visualizer(self, time_unit, time_range, plotted_value, networks, save_path):
        # In the next two lines, group the data by 'Network' and time unit given.
        # for each group, apply the function needed to derive the values
        gp = self.df.groupby(['Network', time_unit])['sm_5']
        processed_grouped_data = gp.apply(self.dispatcher[plotted_value]).reset_index()
        # Only keep the data that is in the given time_range
        final_data = processed_grouped_data[processed_grouped_data[time_unit].isin(time_range)]
        # If the caller has explicitly mentioned the stations they want, only keep those
        if len(networks) > 0:
            final_data = final_data[final_data['Network'].isin(networks)]
        # Put all the data corresponding to different stations into a list
        stations_data = [x[1] for x in final_data.groupby('Network')]
        # Plot all stations' data and label them
        for data in stations_data:
            m = ''
            if len(data[time_unit]) < 100:
                m = '.'
            plt.plot(data[time_unit], data['sm_5'], label=data['Network'].iloc[0], marker=m)
        plt.xlabel(time_unit)
        plt.ylabel(plotted_value)
        plt.grid(True)
        plt.legend(loc='best')
        plt.savefig(save_path)
        plt.show()

    def type1_cluster(self):
        # Given an instance of FileOperation with a specified path, this method this method reads the data
        # into a dataframe clusters the data based on station geographical proximity,
        # far stations' data are cut-off and for each remaining   station, the average of sm is
        # calculated based and categorized based on season and year, returns output as a new dataframe
        # Sort df by Network so that the values are grouped together based
        # on 'Network' and coherent with re-indexed lat_means
        self.df.sort_values('Network', inplace=True)
        # Re-index dataframe
        self.df.reset_index(inplace=True, drop=True)
        # Calculate mean of each network station and put into lat_mean
        lat_mean = self.df.groupby('Network')['lat'].mean()
        # Re-index and resize lat_mean so that we can subtract it from df['lat']
        stretched_lat_mean = lat_mean[self.df['Network']].reset_index(drop=True)
        # Let's make a new df with rows that have far 'lat' values deleted
        self.df = self.df.loc[abs(self.df['lat'] - stretched_lat_mean) < 2]
        # Re-index dataframe
        self.df.reset_index(inplace=True, drop=True)
        # Now do the whole thing over again for 'lon' column
        lon_mean = self.df.groupby('Network')['lon'].mean()
        stretched_lon_mean = lon_mean[self.df['Network']].reset_index(drop=True)
        self.df = self.df.loc[abs(self.df['lon'] - stretched_lon_mean) < 2]
        self.df.reset_index(inplace=True, drop=True)
        # Now the data with close-together stations are kept and the rest removed
        # Only keep stations with a data set larger than 9000
        counts = self.df.groupby('Network')['sm_5'].count()
        stretched_counts = counts[self.df['Network']].reset_index(drop=True)
        self.df = self.df.loc[stretched_counts > 9000]
        self.df.reset_index(drop=True, inplace=True)
        # Turn the Groupby dataframe into a normal data frame with normal indices
        output_df = pandas.DataFrame({'smAVG': self.df.groupby(['Network', 'year', 'season'])['sm_5'].mean()}).reset_index()
        # Add needed columns to the dataframe
        output_df['smSTD'] = self.df.groupby(['Network', 'year', 'season'])['sm_5'].std().reset_index(drop=True)
        output_df['stationCount'] = counts[output_df['Network']].reset_index(drop=True)
        output_df['seasonCount'] = self.df.groupby(['Network', 'year', 'season'])['sm_5'].count().reset_index(drop=True)
        output_df['stationOriginLat'] = lat_mean[output_df['Network']].reset_index(drop=True)
        output_df['stationOriginLon'] = lon_mean[output_df['Network']].reset_index(drop=True)
        return output_df

    def type2_cluster(self):
        # Drop stationID column
        locations = numpy.array([self.df['lat'], self.df['lon']]).transpose()
        labels = OPTICS(eps=5*math.sqrt(2), min_samples=7000).fit_predict(locations[0:10000, :])
        pandas.DataFrame(labels).to_csv('/home/amir/python_workspace/soil moisture 2018-2019/Sorted_data/labels.txt')


file_operator = FileOperation()
file_operator.path = "test_path/best_sorted_data.csv"
da = SoilDataAnalyzer(file_operator)
for i in range(0, 12):
    da.visualizer('doy', numpy.arange(i*30, (i+1)*30), 'mean', ['snotel', 'scan', 'OKM', 'crn', 'WTM'], '../month'+str(i))


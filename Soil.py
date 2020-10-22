import numpy as np
from matplotlib import pyplot as plt

# TODO for all the factors to be realistic, they need to reflect the time unit's length
# TODO change name from mutation to change


class Soil:
    all_data = []
    irrigation_iteration = 0
    LAYERS_SIZE = np.array([])
    INITIAL_LAYERS_SIZE = np.array([])
    NUMBER_OF_LAYERS = 3

    LAYERS_PENETRATION_MEAN = np.array([])
    LAYERS_PENETRATION_VAR = np.array([])
    LAYERS_PENETRATION = np.array([])

    LAYERS_WATER_LOSS_MEAN = np.array([])
    LAYERS_WATER_LOSS_VAR = np.array([])
    LAYERS_WATER_LOSS = np.array([])
    SEASON_CHANGING_WATER_LOSS = {'spring': -0.010, 'summer': -0.012, 'autumn': -0.008, 'winter': -0.005}
    DAILY_CHANGING_WATER_LOSS = np.array([])

    LAYERS_MOISTURE = np.array([])
    # Specific properties of Soil
    VALVE_CAPACITY = 40
    IS_WATERING = False
    RAIN_CHANCE = 0.005
    SEASON_CHANGING_RAIN_MUTATION = {'spring': 0.01, 'summer': 0.0, 'autumn': +0.005, 'winter': +0.01}
    DAY_WATER_LOSS_INCREASE_BASE = 0.01
    DAY_WATER_LOSS_INCREASE_ERROR = 0.008

    input_water = 0

    def __init__(self, time):
        self.time = time

        # penetrations are between 1 to 7 percent with 0.5 percent variance
        self.LAYERS_PENETRATION_MEAN = np.random.rand(self.NUMBER_OF_LAYERS)*(6/100) + 1/100
        self.LAYERS_PENETRATION_VAR = np.random.rand(self.NUMBER_OF_LAYERS)/200

        self.LAYERS_MOISTURE = np.random.rand(self.NUMBER_OF_LAYERS)

        self.INITIAL_LAYERS_SIZE = np.array([np.random.rand()*50 for i in range(self.NUMBER_OF_LAYERS)])

        # in days
        self.TIME_TO_DOUBLE_ROOT_ZONE = np.random.normal(10, 1)


        # Water loss means initiation
        raw_loss_factors = np.random.normal(0, self.NUMBER_OF_LAYERS / 4, 1000)
        bins = np.arange(-self.NUMBER_OF_LAYERS / 2, self.NUMBER_OF_LAYERS / 2 + 1)
        self.LAYERS_WATER_LOSS_MEAN = np.histogram(raw_loss_factors, bins, density=True)[0]
        # This reduces the differences
        self.LAYERS_WATER_LOSS_MEAN **= 3
        minimum_loss_rate_coeff = 1
        f = minimum_loss_rate_coeff - max(self.LAYERS_WATER_LOSS_MEAN)
        self.LAYERS_WATER_LOSS_MEAN += f

        # Daily water loss factors
        raw_loss_factors = np.random.normal(0, self.time.day_time_limit / 4, 1000)
        bins = np.arange(-self.time.day_time_limit / 2, self.time.day_time_limit / 2 + 1)
        self.DAILY_CHANGING_WATER_LOSS = np.histogram(raw_loss_factors, bins, density=True)[0]
        maximum_loss_rate = 0.002
        f = maximum_loss_rate/max(self.DAILY_CHANGING_WATER_LOSS)
        self.DAILY_CHANGING_WATER_LOSS *= f

        # Water loss var initiation
        self.LAYERS_WATER_LOSS_VAR = np.random.rand(self.NUMBER_OF_LAYERS)/1000
        #plt.plot(list(bins[0:len(bins) - 1]), self.LAYERS_WATER_LOSS)
        #plt.show()
        #self.LAYERS_PENETRATION = [0.5, 0.5, 0.5, 0.5]
        #self.LAYERS_MOISTURE = [0.7, 0.6, 0.5]
        #self.LAYERS_SIZE = [70, 80, 90, 90]

    def __str__(self):
        out_str = ""
        out_str += 'TIME: '+str(self.time.time_of_day) + ' , DAY_OF_MONTH: '+str(self.time.day_of_month)+' , MONTH: '
        out_str += str(self.time.month)+' , SEASON: '+str(self.time.season)+'\n'
        for j in range(0, self.NUMBER_OF_LAYERS):
            out_str += str(self.LAYERS_MOISTURE[j]) + " , " + str(self.LAYERS_SIZE[j])\
                  + " , " + str(self.LAYERS_PENETRATION[j]) + '\n'
        out_str += "mean: "+str(np.mean(self.LAYERS_MOISTURE))+"\n"
        out_str += '\n'
        return out_str

    def visualizer(self, time_unit):
        mean_dispatcher = {'day': self.time.day_time_limit, 'month': self.time.day_time_limit*30,
                           'season': self.time.day_time_limit*90, 'time': 1}
        all_data = np.array(self.all_data)
        all_data = all_data.reshape((int(self.irrigation_iteration/mean_dispatcher[time_unit]),
                                     int(mean_dispatcher[time_unit]), self.NUMBER_OF_LAYERS))
        avg_over_unit = np.mean(all_data, axis=1)
        time_axis = np.arange(0, all_data.shape[0])
        marker = ""
        if len(time_axis) < 100:
            marker = "."
        for i in range(0, self.NUMBER_OF_LAYERS):
            plt.plot(time_axis, avg_over_unit[:, i], label='layer '+str(i), marker=marker)
        avg_of_all_layers = np.mean(avg_over_unit, axis=1)
        plt.plot(time_axis, avg_of_all_layers, label='avg', marker=marker)
        plt.xlabel('time')
        plt.ylabel('moisture')
        plt.grid(True)
        plt.legend()
        plt.show()

    def penetration_mutation(self):
        self.LAYERS_PENETRATION = np.random.normal(self.LAYERS_PENETRATION_MEAN, self.LAYERS_PENETRATION_VAR)

    def layers_size_change(self):
        self.LAYERS_SIZE = self.INITIAL_LAYERS_SIZE*(3 - 2/((1/self.TIME_TO_DOUBLE_ROOT_ZONE)*self.time.day_of_month+1))

    def water_loss_mutation(self):
        self.LAYERS_WATER_LOSS = self.LAYERS_WATER_LOSS_MEAN + self.SEASON_CHANGING_WATER_LOSS[self.time.season]
        self.LAYERS_WATER_LOSS -= self.DAILY_CHANGING_WATER_LOSS[self.time.time_of_day]
        self.LAYERS_WATER_LOSS = np.random.normal(self.LAYERS_WATER_LOSS, self.LAYERS_WATER_LOSS_VAR)

    def rain_operation(self):
        if not self.rain.active:
            self.rain.start_rain(self.RAIN_CHANCE + self.SEASON_CHANGING_RAIN_MUTATION[self.time.season])
        if self.rain.active:
            self.input_water += self.rain.rain()

    def make_mutation(self):
        self.penetration_mutation()
        self.water_loss_mutation()
        self.layers_size_change()

    def handle_input_water(self):
        if self.input_water > self.LAYERS_SIZE[0] * (1 - self.LAYERS_MOISTURE[0]):
            self.input_water -= self.LAYERS_SIZE[0] * (1 - self.LAYERS_MOISTURE[0])
            self.LAYERS_MOISTURE[0] = 1.0
        else:
            self.LAYERS_MOISTURE[0] = (self.LAYERS_SIZE[0] * self.LAYERS_MOISTURE[0] +
                                       self.input_water) / self.LAYERS_SIZE[0]
            self.input_water = 0

    def handle_penetration(self, penetration_speed):
        # other layers
        for k in range(penetration_speed):
            for i in range(self.NUMBER_OF_LAYERS-1, 0, -1):
                passed_water = self.LAYERS_MOISTURE[i-1]*self.LAYERS_SIZE[i-1]*min(self.LAYERS_PENETRATION[i-1], 1)
                if passed_water > self.LAYERS_SIZE[i]*(1-self.LAYERS_MOISTURE[i]):
                    passed_water = self.LAYERS_SIZE[i]*(1-self.LAYERS_MOISTURE[i])
                self.LAYERS_MOISTURE[i] += passed_water/self.LAYERS_SIZE[i]
                self.LAYERS_MOISTURE[i-1] -= passed_water/self.LAYERS_SIZE[i-1]

    def handle_water_loss(self):
        self.LAYERS_MOISTURE *= self.LAYERS_WATER_LOSS

    def irrigate(self):
        self.all_data.append(self.LAYERS_MOISTURE.copy())
        self.make_mutation()
        if self.IS_WATERING:
            self.input_water += self.VALVE_CAPACITY
        self.handle_input_water()
        self.handle_penetration(1)
        self.handle_water_loss()
        self.irrigation_iteration += 1



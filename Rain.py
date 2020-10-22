import numpy
import random
import time


class Rain:
    speed = numpy.nan
    intensity = numpy.nan
    duration = 0
    time_limit = numpy.nan
    active = False

    def start_rain(self, chance):
        if numpy.random.rand() < chance:
            self.active = True
            self.duration = 0
            self.time_limit = int((1 + random.random()/5 - 0.1)*self.time_limit)

    def __init__(self, speed, intensity, time_limit):
        self.speed = speed
        self.intensity = intensity
        self.time_limit = time_limit
        random.seed(time.time())

    def rain(self):
        self.duration = self.duration+1
        if self.duration == self.time_limit:
            self.active = False
        else:
            self.speed = self.mutate_variable(self.speed, 2)
            self.intensity = self.mutate_variable(self.intensity, 2)
        return self.intensity

    # mutation_count says how many mutations we want over the duration
    def mutate_variable(self, var, mutation_count):
        mutation_factor = self.time_limit/mutation_count
        if mutation_factor != 0 and self.duration % mutation_factor == 0:
            var = (2*random.random()-1)*2/3*var + var
        else:
            var = (2*random.random()-1)/30*var + var
        return var


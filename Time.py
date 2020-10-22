class ArtificialTime:
    seasons = ['winter', 'winter', 'spring', 'spring', 'spring', 'summer', 'summer', 'summer', 'autumn', 'autumn',
               'autumn', 'winter']
    is_night = False

    def __init__(self, **kwargs):
        self.time_of_day = kwargs.get('time_of_day', 0)
        self.month = kwargs.get('month', 0)
        self.season = kwargs.get('season', 'winter')
        self.day_time_limit = kwargs.get('day_time_limit', 240)
        self.day_of_month = kwargs.get('day_of_month', 0)

    def increase_time(self):
        self.time_of_day += 1
        if self.time_of_day >= self.day_time_limit:
            self.time_of_day = 0
            self.day_of_month += 1
            if self.time_of_day < 10/24*self.day_time_limit:
                self.is_night = True
            else:
                self.is_night = False
            if self.day_of_month >= 30:
                self.day_of_month = 0
                self.month += 1
                if self.month >= 12:
                    self.month = 0
                self.season = self.seasons[self.month]


t1 = ArtificialTime()
t2 = ArtificialTime()

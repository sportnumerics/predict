
class Model:
    def train(self, samples):
        team_info = [None]*self.n_teams

        def default_info():
            return {'count': 0, 'for': 0, 'against': 0}

        def add_points_for(team, points):
            current_info = team_info[team] or default_info()
            current_info['for'] += sample[2]
            current_info['count'] += 0.5
            team_info[team] = current_info

        def add_points_against(team, points):
            current_info = team_info[team] or default_info()
            current_info['against'] += sample[2]
            current_info['count'] += 0.5
            team_info[team] = current_info

        for sample in samples:
            add_points_for(sample[0], sample[2])
            add_points_against(sample[1], sample[2])

        self.average_points_for = [None]*self.n_teams
        self.average_points_against = [None]*self.n_teams
        for i, info in enumerate(team_info):
            self.average_points_for[i] = info['for'] / info['count']
            self.average_points_against[i] = info['against'] / info['count']

    def predict(self, i, j):
        return (self.average_points_for[i] + self.average_points_against[j]) / 2

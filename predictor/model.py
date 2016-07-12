import numpy as np
import math

class Model:
    def __init__(self, n_factors, n_teams, gamma=0.001):
        self.gamma = gamma
        self.n_factors = n_factors
        self.n_teams = n_teams
        self.offensive_factors = 0.1*np.ones([n_factors, n_teams])
        self.defensive_factors = 0.1*np.ones([n_factors, n_teams])

    def calculate_averages(self, samples):
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

    def predict_baseline(self, i, j):
        return (self.average_points_for[i] + self.average_points_against[j]) / 2

    def predict(self, i, j):
        return np.dot(self.offensive_factors[:,i], self.defensive_factors[:,j]) + self.predict_baseline(i,j)

    def train_once(self, sample, i_factor):
        i = sample[0]
        j = sample[1]
        err = (sample[2] - self.predict(i,j))
        delta = self.gamma * err
        of = self.offensive_factors[i_factor, i]
        self.offensive_factors[i_factor, i] += delta * self.defensive_factors[i_factor, j]
        self.defensive_factors[i_factor, j] += delta * of
        return err**2

    def train_one_pass(self, samples, i_factor):
        sum_err = 0
        for sample in samples:
            sum_err += self.train_once(sample, i_factor)
        return sum_err

    def train_one_factor(self, samples, i_factor, rel_tol, max_iterations):
        last_err = 1e10
        for i in range(0, max_iterations):
            err = self.train_one_pass(samples, i_factor)
            avg_err = math.sqrt(err / len(samples))
            print('Average error: {}'.format(avg_err))
            if (abs(err - last_err) < rel_tol):
                break
            else:
                last_err = err

    def train(self, samples, rel_tol=1e-2, max_iterations=10000):
        self.calculate_averages(samples)

        for i_factor in range(0, self.n_factors):
            self.train_one_factor(samples, i_factor, rel_tol, max_iterations)

    def dump(self):
        return {
            'offense': self.offensive_factors.transpose().tolist(),
            'defense': self.defensive_factors.transpose().tolist()
        }

    def predict_samples(self, samples):
        results = []
        for sample in samples:
            predicted_result = self.predict(sample[0], sample[1])
            results.append({'team': sample[0], 'opponent': sample[1], 'result': sample[2], 'prediction': predicted_result})
        return results

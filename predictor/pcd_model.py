import numpy as np
import math

class Model:
    def __init__(self, n_factors, n_teams, baseline_model, gamma=0.01, initial_value=0.01):
        self.gamma = gamma
        self.n_factors = n_factors
        self.n_teams = n_teams
        self.K = 0.2
        self.initial_value = initial_value
        self.offensive_factors = 0.0*np.ones([n_factors, n_teams])
        self.defensive_factors = 0.0*np.ones([n_factors, n_teams])
        self.baseline_model = baseline_model

    def predict(self, i, j):
        return np.dot(self.offensive_factors[:,i], self.defensive_factors[:,j]) + self.baseline_model.predict(i,j)

    def train_once(self, sample, i_factor):
        i = sample[0]
        j = sample[1]
        err = (sample[2] - self.predict(i,j))
        df = self.defensive_factors[i_factor, j]
        of = self.offensive_factors[i_factor, i]
        self.offensive_factors[i_factor, i] += self.gamma * ( err * df - self.K * of )
        self.defensive_factors[i_factor, j] += self.gamma * ( err * of - self.K * df )
        return err**2

    def train_one_pass(self, samples, i_factor):
        sum_err = 0
        for sample in samples:
            sum_err += self.train_once(sample, i_factor)
        return sum_err

    def initialize_factor(self, i_factor):
        self.offensive_factors[i_factor,:] = self.initial_value*np.ones([self.n_teams])
        self.defensive_factors[i_factor,:] = self.initial_value*np.ones([self.n_teams])

    def train_one_factor(self, samples, i_factor, rel_tol, max_iterations):
        history = []
        sample_norm = np.linalg.norm(np.array(samples)[:,2])
        self.initialize_factor(i_factor)
        for i in range(0, max_iterations):
            err = self.train_one_pass(samples, i_factor)
            avg_rel_err = math.sqrt(err)/sample_norm
            history.append(avg_rel_err)
            if (avg_rel_err < rel_tol):
                break
        return history

    def train(self, samples, rel_tol=1e-4, max_iterations=2000):
        print("n: {}, K: {}, tol: {}, i: {}, init: {}, gamma: {}".format(self.n_factors, self.K, rel_tol, max_iterations, self.initial_value, self.gamma))
        history = []
        for i_factor in range(0, self.n_factors):
            history.extend(self.train_one_factor(samples, i_factor, rel_tol, max_iterations))
        return history

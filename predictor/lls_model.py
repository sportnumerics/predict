from scipy.sparse import linalg


class Model:
    def __init__(self):
        self.ratings = None

    def train(self, coefficients, constants):
        x, istop, itn, r1norm, r2norm, anorm, acond, arnorm, xnorm, var = linalg.lsqr(coefficients, constants, damp=1)

        self.ratings = x

    def predict(self, i, j):
        return self.ratings[i] - self.ratings[j + int(len(self.ratings)/2)]

    def corrected_ratings(self):
        return self.ratings

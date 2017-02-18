import sys, os

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, 'vendored'))

from predictor.run import run

if __name__ == "__main__":
    run()

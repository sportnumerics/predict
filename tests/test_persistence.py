import unittest
from predictor.persistence import split_teams_into_divs

class TestPersistence(unittest.TestCase):

  def test_ranking(self):
    teams = [
      team('team-1', 'm1', 0.0),
      team('team-2', 'm1', -1.0),
      team('team-3', 'm1', -2.0),
      team('team-4', 'm2', 0.0),
      team('team-5', 'm1', 0.0)
    ]

    teams_dict = {team['id']: team for team in teams}

    teams_by_div = split_teams_into_divs(teams_dict)

    m1 = {team['id']: team for team in teams_by_div['m1']}

    self.assertEqual(m1['team-1']['rank'], 1)
    self.assertEqual(m1['team-5']['rank'], 1)
    self.assertEqual(m1['team-2']['rank'], 3)
    self.assertEqual(m1['team-3']['rank'], 4)


def team(id, div, overall):
  team = {
    'id': id,
    'div': div,
    'ratings': {
      'overall': overall
    }
  }

  return team
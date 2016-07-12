import copy

def calculate_ratings(team_map, model):
    # rating is determined by how well a team would do if it played all other
    # opponents. total score differential vs all opponents
    n_teams = len(team_map['indicies_to_teams'])

    results = []

    for i in range(0, n_teams):
        rank = 0
        for j in range(i, n_teams):
            if (i != j):
                rank += model.predict(i,j) - model.predict(j,i)
        results.append({
            'team': team_map['indicies_to_teams'][i],
            'rank': rank
        })

    return sorted(results, key=lambda x: -x['rank'])

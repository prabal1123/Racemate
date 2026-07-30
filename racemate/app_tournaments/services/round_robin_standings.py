from ..models import Match, TournamentCategory


def calculate_round_robin_standings(tournament_category):
    """
    Compute Played / Won / Lost standings for a
    Round Robin tournament category.

    Ranking order:
    1. Most wins
    2. Best set difference (sets_won - sets_lost)
    3. Best point difference (points_for - points_against)
    """
    entries = list(
        tournament_category.entries
        .filter(status__code__iexact="confirmed")
    )

    stats = {
        entry.id: {
            "entry": entry,
            "played": 0,
            "won": 0,
            "lost": 0,
            "sets_won": 0,
            "sets_lost": 0,
            "points_for": 0,
            "points_against": 0,
        }
        for entry in entries
    }

    matches = (
        Match.objects
        .filter(
            tournament_round__tournament_category=tournament_category,
            tournament_round__is_knockout=False,
            winner__isnull=False,
        )
        .select_related("entry_one", "entry_two", "winner")
        .prefetch_related("sets")
    )

    for match in matches:
        entry_one_id = match.entry_one_id
        entry_two_id = match.entry_two_id

        # Skip if an entry was withdrawn after fixtures
        # were generated.
        if (
            entry_one_id not in stats
            or entry_two_id not in stats
        ):
            continue

        completed_sets = [
            match_set
            for match_set in match.sets.all()
            if match_set.is_completed
        ]

        entry_one_sets_won = sum(
            1
            for match_set in completed_sets
            if match_set.winner_id == entry_one_id
        )

        entry_two_sets_won = sum(
            1
            for match_set in completed_sets
            if match_set.winner_id == entry_two_id
        )

        entry_one_points = sum(
            match_set.entry_one_score
            for match_set in completed_sets
        )

        entry_two_points = sum(
            match_set.entry_two_score
            for match_set in completed_sets
        )

        stats[entry_one_id]["played"] += 1
        stats[entry_two_id]["played"] += 1

        stats[entry_one_id]["sets_won"] += entry_one_sets_won
        stats[entry_one_id]["sets_lost"] += entry_two_sets_won
        stats[entry_two_id]["sets_won"] += entry_two_sets_won
        stats[entry_two_id]["sets_lost"] += entry_one_sets_won

        stats[entry_one_id]["points_for"] += entry_one_points
        stats[entry_one_id]["points_against"] += entry_two_points
        stats[entry_two_id]["points_for"] += entry_two_points
        stats[entry_two_id]["points_against"] += entry_one_points

        if match.winner_id == entry_one_id:
            stats[entry_one_id]["won"] += 1
            stats[entry_two_id]["lost"] += 1
        else:
            stats[entry_two_id]["won"] += 1
            stats[entry_one_id]["lost"] += 1

    standings = list(stats.values())

    standings.sort(
        key=lambda row: (
            -row["won"],
            -(row["sets_won"] - row["sets_lost"]),
            -(row["points_for"] - row["points_against"]),
        )
    )

    for rank, row in enumerate(standings, start=1):
        row["rank"] = rank

    return standings
import math
import random

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from itertools import combinations
from ..models import (
    Match,
    MatchStatus,
    TournamentCategory,
    TournamentRound,
)


def next_power_of_two(value):
    """
    Return the smallest power of two greater than
    or equal to the supplied value.

    Examples:
    3  -> 4
    5  -> 8
    11 -> 16
    16 -> 16
    """
    if value < 1:
        raise ValidationError(
            "Entry count must be at least 1."
        )

    return 1 << (value - 1).bit_length()


def seeded_slot_order(bracket_size):
    """
    Return the standard seed order for bracket slots.

    Example for an 8-slot bracket:

    Slot 1 -> Seed 1
    Slot 2 -> Seed 8
    Slot 3 -> Seed 4
    Slot 4 -> Seed 5
    Slot 5 -> Seed 2
    Slot 6 -> Seed 7
    Slot 7 -> Seed 3
    Slot 8 -> Seed 6

    Result:
    [1, 8, 4, 5, 2, 7, 3, 6]
    """
    if (
        bracket_size < 2
        or bracket_size & (bracket_size - 1)
    ):
        raise ValidationError(
            "Bracket size must be a power of two "
            "and must be at least 2."
        )

    order = [1]

    while len(order) < bracket_size:
        new_size = len(order) * 2

        order = [
            seed_number
            for existing_seed in order
            for seed_number in (
                existing_seed,
                new_size + 1 - existing_seed,
            )
        ]

    return order


def get_round_name(bracket_size, round_number):
    """
    Return the round name based on the number
    of participants remaining.

    Examples:
    16 participants -> Round of 16
    8 participants  -> Quarterfinal
    4 participants  -> Semifinal
    2 participants  -> Final
    """
    participants_remaining = (
        bracket_size // (2 ** (round_number - 1))
    )

    if participants_remaining == 2:
        return "Final"

    if participants_remaining == 4:
        return "Semifinal"

    if participants_remaining == 8:
        return "Quarterfinal"

    return f"Round of {participants_remaining}"


def get_bracket_side(match_index, total_matches):
    """
    Return the logical side of the bracket.

    top    -> top half
    bottom -> bottom half

    Final matches do not require a side.
    """
    if total_matches <= 1:
        return ""

    halfway_point = total_matches // 2

    if match_index < halfway_point:
        return Match.BracketSide.TOP

    return Match.BracketSide.BOTTOM


def validate_seeds(entries):
    """
    Validate seed values before generating the draw.

    Seeds must:

    - Be unique
    - Start from 1
    - Be consecutive
    - Not exceed the number of entries

    Valid:
    1, 2, 3, 4

    Invalid:
    1, 2, 4
    """
    seeded_entries = sorted(
        [
            entry
            for entry in entries
            if entry.seed is not None
        ],
        key=lambda entry: entry.seed,
    )

    seed_values = [
        entry.seed
        for entry in seeded_entries
    ]

    if len(seed_values) != len(set(seed_values)):
        raise ValidationError(
            "Two or more tournament entries have the same seed."
        )

    if any(seed < 1 for seed in seed_values):
        raise ValidationError(
            "Tournament seeds must start from 1."
        )

    if any(seed > len(entries) for seed in seed_values):
        raise ValidationError(
            "A seed cannot be greater than the number "
            "of confirmed entries."
        )

    expected_seeds = list(
        range(1, len(seed_values) + 1)
    )

    if seed_values != expected_seeds:
        raise ValidationError(
            "Seeds must be consecutive and start from 1. "
            "Example: 1, 2, 3, 4."
        )

    return seeded_entries


def build_knockout_slots(entries, bracket_size):
    """
    Place seeded and unseeded entries into bracket slots.

    Rules:

    - Seeded entries use standard bracket positions.
    - Highest seeds receive byes first.
    - Remaining byes are assigned randomly.
    - Unseeded entries are placed randomly.
    - No first-round pair can be completely empty.
    """
    random_generator = random.SystemRandom()

    seeded_entries = validate_seeds(entries)

    unseeded_entries = [
        entry
        for entry in entries
        if entry.seed is None
    ]

    random_generator.shuffle(unseeded_entries)

    seed_order = seeded_slot_order(bracket_size)

    seed_to_slot = {
        seed_number: slot_index
        for slot_index, seed_number
        in enumerate(seed_order)
    }

    slots = [None] * bracket_size

    # Place seeded entries in standard positions.
    for entry in seeded_entries:
        slot_index = seed_to_slot[entry.seed]
        slots[slot_index] = entry

    bye_count = bracket_size - len(entries)

    # These slots remain empty because they represent byes.
    reserved_empty_slots = set()

    # Highest seeded entries receive byes first.
    top_seeded_bye_entries = seeded_entries[:bye_count]

    for entry in top_seeded_bye_entries:
        entry_slot = seed_to_slot[entry.seed]

        # Adjacent slots form one first-round pairing.
        opponent_slot = entry_slot ^ 1

        if slots[opponent_slot] is not None:
            raise ValidationError(
                f"Unable to assign a bye to seed {entry.seed}. "
                "Please verify the seed configuration."
            )

        reserved_empty_slots.add(opponent_slot)

    remaining_byes = (
        bye_count - len(top_seeded_bye_entries)
    )

    # When fewer seeded entries exist than byes,
    # assign remaining byes randomly.
    empty_pairs = []

    for pair_start in range(0, bracket_size, 2):
        first_slot = pair_start
        second_slot = pair_start + 1

        if (
            slots[first_slot] is None
            and slots[second_slot] is None
        ):
            empty_pairs.append(pair_start)

    random_generator.shuffle(empty_pairs)

    if len(empty_pairs) < remaining_byes:
        raise ValidationError(
            "Unable to create the required bye positions."
        )

    for pair_start in empty_pairs[:remaining_byes]:
        reserved_slot = (
            pair_start
            + random_generator.randrange(2)
        )

        reserved_empty_slots.add(reserved_slot)

    # Every non-reserved empty slot must receive
    # an unseeded entry.
    available_slots = [
        slot_index
        for slot_index, entry in enumerate(slots)
        if (
            entry is None
            and slot_index not in reserved_empty_slots
        )
    ]

    random_generator.shuffle(available_slots)

    if len(available_slots) != len(unseeded_entries):
        raise ValidationError(
            "The number of available bracket slots does not "
            "match the number of unseeded entries."
        )

    for slot_index, entry in zip(
        available_slots,
        unseeded_entries,
    ):
        slots[slot_index] = entry

    bye_entries = []

    # Confirm that every pair has either:
    # - two entries
    # - one entry and one bye
    for pair_start in range(0, bracket_size, 2):
        entry_one = slots[pair_start]
        entry_two = slots[pair_start + 1]

        if entry_one is None and entry_two is None:
            raise ValidationError(
                "Invalid bracket generated: one first-round "
                "pair contains no entries."
            )

        if entry_one is None:
            bye_entries.append(entry_two)

        elif entry_two is None:
            bye_entries.append(entry_one)

    return slots, bye_entries


def create_match(
    tournament_round,
    match_number,
    status,
    bracket_slot,
    bracket_side="",
    entry_one=None,
    entry_two=None,
):
    """
    Create and validate one Match record.
    """
    match = Match(
        tournament_round=tournament_round,
        match_number=match_number,
        entry_one=entry_one,
        entry_two=entry_two,
        status=status,
        bracket_slot=bracket_slot,
        bracket_side=bracket_side,
    )

    match.full_clean()
    match.save()

    return match


def create_knockout_rounds(
    tournament_category,
    bracket_size,
):
    """
    Create the complete knockout round structure.

    Example for 16 bracket slots:

    Round of 16
    Quarterfinal
    Semifinal
    Final
    """
    total_rounds = int(
        math.log2(bracket_size)
    )

    rounds = []

    for round_number in range(
        1,
        total_rounds + 1,
    ):
        tournament_round = TournamentRound.objects.create(
            tournament_category=tournament_category,
            name=get_round_name(
                bracket_size,
                round_number,
            ),
            round_number=round_number,
            is_knockout=True,
            is_active=True,
        )

        rounds.append(tournament_round)

    return rounds


def generate_knockout_draw(
    tournament_category,
    entries,
    scheduled_status,
):
    """
    Generate a complete knockout bracket.

    Real Round 1 matches are created immediately.

    Entries receiving byes skip Round 1 and are inserted
    directly into their correct Round 2 positions.

    Later rounds are created as empty match placeholders
    so that the complete bracket can be displayed.
    """
    entry_count = len(entries)

    bracket_size = next_power_of_two(
        entry_count
    )

    slots, bye_entries = build_knockout_slots(
        entries,
        bracket_size,
    )

    rounds = create_knockout_rounds(
        tournament_category,
        bracket_size,
    )

    total_rounds = len(rounds)

    matches_by_round = {}

    total_matches_created = 0
    round_one_matches_created = 0

    # Create empty match placeholders from Round 2 onward.
    for round_index in range(1, total_rounds):
        tournament_round = rounds[round_index]

        match_count = (
            bracket_size
            // (2 ** (round_index + 1))
        )

        round_matches = []

        for match_index in range(match_count):
            match = create_match(
                tournament_round=tournament_round,
                match_number=match_index + 1,
                status=scheduled_status,
                bracket_slot=match_index + 1,
                bracket_side=get_bracket_side(
                    match_index,
                    match_count,
                ),
            )

            round_matches.append(match)
            total_matches_created += 1

        matches_by_round[round_index + 1] = (
            round_matches
        )

    first_round = rounds[0]
    first_round_pair_count = bracket_size // 2

    first_round_matches = [
        None
    ] * first_round_pair_count

    for pair_index in range(
        first_round_pair_count
    ):
        first_slot = pair_index * 2
        second_slot = first_slot + 1

        entry_one = slots[first_slot]
        entry_two = slots[second_slot]

        bracket_side = get_bracket_side(
            pair_index,
            first_round_pair_count,
        )

        # Create a real first-round match.
        if entry_one and entry_two:
            match = create_match(
                tournament_round=first_round,
                match_number=pair_index + 1,
                status=scheduled_status,
                bracket_slot=pair_index + 1,
                bracket_side=bracket_side,
                entry_one=entry_one,
                entry_two=entry_two,
            )

            first_round_matches[pair_index] = match

            round_one_matches_created += 1
            total_matches_created += 1

            continue

        # An entry with a bye skips Round 1.
        bye_entry = entry_one or entry_two

        if bye_entry is None:
            raise ValidationError(
                "Invalid bracket generated: empty first-round pair."
            )

        if total_rounds < 2:
            raise ValidationError(
                "A bye cannot exist in a two-entry bracket."
            )

        next_round_match_index = pair_index // 2

        next_round_match = (
            matches_by_round[2]
            [next_round_match_index]
        )

        # Even-numbered source pair enters entry one.
        # Odd-numbered source pair enters entry two.
        if pair_index % 2 == 0:
            next_round_match.entry_one = bye_entry
            update_field = "entry_one"

        else:
            next_round_match.entry_two = bye_entry
            update_field = "entry_two"

        next_round_match.full_clean()
        next_round_match.save(
            update_fields=[update_field]
        )

    matches_by_round[1] = first_round_matches

    return {
        "bracket_size": bracket_size,
        "entry_count": entry_count,
        "bye_count": len(bye_entries),
        "bye_entries": bye_entries,
        "rounds": rounds,
        "rounds_created": len(rounds),
        "round_one_matches_created": (
            round_one_matches_created
        ),
        "total_matches_created": (
            total_matches_created
        ),
    }

def generate_round_robin_draw(
    tournament_category,
    entries,
    scheduled_status,
):
    """
    Generate one round-robin round.

    Every confirmed entry plays every other confirmed entry
    exactly once.

    Example with four entries:

    A vs B
    A vs C
    A vs D
    B vs C
    B vs D
    C vs D
    """
    if len(entries) < 2:
        raise ValidationError(
            "At least 2 confirmed entries are required "
            "to generate round-robin fixtures."
        )

    tournament_round = (
        TournamentRound.objects.create(
            tournament_category=tournament_category,
            name="Round Robin",
            round_number=1,
            is_knockout=False,
            is_active=True,
        )
    )

    matches = []

    for match_number, (
        entry_one,
        entry_two,
    ) in enumerate(
        combinations(entries, 2),
        start=1,
    ):
        match = create_match(
            tournament_round=tournament_round,
            match_number=match_number,
            status=scheduled_status,
            bracket_slot=match_number,
            bracket_side="",
            entry_one=entry_one,
            entry_two=entry_two,
        )

        matches.append(match)

    return {
        "fixture_type": "round_robin",
        "entry_count": len(entries),
        "rounds": [tournament_round],
        "rounds_created": 1,
        "matches_created": len(matches),
        "matches": matches,
        "bracket_size": None,
        "bye_count": 0,
        "round_one_matches_created": len(matches),
        "total_matches_created": len(matches),
    }

@transaction.atomic
def generate_fixtures(tournament_category):
    """
    Generate fixtures according to the category's fixture type.

    Supported fixture types:

    - Knockout
    - Round Robin
    """
    if not tournament_category.pk:
        raise ValidationError(
            "Tournament category must be saved before "
            "fixtures can be generated."
        )

    locked_category = (
        TournamentCategory.objects
        .select_for_update()
        .select_related(
            "tournament",
            "scoring_rule",
        )
        .get(pk=tournament_category.pk)
    )

    if locked_category.fixtures_generated_at:
        raise ValidationError(
            "Fixtures have already been generated "
            "for this tournament category."
        )

    if locked_category.rounds.exists():
        raise ValidationError(
            "Tournament rounds already exist for this category. "
            "Delete or correct the existing rounds before "
            "generating fixtures."
        )

    if not locked_category.scoring_rule_id:
        raise ValidationError(
            "Assign a scoring rule before "
            "generating fixtures."
        )

    entries = list(
        locked_category.entries
        .filter(
            status__code__iexact="confirmed"
        )
        .select_related(
            "status",
            "registration",
        )
        .order_by(
            "seed",
            "created_at",
            "pk",
        )
    )

    if len(entries) < 2:
        raise ValidationError(
            "At least 2 confirmed entries are required "
            "to generate fixtures."
        )

    scheduled_status = (
        MatchStatus.objects
        .filter(
            code__iexact="scheduled",
            is_active=True,
        )
        .first()
    )

    if not scheduled_status:
        raise ValidationError(
            "Create an active Match Status with code "
            "'scheduled' before generating fixtures."
        )

    # ================================================
    # KNOCKOUT FIXTURES
    # ================================================
    if (
        locked_category.fixture_type
        == TournamentCategory.FixtureType.KNOCKOUT
    ):
        result = generate_knockout_draw(
            tournament_category=locked_category,
            entries=entries,
            scheduled_status=scheduled_status,
        )

    # ================================================
    # ROUND ROBIN FIXTURES
    # ================================================
    elif (
        locked_category.fixture_type
        == TournamentCategory.FixtureType.ROUND_ROBIN
    ):
        result = generate_round_robin_draw(
            tournament_category=locked_category,
            entries=entries,
            scheduled_status=scheduled_status,
        )

    else:
        raise ValidationError(
            "The selected fixture type is not supported."
        )

    locked_category.fixtures_generated_at = (
        timezone.now()
    )

    locked_category.save(
        update_fields=[
            "fixtures_generated_at",
        ]
    )

    result["fixture_type"] = (
        locked_category.fixture_type
    )

    result["tournament_category"] = (
        locked_category
    )

    return result
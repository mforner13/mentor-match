import pytest

from app.classes import CSMentor, CSMentee, CSParticipantFactory
from matching.rules import rule as rl
from matching.match import Match


@pytest.mark.unit
def test_CSMentor_to_dict(base_data):
    mentor = CSMentor(**base_data.copy())
    for key, value in base_data.items():
        assert value in mentor.to_dict()[mentor.class_name()].values()
    assert mentor == CSMentor(**mentor.to_dict()[mentor.class_name()])


@pytest.mark.unit
def test_CSMentee_to_dict(base_data):
    base_data["target profession"] = base_data.pop("profession")
    mentor = CSMentee(**base_data)
    for key, value in base_data.items():
        assert value in mentor.to_dict()[mentor.class_name()].values()
    assert mentor == CSMentee(**mentor.to_dict()[mentor.class_name()])


@pytest.mark.unit
def test_factory(base_mentor_data, base_mentee_data, base_mentor, base_mentee):
    assert (
        CSParticipantFactory.create_from_dict({"csmentor": base_mentor_data})
        == base_mentor
    )
    assert (
        CSParticipantFactory.create_from_dict({"csmentee": base_mentee_data})
        == base_mentee
    )


@pytest.mark.unit
def test_matches_and_rules(base_mentor, base_mentee):
    rule = rl.Generic(
        {True: 3, False: 0},
        lambda match: match.mentee.characteristic in match.mentor.characteristics,
    )
    match = Match(base_mentor, base_mentee, {}, [])
    match.rules = [rule]
    match.calculate_match()
    assert match.score == 3

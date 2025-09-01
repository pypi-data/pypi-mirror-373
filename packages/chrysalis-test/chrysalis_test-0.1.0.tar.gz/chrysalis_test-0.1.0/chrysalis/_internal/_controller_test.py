from chrysalis._internal import _controller as controller
from chrysalis._internal import _invariants as invariants
from chrysalis._internal.conftest import (
    identity,
    inverse,
)


def test_single_register() -> None:
    controller.new_knowledge_base()
    controller.register(
        transformation=identity,
        invariant=invariants.equals,
    )

    knowledge_base = controller._CURRENT_KNOWLEDGE_BASE

    assert knowledge_base is not None
    assert len(knowledge_base.relations) == 1
    assert knowledge_base.relations[0].transformation_name == "identity"


def test_multiple_register() -> None:
    controller.new_knowledge_base()
    controller.register(
        transformation=identity,
        invariant=invariants.equals,
    )
    controller.register(
        transformation=identity,
        invariant=invariants.is_same_sign,
    )
    controller.register(
        transformation=inverse,
        invariant=invariants.not_equals,
    )

    knowledge_base = controller._CURRENT_KNOWLEDGE_BASE

    assert knowledge_base is not None
    assert len(knowledge_base.relations) == 2
    assert {relation.transformation_name for relation in knowledge_base.relations} == {
        "identity",
        "inverse",
    }
    assert set(knowledge_base._relations["identity"].invariants) == {
        invariants.equals,
        invariants.is_same_sign,
    }
    assert knowledge_base._relations["inverse"].invariants == [invariants.not_equals]

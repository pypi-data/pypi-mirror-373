from .id_maker import create_make_id_for_actor_id


def test_create_make_id_for_actor_id():
    actor_id = "https://actor.test/actor_id"
    make_id = create_make_id_for_actor_id(actor_id)

    assert make_id().startswith("https://actor.test/object/")

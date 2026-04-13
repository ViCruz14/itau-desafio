from domain.entities.completion import Completion
from domain.value_objects.completion_status import CompletionStatus


def test_new_completion_is_pending():
    c = Completion(user_id="u1", prompt="hello", model="m1")
    assert c.status == CompletionStatus.PENDING
    assert c.response is None
    assert c.error_msg is None
    assert c.latency_ms is None
    assert c.id is not None
    assert c.created_at is not None


def test_mark_success_sets_all_fields():
    c = Completion(user_id="u1", prompt="hello", model="m1")
    c.mark_success("world", 100)
    assert c.status == CompletionStatus.SUCCESS
    assert c.response == "world"
    assert c.latency_ms == 100


def test_mark_error_sets_all_fields():
    c = Completion(user_id="u1", prompt="hello", model="m1")
    c.mark_error("timeout", 0)
    assert c.status == CompletionStatus.ERROR
    assert c.error_msg == "timeout"
    assert c.latency_ms == 0


def test_each_instance_gets_unique_id():
    c1 = Completion(user_id="u1", prompt="p", model="m")
    c2 = Completion(user_id="u1", prompt="p", model="m")
    assert c1.id != c2.id

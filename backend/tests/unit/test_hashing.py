import os
import subprocess
import sys

from cid.core.hashing import hmac_id, record_hash


def test_record_hash_stable_across_key_ordering():
    a = {"b": 2, "a": 1, "c": {"y": 2, "x": 1}}
    b = {"a": 1, "c": {"x": 1, "y": 2}, "b": 2}
    assert record_hash(a) == record_hash(b)


def test_record_hash_changed_field_changes_digest():
    a = {"a": 1, "b": 2}
    b = {"a": 1, "b": 3}
    assert record_hash(a) != record_hash(b)


def test_record_hash_stable_across_pythonhashseed():
    record = {"a": 1, "b": [1, 2, 3], "c": "श्री"}
    code = f"from cid.core.hashing import record_hash\nprint(record_hash({record!r}))\n"
    env0 = {**os.environ, "PYTHONHASHSEED": "0"}
    env1 = {**os.environ, "PYTHONHASHSEED": "1"}
    out0 = subprocess.run(
        [sys.executable, "-c", code], env=env0, capture_output=True, text=True, check=True
    ).stdout.strip()
    out1 = subprocess.run(
        [sys.executable, "-c", code], env=env1, capture_output=True, text=True, check=True
    ).stdout.strip()
    assert out0 == out1 == record_hash(record)


def test_hmac_id_stable_for_a_key():
    assert hmac_id("+919820011234", "key-a") == hmac_id("+919820011234", "key-a")


def test_hmac_id_differs_for_a_different_key():
    assert hmac_id("+919820011234", "key-a") != hmac_id("+919820011234", "key-b")

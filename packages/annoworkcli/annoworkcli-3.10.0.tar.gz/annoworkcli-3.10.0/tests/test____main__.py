from annoworkcli.__main__ import mask_sensitive_value_in_argv


def test__mask_sensitive_value_in_argv__同じ引数を指定する():
    actual = mask_sensitive_value_in_argv(
        [
            "--annofab_user_id",
            "alice",
            "--annofab_password",
            "pw_alice",
            "--annofab_user_id",
            "bob",
            "--annofab_password",
            "pw_bob",
            "--annowork_user_id",
            "chris",
            "--annowork_password",
            "pw_chris",
            "--annowork_user_id",
            "dave",
            "--annowork_password",
            "pw_dave",
            "--annofab_pat",
            "pat_eve",
        ]
    )
    assert actual == [
        "--annofab_user_id",
        "***",
        "--annofab_password",
        "***",
        "--annofab_user_id",
        "***",
        "--annofab_password",
        "***",
        "--annowork_user_id",
        "***",
        "--annowork_password",
        "***",
        "--annowork_user_id",
        "***",
        "--annowork_password",
        "***",
        "--annofab_pat",
        "***",
    ]

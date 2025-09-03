from shekar.utils import is_informal


def test_is_informal():
    input_text = "میخوام برم خونه، تو نمیای؟"
    expected_output = True
    assert is_informal(input_text) == expected_output

    input_text = "دیگه چه خبر؟"
    expected_output = True
    assert is_informal(input_text) == expected_output

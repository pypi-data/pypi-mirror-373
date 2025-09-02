from copy import deepcopy
from quam.components import BasicQuam, SingleChannel


def test_instantiate_basic_quam_empty():
    quam = BasicQuam()
    assert quam.channels == {}
    assert quam.octaves == {}

    d = quam.to_dict()
    assert d == {
        "__class__": "quam.components.basic_quam.BasicQuam",
    }


def test_instantiate_basic_quam_with_channel():
    quam = BasicQuam(channels={"single": SingleChannel(opx_output=("con1", 1))})
    d = quam.to_dict()
    assert d == {
        "__class__": "quam.components.basic_quam.BasicQuam",
        "channels": {
            "single": {
                "__class__": "quam.components.channels.SingleChannel",
                "opx_output": ("con1", 1),
            },
        },
    }


def test_generate_basic_quam_config(qua_config):
    quam = BasicQuam()
    cfg = quam.generate_config()
    assert cfg == qua_config

    quam.channels = {"single": SingleChannel(opx_output=("con1", 1))}
    cfg = quam.generate_config()

    quam.channels["single"].apply_to_config(qua_config)
    qua_config["controllers"]["con1"]["analog_outputs"][1]["offset"] = 0.0

    assert cfg == qua_config

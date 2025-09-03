#  MIT License
#
#  Copyright (c) 2024 denes44
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom
#  the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#  OTHER DEALINGS IN THE SOFTWARE.

# ruff: noqa: D103, S101

import os

import pytest
from pydantic import ValidationError

# Mock environment variables before importing the module
# LED Configuration
os.environ["LED_DIM_RATIO"] = "0.3"
os.environ["LED_FADE_TIME"] = "5.3"

# sACN Configuration
os.environ["SACN_MULTICAST"] = "False"
os.environ["SACN_UNICAST_IP"] = "192.168.1.1"
os.environ["SACN_UNIVERSE"] = "2"
os.environ["SACN_FPS"] = "15"

# BKK Configuration
os.environ["BKK_API_KEY"] = "123e4567-e89b-12d3-a456-426614174000"
os.environ["BKK_API_UPDATE_INTERVAL"] = "6"
os.environ["BKK_API_UPDATE_REALTIME"] = "82"
os.environ["BKK_API_UPDATE_REGULAR"] = "3456"
os.environ["BKK_API_UPDATE_ALERTS"] = "123"

# ESPHome Configuration
os.environ["ESPHOME_USED"] = "True"
os.environ["ESPHOME_DEVICE_IP"] = "192.168.1.2"
os.environ["ESPHOME_API_KEY"] = "0LTLKmoTVR0BO3xppXQkIBVb0VzDLZFqAplYnADTbOY="

from BudapestMetroDisplay.config import (
    AppConfig,
    BKKConfig,
    ESPHomeConfig,
    LEDConfig,
    SACNConfig,
)


def test_app_config_initializes_correctly() -> None:
    config = AppConfig()
    # LED Configuration
    assert config.led.dim_ratio == 0.3
    assert config.led.fade_time == 5.3

    # sACN Configuration
    assert not config.sacn.multicast
    assert str(config.sacn.unicast_ip) == "192.168.1.1"
    assert config.sacn.universe == 2
    assert config.sacn.fps == 15

    # BKK Configuration
    assert config.bkk.api_key == "123e4567-e89b-12d3-a456-426614174000"
    assert config.bkk.api_update_interval == 6
    assert config.bkk.api_update_realtime == 82
    assert config.bkk.api_update_regular == 3456
    assert config.bkk.api_update_alerts == 123

    # ESPHome Configuration
    assert config.esphome.used
    assert str(config.esphome.device_ip) == "192.168.1.2"
    assert config.esphome.api_key == "0LTLKmoTVR0BO3xppXQkIBVb0VzDLZFqAplYnADTbOY="


def test_delete_env_vars() -> None:
    # List of environment variable keys to delete
    env_vars = [
        "LED_DIM_RATIO",
        "LED_FADE_TIME",
        "SACN_MULTICAST",
        "SACN_UNICAST_IP",
        "SACN_UNIVERSE",
        "SACN_FPS",
        "BKK_API_KEY",
        "BKK_API_UPDATE_INTERVAL",
        "BKK_API_UPDATE_REALTIME",
        "BKK_API_UPDATE_REGULAR",
        "BKK_API_UPDATE_ALERTS",
        "ESPHOME_USED",
        "ESPHOME_DEVICE_IP",
        "ESPHOME_API_KEY",
    ]
    # Delete each environment variable
    for var in env_vars:
        if var in os.environ:
            del os.environ[var]


def test_led_config_dim_ratio_within_bounds() -> None:
    config = LEDConfig(dim_ratio=0.5)
    assert config.dim_ratio == 0.5


def test_led_config_dim_ratio_out_of_bounds_positive() -> None:
    with pytest.raises(ValidationError):
        LEDConfig(dim_ratio=1.5)


def test_led_config_dim_ratio_out_of_bounds_negative() -> None:
    with pytest.raises(ValidationError):
        LEDConfig(dim_ratio=-2.5)


def test_led_config_fade_time_positive() -> None:
    config = LEDConfig(fade_time=2.0)
    assert config.fade_time == 2.0


def test_led_config_fade_time_zero() -> None:
    config = LEDConfig(fade_time=0.0)
    assert config.fade_time == 0.0


def test_led_config_fade_time_non_positive() -> None:
    with pytest.raises(ValidationError):
        LEDConfig(fade_time=-1.0)


def test_sacn_config_multicast_default() -> None:
    config = SACNConfig()
    assert config.multicast is True


def test_sacn_config_unicast_ip_required() -> None:
    with pytest.raises(ValidationError):
        SACNConfig(multicast=False, unicast_ip=None)


def test_sacn_config_unicast_ipv4() -> None:
    config = SACNConfig(multicast=False, unicast_ip="192.168.1.1")
    assert str(config.unicast_ip) == "192.168.1.1"


def test_sacn_config_unicast_ipv6() -> None:
    config = SACNConfig(
        multicast=False,
        unicast_ip="2001:0000:130F:0000:0000:09C0:876A:130B",
    )
    assert str(config.unicast_ip) == "2001:0:130f::9c0:876a:130b"


def test_bkk_config_api_key_required_none() -> None:
    with pytest.raises(ValidationError):
        BKKConfig(api_key=None)


def test_bkk_config_api_key_required_empty() -> None:
    with pytest.raises(ValidationError):
        BKKConfig(api_key="")


def test_bkk_config_api_key_required_invalid() -> None:
    with pytest.raises(ValidationError):
        BKKConfig(api_key="test-api-key")


def test_bkk_config_api_key_required() -> None:
    config = BKKConfig(api_key="123e4567-e89b-12d3-a456-426614174000")
    assert config.api_key == "123e4567-e89b-12d3-a456-426614174000"


def test_bkk_config_api_update_interval_positive() -> None:
    config = BKKConfig(
        api_key="123e4567-e89b-12d3-a456-426614174000",
        api_update_interval=5,
    )
    assert config.api_update_interval == 5


def test_bkk_config_api_update_interval_out_of_bounds() -> None:
    with pytest.raises(ValidationError):
        BKKConfig(api_update_interval=-5)


def test_bkk_config_api_update_realtime_positive() -> None:
    config = BKKConfig(
        api_key="123e4567-e89b-12d3-a456-426614174000",
        api_update_realtime=5,
    )
    assert config.api_update_realtime == 5


def test_bkk_config_api_update_realtime_out_of_bounds() -> None:
    with pytest.raises(ValidationError):
        BKKConfig(api_update_realtime=-5)


def test_bkk_config_api_update_regular_positive() -> None:
    config = BKKConfig(
        api_key="123e4567-e89b-12d3-a456-426614174000",
        api_update_regular=5,
    )
    assert config.api_update_regular == 5


def test_bkk_config_api_update_regular_out_of_bounds() -> None:
    with pytest.raises(ValidationError):
        BKKConfig(api_update_regular=-5)


def test_bkk_config_api_update_alerts_positive() -> None:
    config = BKKConfig(
        api_key="123e4567-e89b-12d3-a456-426614174000",
        api_update_alerts=5,
    )
    assert config.api_update_alerts == 5


def test_bkk_config_api_update_alerts_out_of_bounds() -> None:
    with pytest.raises(ValidationError):
        BKKConfig(api_update_alerts=-5)


def test_esphome_config_used_requires_ip() -> None:
    with pytest.raises(ValidationError):
        ESPHomeConfig(used=True, device_ip=None, api_key=None)


def test_esphome_config_used_requires_ip_and_key() -> None:
    with pytest.raises(ValidationError):
        ESPHomeConfig(used=True, device_ip=None, api_key=None)


def test_esphome_config_used_empty_api_key() -> None:
    with pytest.raises(ValidationError):
        ESPHomeConfig(used=True, device_ip="192.168.1.1", api_key="")


def test_esphome_config_used_invalid_api_key() -> None:
    with pytest.raises(ValidationError):
        ESPHomeConfig(used=True, device_ip="192.168.1.1", api_key="test_api_key")


def test_esphome_config_used_ipv6() -> None:
    config = ESPHomeConfig(
        used=True,
        device_ip="2001:0000:130F:0000:0000:09C0:876A:130B",
        api_key="0LTLKmoTVR0BO3xppXQkIBVb0VzDLZFqAplYnADTbOY=",
    )
    assert config.used is True
    assert str(config.device_ip) == "2001:0:130f::9c0:876a:130b"
    assert config.api_key == "0LTLKmoTVR0BO3xppXQkIBVb0VzDLZFqAplYnADTbOY="


def test_esphome_config_not_used_allows_missing_ip_and_key() -> None:
    config = ESPHomeConfig(used=False)
    assert config.used is False
    assert config.device_ip is None
    assert config.api_key is None

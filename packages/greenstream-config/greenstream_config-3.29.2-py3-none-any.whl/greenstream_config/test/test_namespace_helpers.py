import pytest
from greenstream_config.types import Camera

from libs.greenstream_config.greenstream_config.namespace_helpers import (
    camera_frame_topic,
    camera_frame_topic_from_camera,
    camera_namespace,
    camera_namespace_from_camera,
    camera_node_name,
    camera_node_name_from_camera,
    camera_topic,
    camera_topic_from_camera,
    frame_id,
    frame_id_from_camera,
)


@pytest.fixture
def camera():
    return Camera(name="bow", type="color", order=0)


def test_camera_topic():
    assert camera_topic("vessel_1", "bow", "color") == "/vessel_1/sensors/cameras/bow_color"


def test_camera_topic_from_camera(camera):
    assert camera_topic_from_camera("vessel_1", camera) == "/vessel_1/sensors/cameras/bow_color"


def test_frame_id():
    assert frame_id("vessel_1", "bow", "color") == "vessel_1_bow_color_optical_frame"


def test_frame_id_from_camera(camera):
    assert frame_id_from_camera("vessel_1", camera) == "vessel_1_bow_color_optical_frame"


def test_camera_namespace():
    assert camera_namespace("namespace", "bow") == "namespace/cameras/bow"


def test_camera_namespace_from_camera(camera):
    assert camera_namespace_from_camera("namespace", camera) == "namespace/cameras/bow"


def test_camera_node_name():
    assert camera_node_name("node", "bow", "color") == "node_bow_color"


def test_camera_node_name_from_camera(camera):
    assert camera_node_name_from_camera("node", camera) == "node_bow_color"


def test_camera_frame_topic():
    assert (
        camera_frame_topic("vessel_1", "bow", "color") == "/vessel_1/perception/frames/bow_color"
    )


def test_camera_frame_topic_empty_namespace():
    assert camera_frame_topic("", "bow", "color") == "perception/frames/bow_color"


def test_camera_frame_topic_from_camera(camera):
    assert (
        camera_frame_topic_from_camera("vessel_1", camera)
        == "/vessel_1/perception/frames/bow_color"
    )


def test_camera_frame_topic_from_camera_empty_namespace(camera):
    assert camera_frame_topic_from_camera("", camera) == "perception/frames/bow_color"

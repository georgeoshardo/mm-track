import numpy as np
import pytest

from mm_track.application_menus.view_mode_widget import ViewModeWidget
from mm_track.data_views.views_coordinator.tracks_viewer import TracksViewer


@pytest.fixture(autouse=True)
def clear_viewer_layers(viewer):
    """Clear viewer layers between tests."""
    yield
    viewer.layers.clear()


@pytest.fixture
def view_mode_widget(viewer, solution_tracks_3d, qtbot):
    tracks_viewer = TracksViewer.get_instance(viewer)
    tracks_viewer.update_tracks(tracks=solution_tracks_3d, name="test")

    widget = ViewModeWidget(viewer)
    qtbot.addWidget(widget)

    return widget, tracks_viewer


@pytest.fixture
def view_mode_widget_2d(viewer, solution_tracks_2d, segmentation_2d, qtbot):
    """A ViewModeWidget on 2D+time tracks with a matching raw image layer, so that the
    kymograph view is available."""
    viewer.add_image(np.asarray(segmentation_2d, dtype=float), name="raw")

    tracks_viewer = TracksViewer.get_instance(viewer)
    tracks_viewer.update_tracks(tracks=solution_tracks_2d, name="test")
    tracks_viewer.set_kymograph_image_layer("raw")

    widget = ViewModeWidget(viewer)
    qtbot.addWidget(widget)

    return widget, tracks_viewer


@pytest.mark.parametrize("mode", ["lineage", "group", "all"])
def test_switch_display_modes(view_mode_widget, mode):
    """Test that checking the radio buttons changes the display mode"""

    widget, tracks_viewer = view_mode_widget

    widget.mode_widget.button_for_mode(mode).setChecked(True)

    assert tracks_viewer.mode == mode


@pytest.mark.parametrize("mode", ["lineage", "group", "all"])
def test_mode_update_syncs_radio_buttons(view_mode_widget, mode):
    """Check that the radio button states are updated when the tracks_viewer updates its
    display mode."""

    widget, tracks_viewer = view_mode_widget

    tracks_viewer.set_display_mode(mode)
    widget._update_controls()
    radio = widget.mode_widget.button_for_mode(mode)

    assert radio.isChecked()


class TestKymographView:
    """The view mode buttons and the kymograph image selector."""

    def test_kymograph_button_disabled_for_3d_tracks(self, view_mode_widget):
        """The kymograph view only supports 2D+time tracks."""
        widget, _ = view_mode_widget

        assert widget.view_mode_widget.button_for_mode("kymograph").isEnabled() is False

    def test_view_mode_switches_to_kymograph_and_disables_image_selector(
        self, view_mode_widget_2d
    ):
        widget, tracks_viewer = view_mode_widget_2d

        assert widget.view_mode_widget.button_for_mode("kymograph").isEnabled() is True
        assert widget.image_layer_box.currentText() == "raw"

        widget.view_mode_widget.button_for_mode("kymograph").setChecked(True)

        assert tracks_viewer.view_mode == "kymograph"
        # the image can only be changed from the spatial view
        assert widget.image_layer_box.isEnabled() is False
        assert widget.image_layer_box.currentText() == "raw"

        widget.view_mode_widget.button_for_mode("spatial").setChecked(True)

        assert tracks_viewer.view_mode == "spatial"
        assert widget.image_layer_box.isEnabled() is True

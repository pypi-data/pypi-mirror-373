from kivy.clock import Clock
from kivy.uix.modalview import ModalView

from ... import Controller
from .operations.OperationsBase import OperationsBase
from .operations.OutsideCorner.OutsideCornerOperationType import OutsideCornerOperationType
from .operations.OutsideCorner.OutsideCornerSettings import OutsideCornerSettings
from .operations.InsideCorner.InsideCornerSettings import InsideCornerSettings
from .operations.SingleAxis.SingleAxisProbeOperationType import \
    SingleAxisProbeOperationType
from .operations.SingleAxis.SingleAxisProbeSettings import SingleAxisProbeSettings
from .preview.ProbingPreviewPopup import ProbingPreviewPopup

from .operations.InsideCorner.InsideCornerOperationType import InsideCornerOperationType

from .operations.Bore.BoreOperationType import BoreOperationType
from .operations.Bore.BoreSettings import BoreSettings

from .operations.Boss.BossOperationType import BossOperationType
from .operations.Boss.BossSettings import BossSettings

from .operations.Angle.AngleOperationType import AngleOperationType
from .operations.Angle.AngleSettings import AngleSettings

class ProbingPopup(ModalView):

    controller: Controller

    def __init__(self, controller, **kwargs):
        self.outside_corner_settings = None
        self.inside_corner_settings = None
        self.single_axis_settings = None
        self.bore_settings = None
        self.boss_settings = None
        self.angle_settings = None
        self.controller = controller

        self.preview_popup = ProbingPreviewPopup(controller)

        # wait on UI to finish loading
        Clock.schedule_once(self.delayed_bind, 0.1)

        super(ProbingPopup, self).__init__(**kwargs)

    def delayed_bind(self, dt):
        self.outside_corner_settings = self.ids.outside_corner_settings
        self.inside_corner_settings = self.ids.inside_corner_settings
        self.single_axis_settings = self.ids.single_axis_settings
        self.bore_settings = self.ids.bore_settings
        self.boss_settings = self.ids.boss_settings
        self.angle_settings = self.ids.angle_settings


    def on_single_axis_probing_pressed(self, operation_key: str):
        cfg = self.single_axis_settings.get_config()
        the_op = SingleAxisProbeOperationType[operation_key].value
        self.show_preview(the_op, cfg)

    def on_inside_corner_probing_pressed(self, operation_key: str):
        cfg = self.inside_corner_settings.get_config()
        the_op = InsideCornerOperationType[operation_key].value
        self.show_preview(the_op, cfg)

    def on_outside_corner_probing_pressed(self, operation_key: str):

        cfg = self.outside_corner_settings.get_config()
        the_op = OutsideCornerOperationType[operation_key].value
        self.show_preview(the_op, cfg)

    def on_bore_probing_pressed(self, operation_key: str):

        cfg = self.bore_settings.get_config()
        the_op = BoreOperationType[operation_key].value
        self.show_preview(the_op, cfg)

    def on_boss_probing_pressed(self, operation_key: str):

        cfg = self.boss_settings.get_config()
        the_op = BossOperationType[operation_key].value
        self.show_preview(the_op, cfg)

    def on_angle_probing_pressed(self, operation_key: str):

        cfg = self.angle_settings.get_config()
        the_op = AngleOperationType[operation_key].value
        self.show_preview(the_op, cfg)


    def show_preview(self, operation: OperationsBase, cfg):
        missing_definition = operation.get_missing_config(cfg)

        if missing_definition is None:
            gcode = operation.generate(cfg)
            self.preview_popup.gcode = gcode
            self.preview_popup.probe_preview_label = gcode
        else:
            self.preview_popup.gcode = ""
            self.preview_popup.probe_preview_label = "Missing required parameter " + missing_definition.label

        self.preview_popup.open()

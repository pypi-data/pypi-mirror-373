from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DisplayCls:
	"""Display commands group definition. 59 total commands, 11 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("display", core, parent)

	@property
	def color(self):
		"""color commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_color'):
			from .Color import ColorCls
			self._color = ColorCls(self._core, self._cmd_group)
		return self._color

	@property
	def signal(self):
		"""signal commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_signal'):
			from .Signal import SignalCls
			self._signal = SignalCls(self._core, self._cmd_group)
		return self._signal

	@property
	def backlight(self):
		"""backlight commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_backlight'):
			from .Backlight import BacklightCls
			self._backlight = BacklightCls(self._core, self._cmd_group)
		return self._backlight

	@property
	def dialog(self):
		"""dialog commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_dialog'):
			from .Dialog import DialogCls
			self._dialog = DialogCls(self._core, self._cmd_group)
		return self._dialog

	@property
	def result(self):
		"""result commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_result'):
			from .Result import ResultCls
			self._result = ResultCls(self._core, self._cmd_group)
		return self._result

	@property
	def annotation(self):
		"""annotation commands group. 5 Sub-classes, 2 commands."""
		if not hasattr(self, '_annotation'):
			from .Annotation import AnnotationCls
			self._annotation = AnnotationCls(self._core, self._cmd_group)
		return self._annotation

	@property
	def clr(self):
		"""clr commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_clr'):
			from .Clr import ClrCls
			self._clr = ClrCls(self._core, self._cmd_group)
		return self._clr

	@property
	def diagram(self):
		"""diagram commands group. 0 Sub-classes, 7 commands."""
		if not hasattr(self, '_diagram'):
			from .Diagram import DiagramCls
			self._diagram = DiagramCls(self._core, self._cmd_group)
		return self._diagram

	@property
	def persistence(self):
		"""persistence commands group. 0 Sub-classes, 4 commands."""
		if not hasattr(self, '_persistence'):
			from .Persistence import PersistenceCls
			self._persistence = PersistenceCls(self._core, self._cmd_group)
		return self._persistence

	@property
	def trigger(self):
		"""trigger commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_trigger'):
			from .Trigger import TriggerCls
			self._trigger = TriggerCls(self._core, self._cmd_group)
		return self._trigger

	@property
	def toolbar(self):
		"""toolbar commands group. 2 Sub-classes, 1 commands."""
		if not hasattr(self, '_toolbar'):
			from .Toolbar import ToolbarCls
			self._toolbar = ToolbarCls(self._core, self._cmd_group)
		return self._toolbar

	def get_intensity(self) -> float:
		"""DISPlay:INTensity \n
		Snippet: value: float = driver.display.get_intensity() \n
		The intensity determines the strength of the waveform line in the diagram. Enter a percentage between 0 (not visible) and
		100% (strong) . The default value is 50%. \n
			:return: intensity: No help available
		"""
		response = self._core.io.query_str('DISPlay:INTensity?')
		return Conversions.str_to_float(response)

	def set_intensity(self, intensity: float) -> None:
		"""DISPlay:INTensity \n
		Snippet: driver.display.set_intensity(intensity = 1.0) \n
		The intensity determines the strength of the waveform line in the diagram. Enter a percentage between 0 (not visible) and
		100% (strong) . The default value is 50%. \n
			:param intensity: No help available
		"""
		param = Conversions.decimal_value_to_str(intensity)
		self._core.io.write(f'DISPlay:INTensity {param}')

	def clone(self) -> 'DisplayCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = DisplayCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group

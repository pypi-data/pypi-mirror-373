from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.RepeatedCapability import RepeatedCapability
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AnnotationCls:
	"""Annotation commands group definition. 32 total commands, 5 Subgroups, 2 group commands
	Repeated Capability: Annotation, default value after init: Annotation.Ix1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("annotation", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_annotation_get', 'repcap_annotation_set', repcap.Annotation.Ix1)

	def repcap_annotation_set(self, annotation: repcap.Annotation) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Annotation.Default.
		Default value after init: Annotation.Ix1"""
		self._cmd_group.set_repcap_enum_value(annotation)

	def repcap_annotation_get(self) -> repcap.Annotation:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def color(self):
		"""color commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_color'):
			from .Color import ColorCls
			self._color = ColorCls(self._core, self._cmd_group)
		return self._color

	@property
	def text(self):
		"""text commands group. 6 Sub-classes, 1 commands."""
		if not hasattr(self, '_text'):
			from .Text import TextCls
			self._text = TextCls(self._core, self._cmd_group)
		return self._text

	@property
	def arrow(self):
		"""arrow commands group. 8 Sub-classes, 1 commands."""
		if not hasattr(self, '_arrow'):
			from .Arrow import ArrowCls
			self._arrow = ArrowCls(self._core, self._cmd_group)
		return self._arrow

	@property
	def rectangle(self):
		"""rectangle commands group. 7 Sub-classes, 1 commands."""
		if not hasattr(self, '_rectangle'):
			from .Rectangle import RectangleCls
			self._rectangle = RectangleCls(self._core, self._cmd_group)
		return self._rectangle

	@property
	def pline(self):
		"""pline commands group. 4 Sub-classes, 1 commands."""
		if not hasattr(self, '_pline'):
			from .Pline import PlineCls
			self._pline = PlineCls(self._core, self._cmd_group)
		return self._pline

	def clear(self) -> None:
		"""DISPlay:ANNotation:CLEar \n
		Snippet: driver.display.annotation.clear() \n
		Removes all existing annotations. \n
		"""
		self._core.io.write(f'DISPlay:ANNotation:CLEar')

	def clear_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""DISPlay:ANNotation:CLEar \n
		Snippet: driver.display.annotation.clear_and_wait() \n
		Removes all existing annotations. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'DISPlay:ANNotation:CLEar', opc_timeout_ms)

	def get_transparency(self) -> int:
		"""DISPlay:ANNotation:TRANsparency \n
		Snippet: value: int = driver.display.annotation.get_transparency() \n
		Sets a transparency of all annotations. For high transparency values, you can see the waveform display in the background.
		For lower transparency values, readability of the annotation improves. \n
			:return: transparency: No help available
		"""
		response = self._core.io.query_str('DISPlay:ANNotation:TRANsparency?')
		return Conversions.str_to_int(response)

	def set_transparency(self, transparency: int) -> None:
		"""DISPlay:ANNotation:TRANsparency \n
		Snippet: driver.display.annotation.set_transparency(transparency = 1) \n
		Sets a transparency of all annotations. For high transparency values, you can see the waveform display in the background.
		For lower transparency values, readability of the annotation improves. \n
			:param transparency: No help available
		"""
		param = Conversions.decimal_value_to_str(transparency)
		self._core.io.write(f'DISPlay:ANNotation:TRANsparency {param}')

	def clone(self) -> 'AnnotationCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = AnnotationCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group

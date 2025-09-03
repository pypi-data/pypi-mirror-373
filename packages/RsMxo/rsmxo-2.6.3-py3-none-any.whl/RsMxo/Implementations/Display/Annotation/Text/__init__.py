from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TextCls:
	"""Text commands group definition. 7 total commands, 6 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("text", core, parent)

	@property
	def value(self):
		"""value commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_value'):
			from .Value import ValueCls
			self._value = ValueCls(self._core, self._cmd_group)
		return self._value

	@property
	def remove(self):
		"""remove commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_remove'):
			from .Remove import RemoveCls
			self._remove = RemoveCls(self._core, self._cmd_group)
		return self._remove

	@property
	def color(self):
		"""color commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_color'):
			from .Color import ColorCls
			self._color = ColorCls(self._core, self._cmd_group)
		return self._color

	@property
	def fontsize(self):
		"""fontsize commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fontsize'):
			from .Fontsize import FontsizeCls
			self._fontsize = FontsizeCls(self._core, self._cmd_group)
		return self._fontsize

	@property
	def horizontal(self):
		"""horizontal commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_horizontal'):
			from .Horizontal import HorizontalCls
			self._horizontal = HorizontalCls(self._core, self._cmd_group)
		return self._horizontal

	@property
	def vertical(self):
		"""vertical commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_vertical'):
			from .Vertical import VerticalCls
			self._vertical = VerticalCls(self._core, self._cmd_group)
		return self._vertical

	def clear(self, annotation=repcap.Annotation.Default) -> None:
		"""DISPlay:ANNotation:TEXT<*>:CLEar \n
		Snippet: driver.display.annotation.text.clear(annotation = repcap.Annotation.Default) \n
		Deletes all text annotations. \n
			:param annotation: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Annotation')
		"""
		annotation_cmd_val = self._cmd_group.get_repcap_cmd_value(annotation, repcap.Annotation)
		self._core.io.write(f'DISPlay:ANNotation:TEXT{annotation_cmd_val}:CLEar')

	def clear_and_wait(self, annotation=repcap.Annotation.Default, opc_timeout_ms: int = -1) -> None:
		annotation_cmd_val = self._cmd_group.get_repcap_cmd_value(annotation, repcap.Annotation)
		"""DISPlay:ANNotation:TEXT<*>:CLEar \n
		Snippet: driver.display.annotation.text.clear_and_wait(annotation = repcap.Annotation.Default) \n
		Deletes all text annotations. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param annotation: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Annotation')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'DISPlay:ANNotation:TEXT{annotation_cmd_val}:CLEar', opc_timeout_ms)

	def clone(self) -> 'TextCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = TextCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group

from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ExpResultCls:
	"""ExpResult commands group definition. 5 total commands, 4 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("expResult", core, parent)

	@property
	def path(self):
		"""path commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_path'):
			from .Path import PathCls
			self._path = PathCls(self._core, self._cmd_group)
		return self._path

	@property
	def extension(self):
		"""extension commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_extension'):
			from .Extension import ExtensionCls
			self._extension = ExtensionCls(self._core, self._cmd_group)
		return self._extension

	@property
	def detail(self):
		"""detail commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_detail'):
			from .Detail import DetailCls
			self._detail = DetailCls(self._core, self._cmd_group)
		return self._detail

	@property
	def time(self):
		"""time commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_time'):
			from .Time import TimeCls
			self._time = TimeCls(self._core, self._cmd_group)
		return self._time

	def save(self, filename: str, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:EXPResult:SAVE \n
		Snippet: driver.sbus.expResult.save(filename = 'abc', serialBus = repcap.SerialBus.Default) \n
		Saves the selected results to the indicated file. \n
			:param filename: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.value_to_quoted_str(filename)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:EXPResult:SAVE {param}')

	def clone(self) -> 'ExpResultCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ExpResultCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group

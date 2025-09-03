from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FormatPyCls:
	"""FormatPy commands group definition. 16 total commands, 4 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("formatPy", core, parent)

	@property
	def fcount(self):
		"""fcount commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fcount'):
			from .Fcount import FcountCls
			self._fcount = FcountCls(self._core, self._cmd_group)
		return self._fcount

	@property
	def addFrame(self):
		"""addFrame commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_addFrame'):
			from .AddFrame import AddFrameCls
			self._addFrame = AddFrameCls(self._core, self._cmd_group)
		return self._addFrame

	@property
	def clr(self):
		"""clr commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_clr'):
			from .Clr import ClrCls
			self._clr = ClrCls(self._core, self._cmd_group)
		return self._clr

	@property
	def frame(self):
		"""frame commands group. 5 Sub-classes, 0 commands."""
		if not hasattr(self, '_frame'):
			from .Frame import FrameCls
			self._frame = FrameCls(self._core, self._cmd_group)
		return self._frame

	def load(self, filename: str, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:NRZC:FORMat:LOAD \n
		Snippet: driver.sbus.nrzc.formatPy.load(filename = 'abc', serialBus = repcap.SerialBus.Default) \n
		Loads a the specified XML file with a list of frame descriptions. \n
			:param filename: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.value_to_quoted_str(filename)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:NRZC:FORMat:LOAD {param}')

	def save(self, filename: str, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:NRZC:FORMat:SAVE \n
		Snippet: driver.sbus.nrzc.formatPy.save(filename = 'abc', serialBus = repcap.SerialBus.Default) \n
		Saves the current list of frame descriptions to an XML file with the specified name. \n
			:param filename: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.value_to_quoted_str(filename)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:NRZC:FORMat:SAVE {param}')

	def clone(self) -> 'FormatPyCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = FormatPyCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group

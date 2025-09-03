from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class QspiCls:
	"""Qspi commands group definition. 91 total commands, 15 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("qspi", core, parent)

	@property
	def fcount(self):
		"""fcount commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fcount'):
			from .Fcount import FcountCls
			self._fcount = FcountCls(self._core, self._cmd_group)
		return self._fcount

	@property
	def instruction(self):
		"""instruction commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_instruction'):
			from .Instruction import InstructionCls
			self._instruction = InstructionCls(self._core, self._cmd_group)
		return self._instruction

	@property
	def ldopCode(self):
		"""ldopCode commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_ldopCode'):
			from .LdopCode import LdopCodeCls
			self._ldopCode = LdopCodeCls(self._core, self._cmd_group)
		return self._ldopCode

	@property
	def svop(self):
		"""svop commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_svop'):
			from .Svop import SvopCls
			self._svop = SvopCls(self._core, self._cmd_group)
		return self._svop

	@property
	def swtIndex(self):
		"""swtIndex commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_swtIndex'):
			from .SwtIndex import SwtIndexCls
			self._swtIndex = SwtIndexCls(self._core, self._cmd_group)
		return self._swtIndex

	@property
	def swtTime(self):
		"""swtTime commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_swtTime'):
			from .SwtTime import SwtTimeCls
			self._swtTime = SwtTimeCls(self._core, self._cmd_group)
		return self._swtTime

	@property
	def opCode(self):
		"""opCode commands group. 4 Sub-classes, 2 commands."""
		if not hasattr(self, '_opCode'):
			from .OpCode import OpCodeCls
			self._opCode = OpCodeCls(self._core, self._cmd_group)
		return self._opCode

	@property
	def csel(self):
		"""csel commands group. 4 Sub-classes, 0 commands."""
		if not hasattr(self, '_csel'):
			from .Csel import CselCls
			self._csel = CselCls(self._core, self._cmd_group)
		return self._csel

	@property
	def sclk(self):
		"""sclk commands group. 4 Sub-classes, 0 commands."""
		if not hasattr(self, '_sclk'):
			from .Sclk import SclkCls
			self._sclk = SclkCls(self._core, self._cmd_group)
		return self._sclk

	@property
	def ioZero(self):
		"""ioZero commands group. 6 Sub-classes, 0 commands."""
		if not hasattr(self, '_ioZero'):
			from .IoZero import IoZeroCls
			self._ioZero = IoZeroCls(self._core, self._cmd_group)
		return self._ioZero

	@property
	def ioOne(self):
		"""ioOne commands group. 6 Sub-classes, 0 commands."""
		if not hasattr(self, '_ioOne'):
			from .IoOne import IoOneCls
			self._ioOne = IoOneCls(self._core, self._cmd_group)
		return self._ioOne

	@property
	def ioTwo(self):
		"""ioTwo commands group. 6 Sub-classes, 0 commands."""
		if not hasattr(self, '_ioTwo'):
			from .IoTwo import IoTwoCls
			self._ioTwo = IoTwoCls(self._core, self._cmd_group)
		return self._ioTwo

	@property
	def ioThree(self):
		"""ioThree commands group. 6 Sub-classes, 0 commands."""
		if not hasattr(self, '_ioThree'):
			from .IoThree import IoThreeCls
			self._ioThree = IoThreeCls(self._core, self._cmd_group)
		return self._ioThree

	@property
	def frame(self):
		"""frame commands group. 12 Sub-classes, 0 commands."""
		if not hasattr(self, '_frame'):
			from .Frame import FrameCls
			self._frame = FrameCls(self._core, self._cmd_group)
		return self._frame

	@property
	def filterPy(self):
		"""filterPy commands group. 16 Sub-classes, 0 commands."""
		if not hasattr(self, '_filterPy'):
			from .FilterPy import FilterPyCls
			self._filterPy = FilterPyCls(self._core, self._cmd_group)
		return self._filterPy

	def clone(self) -> 'QspiCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = QspiCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group

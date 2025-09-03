from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SpiCls:
	"""Spi commands group definition. 62 total commands, 13 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("spi", core, parent)

	@property
	def fcount(self):
		"""fcount commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fcount'):
			from .Fcount import FcountCls
			self._fcount = FcountCls(self._core, self._cmd_group)
		return self._fcount

	@property
	def border(self):
		"""border commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_border'):
			from .Border import BorderCls
			self._border = BorderCls(self._core, self._cmd_group)
		return self._border

	@property
	def wsize(self):
		"""wsize commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_wsize'):
			from .Wsize import WsizeCls
			self._wsize = WsizeCls(self._core, self._cmd_group)
		return self._wsize

	@property
	def frCondition(self):
		"""frCondition commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_frCondition'):
			from .FrCondition import FrConditionCls
			self._frCondition = FrConditionCls(self._core, self._cmd_group)
		return self._frCondition

	@property
	def timeout(self):
		"""timeout commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_timeout'):
			from .Timeout import TimeoutCls
			self._timeout = TimeoutCls(self._core, self._cmd_group)
		return self._timeout

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
	def mosi(self):
		"""mosi commands group. 6 Sub-classes, 0 commands."""
		if not hasattr(self, '_mosi'):
			from .Mosi import MosiCls
			self._mosi = MosiCls(self._core, self._cmd_group)
		return self._mosi

	@property
	def miso(self):
		"""miso commands group. 6 Sub-classes, 0 commands."""
		if not hasattr(self, '_miso'):
			from .Miso import MisoCls
			self._miso = MisoCls(self._core, self._cmd_group)
		return self._miso

	@property
	def sclk(self):
		"""sclk commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_sclk'):
			from .Sclk import SclkCls
			self._sclk = SclkCls(self._core, self._cmd_group)
		return self._sclk

	@property
	def cselect(self):
		"""cselect commands group. 4 Sub-classes, 0 commands."""
		if not hasattr(self, '_cselect'):
			from .Cselect import CselectCls
			self._cselect = CselectCls(self._core, self._cmd_group)
		return self._cselect

	@property
	def frame(self):
		"""frame commands group. 7 Sub-classes, 0 commands."""
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

	def clone(self) -> 'SpiCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = SpiCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group

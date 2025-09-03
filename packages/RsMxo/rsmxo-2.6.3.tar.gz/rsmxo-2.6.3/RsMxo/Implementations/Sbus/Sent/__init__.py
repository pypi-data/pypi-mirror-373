from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SentCls:
	"""Sent commands group definition. 68 total commands, 20 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("sent", core, parent)

	@property
	def fcount(self):
		"""fcount commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fcount'):
			from .Fcount import FcountCls
			self._fcount = FcountCls(self._core, self._cmd_group)
		return self._fcount

	@property
	def scale(self):
		"""scale commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_scale'):
			from .Scale import ScaleCls
			self._scale = ScaleCls(self._core, self._cmd_group)
		return self._scale

	@property
	def position(self):
		"""position commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_position'):
			from .Position import PositionCls
			self._position = PositionCls(self._core, self._cmd_group)
		return self._position

	@property
	def symbols(self):
		"""symbols commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_symbols'):
			from .Symbols import SymbolsCls
			self._symbols = SymbolsCls(self._core, self._cmd_group)
		return self._symbols

	@property
	def newlist(self):
		"""newlist commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_newlist'):
			from .Newlist import NewlistCls
			self._newlist = NewlistCls(self._core, self._cmd_group)
		return self._newlist

	@property
	def mode(self):
		"""mode commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_mode'):
			from .Mode import ModeCls
			self._mode = ModeCls(self._core, self._cmd_group)
		return self._mode

	@property
	def crcVersion(self):
		"""crcVersion commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_crcVersion'):
			from .CrcVersion import CrcVersionCls
			self._crcVersion = CrcVersionCls(self._core, self._cmd_group)
		return self._crcVersion

	@property
	def crcMethod(self):
		"""crcMethod commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_crcMethod'):
			from .CrcMethod import CrcMethodCls
			self._crcMethod = CrcMethodCls(self._core, self._cmd_group)
		return self._crcMethod

	@property
	def clkPeriod(self):
		"""clkPeriod commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_clkPeriod'):
			from .ClkPeriod import ClkPeriodCls
			self._clkPeriod = ClkPeriodCls(self._core, self._cmd_group)
		return self._clkPeriod

	@property
	def clkTolerance(self):
		"""clkTolerance commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_clkTolerance'):
			from .ClkTolerance import ClkToleranceCls
			self._clkTolerance = ClkToleranceCls(self._core, self._cmd_group)
		return self._clkTolerance

	@property
	def dnibbles(self):
		"""dnibbles commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_dnibbles'):
			from .Dnibbles import DnibblesCls
			self._dnibbles = DnibblesCls(self._core, self._cmd_group)
		return self._dnibbles

	@property
	def sformat(self):
		"""sformat commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_sformat'):
			from .Sformat import SformatCls
			self._sformat = SformatCls(self._core, self._cmd_group)
		return self._sformat

	@property
	def ppulse(self):
		"""ppulse commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_ppulse'):
			from .Ppulse import PpulseCls
			self._ppulse = PpulseCls(self._core, self._cmd_group)
		return self._ppulse

	@property
	def ppfLength(self):
		"""ppfLength commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_ppfLength'):
			from .PpfLength import PpfLengthCls
			self._ppfLength = PpfLengthCls(self._core, self._cmd_group)
		return self._ppfLength

	@property
	def rdsl(self):
		"""rdsl commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_rdsl'):
			from .Rdsl import RdslCls
			self._rdsl = RdslCls(self._core, self._cmd_group)
		return self._rdsl

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
	def data(self):
		"""data commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_data'):
			from .Data import DataCls
			self._data = DataCls(self._core, self._cmd_group)
		return self._data

	@property
	def frame(self):
		"""frame commands group. 21 Sub-classes, 0 commands."""
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

	def clone(self) -> 'SentCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = SentCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group

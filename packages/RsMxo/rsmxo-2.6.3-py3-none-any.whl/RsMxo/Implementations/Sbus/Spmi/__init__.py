from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SpmiCls:
	"""Spmi commands group definition. 57 total commands, 15 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("spmi", core, parent)

	@property
	def fcount(self):
		"""fcount commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fcount'):
			from .Fcount import FcountCls
			self._fcount = FcountCls(self._core, self._cmd_group)
		return self._fcount

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
	def gsidEnable(self):
		"""gsidEnable commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_gsidEnable'):
			from .GsidEnable import GsidEnableCls
			self._gsidEnable = GsidEnableCls(self._core, self._cmd_group)
		return self._gsidEnable

	@property
	def gidValue(self):
		"""gidValue commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_gidValue'):
			from .GidValue import GidValueCls
			self._gidValue = GidValueCls(self._core, self._cmd_group)
		return self._gidValue

	@property
	def gtchEnable(self):
		"""gtchEnable commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_gtchEnable'):
			from .GtchEnable import GtchEnableCls
			self._gtchEnable = GtchEnableCls(self._core, self._cmd_group)
		return self._gtchEnable

	@property
	def gtwdith(self):
		"""gtwdith commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_gtwdith'):
			from .Gtwdith import GtwdithCls
			self._gtwdith = GtwdithCls(self._core, self._cmd_group)
		return self._gtwdith

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
	def sdata(self):
		"""sdata commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_sdata'):
			from .Sdata import SdataCls
			self._sdata = SdataCls(self._core, self._cmd_group)
		return self._sdata

	@property
	def sclk(self):
		"""sclk commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_sclk'):
			from .Sclk import SclkCls
			self._sclk = SclkCls(self._core, self._cmd_group)
		return self._sclk

	@property
	def frame(self):
		"""frame commands group. 13 Sub-classes, 0 commands."""
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

	def clone(self) -> 'SpmiCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = SpmiCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group

from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class LinCls:
	"""Lin commands group definition. 52 total commands, 13 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("lin", core, parent)

	@property
	def fcount(self):
		"""fcount commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fcount'):
			from .Fcount import FcountCls
			self._fcount = FcountCls(self._core, self._cmd_group)
		return self._fcount

	@property
	def standard(self):
		"""standard commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_standard'):
			from .Standard import StandardCls
			self._standard = StandardCls(self._core, self._cmd_group)
		return self._standard

	@property
	def bitrate(self):
		"""bitrate commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_bitrate'):
			from .Bitrate import BitrateCls
			self._bitrate = BitrateCls(self._core, self._cmd_group)
		return self._bitrate

	@property
	def polarity(self):
		"""polarity commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_polarity'):
			from .Polarity import PolarityCls
			self._polarity = PolarityCls(self._core, self._cmd_group)
		return self._polarity

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

	def clone(self) -> 'LinCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = LinCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group

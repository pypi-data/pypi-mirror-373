from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ArincCls:
	"""Arinc commands group definition. 46 total commands, 16 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("arinc", core, parent)

	@property
	def polarity(self):
		"""polarity commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_polarity'):
			from .Polarity import PolarityCls
			self._polarity = PolarityCls(self._core, self._cmd_group)
		return self._polarity

	@property
	def source(self):
		"""source commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_source'):
			from .Source import SourceCls
			self._source = SourceCls(self._core, self._cmd_group)
		return self._source

	@property
	def brMode(self):
		"""brMode commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_brMode'):
			from .BrMode import BrModeCls
			self._brMode = BrModeCls(self._core, self._cmd_group)
		return self._brMode

	@property
	def brValue(self):
		"""brValue commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_brValue'):
			from .BrValue import BrValueCls
			self._brValue = BrValueCls(self._core, self._cmd_group)
		return self._brValue

	@property
	def wcount(self):
		"""wcount commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_wcount'):
			from .Wcount import WcountCls
			self._wcount = WcountCls(self._core, self._cmd_group)
		return self._wcount

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
	def threshold(self):
		"""threshold commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_threshold'):
			from .Threshold import ThresholdCls
			self._threshold = ThresholdCls(self._core, self._cmd_group)
		return self._threshold

	@property
	def minGap(self):
		"""minGap commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_minGap'):
			from .MinGap import MinGapCls
			self._minGap = MinGapCls(self._core, self._cmd_group)
		return self._minGap

	@property
	def maxGap(self):
		"""maxGap commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_maxGap'):
			from .MaxGap import MaxGapCls
			self._maxGap = MaxGapCls(self._core, self._cmd_group)
		return self._maxGap

	@property
	def word(self):
		"""word commands group. 10 Sub-classes, 0 commands."""
		if not hasattr(self, '_word'):
			from .Word import WordCls
			self._word = WordCls(self._core, self._cmd_group)
		return self._word

	@property
	def filterPy(self):
		"""filterPy commands group. 13 Sub-classes, 0 commands."""
		if not hasattr(self, '_filterPy'):
			from .FilterPy import FilterPyCls
			self._filterPy = FilterPyCls(self._core, self._cmd_group)
		return self._filterPy

	def clone(self) -> 'ArincCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ArincCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group

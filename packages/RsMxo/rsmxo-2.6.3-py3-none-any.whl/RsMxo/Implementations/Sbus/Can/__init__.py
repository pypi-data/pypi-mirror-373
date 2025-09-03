from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CanCls:
	"""Can commands group definition. 78 total commands, 18 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("can", core, parent)

	@property
	def typePy(self):
		"""typePy commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_typePy'):
			from .TypePy import TypePyCls
			self._typePy = TypePyCls(self._core, self._cmd_group)
		return self._typePy

	@property
	def trcvMode(self):
		"""trcvMode commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_trcvMode'):
			from .TrcvMode import TrcvModeCls
			self._trcvMode = TrcvModeCls(self._core, self._cmd_group)
		return self._trcvMode

	@property
	def bitrate(self):
		"""bitrate commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_bitrate'):
			from .Bitrate import BitrateCls
			self._bitrate = BitrateCls(self._core, self._cmd_group)
		return self._bitrate

	@property
	def samplePoint(self):
		"""samplePoint commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_samplePoint'):
			from .SamplePoint import SamplePointCls
			self._samplePoint = SamplePointCls(self._core, self._cmd_group)
		return self._samplePoint

	@property
	def fcount(self):
		"""fcount commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fcount'):
			from .Fcount import FcountCls
			self._fcount = FcountCls(self._core, self._cmd_group)
		return self._fcount

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
	def source(self):
		"""source commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_source'):
			from .Source import SourceCls
			self._source = SourceCls(self._core, self._cmd_group)
		return self._source

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
	def sic(self):
		"""sic commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_sic'):
			from .Sic import SicCls
			self._sic = SicCls(self._core, self._cmd_group)
		return self._sic

	@property
	def fast(self):
		"""fast commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_fast'):
			from .Fast import FastCls
			self._fast = FastCls(self._core, self._cmd_group)
		return self._fast

	@property
	def frame(self):
		"""frame commands group. 25 Sub-classes, 0 commands."""
		if not hasattr(self, '_frame'):
			from .Frame import FrameCls
			self._frame = FrameCls(self._core, self._cmd_group)
		return self._frame

	@property
	def fdata(self):
		"""fdata commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_fdata'):
			from .Fdata import FdataCls
			self._fdata = FdataCls(self._core, self._cmd_group)
		return self._fdata

	@property
	def xdata(self):
		"""xdata commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_xdata'):
			from .Xdata import XdataCls
			self._xdata = XdataCls(self._core, self._cmd_group)
		return self._xdata

	@property
	def filterPy(self):
		"""filterPy commands group. 16 Sub-classes, 0 commands."""
		if not hasattr(self, '_filterPy'):
			from .FilterPy import FilterPyCls
			self._filterPy = FilterPyCls(self._core, self._cmd_group)
		return self._filterPy

	def clone(self) -> 'CanCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = CanCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group

from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FilterPyCls:
	"""FilterPy commands group definition. 24 total commands, 16 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("filterPy", core, parent)

	@property
	def chkAll(self):
		"""chkAll commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_chkAll'):
			from .ChkAll import ChkAllCls
			self._chkAll = ChkAllCls(self._core, self._cmd_group)
		return self._chkAll

	@property
	def clr(self):
		"""clr commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_clr'):
			from .Clr import ClrCls
			self._clr = ClrCls(self._core, self._cmd_group)
		return self._clr

	@property
	def invert(self):
		"""invert commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_invert'):
			from .Invert import InvertCls
			self._invert = InvertCls(self._core, self._cmd_group)
		return self._invert

	@property
	def rst(self):
		"""rst commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_rst'):
			from .Rst import RstCls
			self._rst = RstCls(self._core, self._cmd_group)
		return self._rst

	@property
	def erEnable(self):
		"""erEnable commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_erEnable'):
			from .ErEnable import ErEnableCls
			self._erEnable = ErEnableCls(self._core, self._cmd_group)
		return self._erEnable

	@property
	def frEnable(self):
		"""frEnable commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_frEnable'):
			from .FrEnable import FrEnableCls
			self._frEnable = FrEnableCls(self._core, self._cmd_group)
		return self._frEnable

	@property
	def fiEnable(self):
		"""fiEnable commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fiEnable'):
			from .FiEnable import FiEnableCls
			self._fiEnable = FiEnableCls(self._core, self._cmd_group)
		return self._fiEnable

	@property
	def bit(self):
		"""bit commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_bit'):
			from .Bit import BitCls
			self._bit = BitCls(self._core, self._cmd_group)
		return self._bit

	@property
	def doperator(self):
		"""doperator commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_doperator'):
			from .Doperator import DoperatorCls
			self._doperator = DoperatorCls(self._core, self._cmd_group)
		return self._doperator

	@property
	def dmin(self):
		"""dmin commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_dmin'):
			from .Dmin import DminCls
			self._dmin = DminCls(self._core, self._cmd_group)
		return self._dmin

	@property
	def dmax(self):
		"""dmax commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_dmax'):
			from .Dmax import DmaxCls
			self._dmax = DmaxCls(self._core, self._cmd_group)
		return self._dmax

	@property
	def ioperator(self):
		"""ioperator commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_ioperator'):
			from .Ioperator import IoperatorCls
			self._ioperator = IoperatorCls(self._core, self._cmd_group)
		return self._ioperator

	@property
	def imin(self):
		"""imin commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_imin'):
			from .Imin import IminCls
			self._imin = IminCls(self._core, self._cmd_group)
		return self._imin

	@property
	def imax(self):
		"""imax commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_imax'):
			from .Imax import ImaxCls
			self._imax = ImaxCls(self._core, self._cmd_group)
		return self._imax

	@property
	def error(self):
		"""error commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_error'):
			from .Error import ErrorCls
			self._error = ErrorCls(self._core, self._cmd_group)
		return self._error

	@property
	def frame(self):
		"""frame commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_frame'):
			from .Frame import FrameCls
			self._frame = FrameCls(self._core, self._cmd_group)
		return self._frame

	def clone(self) -> 'FilterPyCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = FilterPyCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group

from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal.RepeatedCapability import RepeatedCapability
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FrameCls:
	"""Frame commands group definition. 19 total commands, 16 Subgroups, 0 group commands
	Repeated Capability: Frame, default value after init: Frame.Ix1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("frame", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_frame_get', 'repcap_frame_set', repcap.Frame.Ix1)

	def repcap_frame_set(self, frame: repcap.Frame) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Frame.Default.
		Default value after init: Frame.Ix1"""
		self._cmd_group.set_repcap_enum_value(frame)

	def repcap_frame_get(self) -> repcap.Frame:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def fldCount(self):
		"""fldCount commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fldCount'):
			from .FldCount import FldCountCls
			self._fldCount = FldCountCls(self._core, self._cmd_group)
		return self._fldCount

	@property
	def state(self):
		"""state commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_state'):
			from .State import StateCls
			self._state = StateCls(self._core, self._cmd_group)
		return self._state

	@property
	def start(self):
		"""start commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_start'):
			from .Start import StartCls
			self._start = StartCls(self._core, self._cmd_group)
		return self._start

	@property
	def stop(self):
		"""stop commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_stop'):
			from .Stop import StopCls
			self._stop = StopCls(self._core, self._cmd_group)
		return self._stop

	@property
	def typePy(self):
		"""typePy commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_typePy'):
			from .TypePy import TypePyCls
			self._typePy = TypePyCls(self._core, self._cmd_group)
		return self._typePy

	@property
	def sadd(self):
		"""sadd commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_sadd'):
			from .Sadd import SaddCls
			self._sadd = SaddCls(self._core, self._cmd_group)
		return self._sadd

	@property
	def bcount(self):
		"""bcount commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_bcount'):
			from .Bcount import BcountCls
			self._bcount = BcountCls(self._core, self._cmd_group)
		return self._bcount

	@property
	def address(self):
		"""address commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_address'):
			from .Address import AddressCls
			self._address = AddressCls(self._core, self._cmd_group)
		return self._address

	@property
	def symbol(self):
		"""symbol commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_symbol'):
			from .Symbol import SymbolCls
			self._symbol = SymbolCls(self._core, self._cmd_group)
		return self._symbol

	@property
	def data(self):
		"""data commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_data'):
			from .Data import DataCls
			self._data = DataCls(self._core, self._cmd_group)
		return self._data

	@property
	def wbtRate(self):
		"""wbtRate commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_wbtRate'):
			from .WbtRate import WbtRateCls
			self._wbtRate = WbtRateCls(self._core, self._cmd_group)
		return self._wbtRate

	@property
	def rbtRate(self):
		"""rbtRate commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_rbtRate'):
			from .RbtRate import RbtRateCls
			self._rbtRate = RbtRateCls(self._core, self._cmd_group)
		return self._rbtRate

	@property
	def pctrl(self):
		"""pctrl commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_pctrl'):
			from .Pctrl import PctrlCls
			self._pctrl = PctrlCls(self._core, self._cmd_group)
		return self._pctrl

	@property
	def padZero(self):
		"""padZero commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_padZero'):
			from .PadZero import PadZeroCls
			self._padZero = PadZeroCls(self._core, self._cmd_group)
		return self._padZero

	@property
	def padOne(self):
		"""padOne commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_padOne'):
			from .PadOne import PadOneCls
			self._padOne = PadOneCls(self._core, self._cmd_group)
		return self._padOne

	@property
	def fld(self):
		"""fld commands group. 4 Sub-classes, 0 commands."""
		if not hasattr(self, '_fld'):
			from .Fld import FldCls
			self._fld = FldCls(self._core, self._cmd_group)
		return self._fld

	def clone(self) -> 'FrameCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = FrameCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group

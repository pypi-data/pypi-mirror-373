from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal.RepeatedCapability import RepeatedCapability
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FrameCls:
	"""Frame commands group definition. 34 total commands, 25 Subgroups, 0 group commands
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
	def status(self):
		"""status commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_status'):
			from .Status import StatusCls
			self._status = StatusCls(self._core, self._cmd_group)
		return self._status

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
	def idState(self):
		"""idState commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_idState'):
			from .IdState import IdStateCls
			self._idState = IdStateCls(self._core, self._cmd_group)
		return self._idState

	@property
	def idType(self):
		"""idType commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_idType'):
			from .IdType import IdTypeCls
			self._idType = IdTypeCls(self._core, self._cmd_group)
		return self._idType

	@property
	def idValue(self):
		"""idValue commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_idValue'):
			from .IdValue import IdValueCls
			self._idValue = IdValueCls(self._core, self._cmd_group)
		return self._idValue

	@property
	def dlcState(self):
		"""dlcState commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_dlcState'):
			from .DlcState import DlcStateCls
			self._dlcState = DlcStateCls(self._core, self._cmd_group)
		return self._dlcState

	@property
	def dlcValue(self):
		"""dlcValue commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_dlcValue'):
			from .DlcValue import DlcValueCls
			self._dlcValue = DlcValueCls(self._core, self._cmd_group)
		return self._dlcValue

	@property
	def ndBytes(self):
		"""ndBytes commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_ndBytes'):
			from .NdBytes import NdBytesCls
			self._ndBytes = NdBytesCls(self._core, self._cmd_group)
		return self._ndBytes

	@property
	def stuff(self):
		"""stuff commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_stuff'):
			from .Stuff import StuffCls
			self._stuff = StuffCls(self._core, self._cmd_group)
		return self._stuff

	@property
	def csState(self):
		"""csState commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_csState'):
			from .CsState import CsStateCls
			self._csState = CsStateCls(self._core, self._cmd_group)
		return self._csState

	@property
	def csValue(self):
		"""csValue commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_csValue'):
			from .CsValue import CsValueCls
			self._csValue = CsValueCls(self._core, self._cmd_group)
		return self._csValue

	@property
	def ackState(self):
		"""ackState commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_ackState'):
			from .AckState import AckStateCls
			self._ackState = AckStateCls(self._core, self._cmd_group)
		return self._ackState

	@property
	def ackValue(self):
		"""ackValue commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_ackValue'):
			from .AckValue import AckValueCls
			self._ackValue = AckValueCls(self._core, self._cmd_group)
		return self._ackValue

	@property
	def data(self):
		"""data commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_data'):
			from .Data import DataCls
			self._data = DataCls(self._core, self._cmd_group)
		return self._data

	@property
	def symbol(self):
		"""symbol commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_symbol'):
			from .Symbol import SymbolCls
			self._symbol = SymbolCls(self._core, self._cmd_group)
		return self._symbol

	@property
	def nbitrate(self):
		"""nbitrate commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_nbitrate'):
			from .Nbitrate import NbitrateCls
			self._nbitrate = NbitrateCls(self._core, self._cmd_group)
		return self._nbitrate

	@property
	def dbitrate(self):
		"""dbitrate commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_dbitrate'):
			from .Dbitrate import DbitrateCls
			self._dbitrate = DbitrateCls(self._core, self._cmd_group)
		return self._dbitrate

	@property
	def ferCause(self):
		"""ferCause commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_ferCause'):
			from .FerCause import FerCauseCls
			self._ferCause = FerCauseCls(self._core, self._cmd_group)
		return self._ferCause

	@property
	def sbc(self):
		"""sbc commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_sbc'):
			from .Sbc import SbcCls
			self._sbc = SbcCls(self._core, self._cmd_group)
		return self._sbc

	@property
	def fdata(self):
		"""fdata commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_fdata'):
			from .Fdata import FdataCls
			self._fdata = FdataCls(self._core, self._cmd_group)
		return self._fdata

	@property
	def xdata(self):
		"""xdata commands group. 6 Sub-classes, 0 commands."""
		if not hasattr(self, '_xdata'):
			from .Xdata import XdataCls
			self._xdata = XdataCls(self._core, self._cmd_group)
		return self._xdata

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

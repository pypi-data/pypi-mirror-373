from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal.RepeatedCapability import RepeatedCapability
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FrameCls:
	"""Frame commands group definition. 24 total commands, 21 Subgroups, 0 group commands
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
	def syncDuration(self):
		"""syncDuration commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_syncDuration'):
			from .SyncDuration import SyncDurationCls
			self._syncDuration = SyncDurationCls(self._core, self._cmd_group)
		return self._syncDuration

	@property
	def scom(self):
		"""scom commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_scom'):
			from .Scom import ScomCls
			self._scom = ScomCls(self._core, self._cmd_group)
		return self._scom

	@property
	def fsCom(self):
		"""fsCom commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fsCom'):
			from .FsCom import FsComCls
			self._fsCom = FsComCls(self._core, self._cmd_group)
		return self._fsCom

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
	def fdValues(self):
		"""fdValues commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fdValues'):
			from .FdValues import FdValuesCls
			self._fdValues = FdValuesCls(self._core, self._cmd_group)
		return self._fdValues

	@property
	def csValue(self):
		"""csValue commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_csValue'):
			from .CsValue import CsValueCls
			self._csValue = CsValueCls(self._core, self._cmd_group)
		return self._csValue

	@property
	def papTicks(self):
		"""papTicks commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_papTicks'):
			from .PapTicks import PapTicksCls
			self._papTicks = PapTicksCls(self._core, self._cmd_group)
		return self._papTicks

	@property
	def mtpDuration(self):
		"""mtpDuration commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_mtpDuration'):
			from .MtpDuration import MtpDurationCls
			self._mtpDuration = MtpDurationCls(self._core, self._cmd_group)
		return self._mtpDuration

	@property
	def sensor(self):
		"""sensor commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_sensor'):
			from .Sensor import SensorCls
			self._sensor = SensorCls(self._core, self._cmd_group)
		return self._sensor

	@property
	def symbol(self):
		"""symbol commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_symbol'):
			from .Symbol import SymbolCls
			self._symbol = SymbolCls(self._core, self._cmd_group)
		return self._symbol

	@property
	def sdata(self):
		"""sdata commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_sdata'):
			from .Sdata import SdataCls
			self._sdata = SdataCls(self._core, self._cmd_group)
		return self._sdata

	@property
	def fsDta(self):
		"""fsDta commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fsDta'):
			from .FsDta import FsDtaCls
			self._fsDta = FsDtaCls(self._core, self._cmd_group)
		return self._fsDta

	@property
	def bitrate(self):
		"""bitrate commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_bitrate'):
			from .Bitrate import BitrateCls
			self._bitrate = BitrateCls(self._core, self._cmd_group)
		return self._bitrate

	@property
	def data(self):
		"""data commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_data'):
			from .Data import DataCls
			self._data = DataCls(self._core, self._cmd_group)
		return self._data

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

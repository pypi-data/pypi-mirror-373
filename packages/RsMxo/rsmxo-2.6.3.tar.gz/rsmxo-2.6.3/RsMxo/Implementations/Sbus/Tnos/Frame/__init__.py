from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal.RepeatedCapability import RepeatedCapability
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FrameCls:
	"""Frame commands group definition. 22 total commands, 19 Subgroups, 0 group commands
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
	def dtAddress(self):
		"""dtAddress commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_dtAddress'):
			from .DtAddress import DtAddressCls
			self._dtAddress = DtAddressCls(self._core, self._cmd_group)
		return self._dtAddress

	@property
	def fdtAddress(self):
		"""fdtAddress commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fdtAddress'):
			from .FdtAddress import FdtAddressCls
			self._fdtAddress = FdtAddressCls(self._core, self._cmd_group)
		return self._fdtAddress

	@property
	def srAddress(self):
		"""srAddress commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_srAddress'):
			from .SrAddress import SrAddressCls
			self._srAddress = SrAddressCls(self._core, self._cmd_group)
		return self._srAddress

	@property
	def fsrAddress(self):
		"""fsrAddress commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fsrAddress'):
			from .FsrAddress import FsrAddressCls
			self._fsrAddress = FsrAddressCls(self._core, self._cmd_group)
		return self._fsrAddress

	@property
	def dtSymbol(self):
		"""dtSymbol commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_dtSymbol'):
			from .DtSymbol import DtSymbolCls
			self._dtSymbol = DtSymbolCls(self._core, self._cmd_group)
		return self._dtSymbol

	@property
	def srSymbol(self):
		"""srSymbol commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_srSymbol'):
			from .SrSymbol import SrSymbolCls
			self._srSymbol = SrSymbolCls(self._core, self._cmd_group)
		return self._srSymbol

	@property
	def tpLength(self):
		"""tpLength commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_tpLength'):
			from .TpLength import TpLengthCls
			self._tpLength = TpLengthCls(self._core, self._cmd_group)
		return self._tpLength

	@property
	def ftpLength(self):
		"""ftpLength commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_ftpLength'):
			from .FtpLength import FtpLengthCls
			self._ftpLength = FtpLengthCls(self._core, self._cmd_group)
		return self._ftpLength

	@property
	def fdata(self):
		"""fdata commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fdata'):
			from .Fdata import FdataCls
			self._fdata = FdataCls(self._core, self._cmd_group)
		return self._fdata

	@property
	def crc(self):
		"""crc commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_crc'):
			from .Crc import CrcCls
			self._crc = CrcCls(self._core, self._cmd_group)
		return self._crc

	@property
	def fcRc(self):
		"""fcRc commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fcRc'):
			from .FcRc import FcRcCls
			self._fcRc = FcRcCls(self._core, self._cmd_group)
		return self._fcRc

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

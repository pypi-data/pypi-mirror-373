from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal.RepeatedCapability import RepeatedCapability
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FrameCls:
	"""Frame commands group definition. 21 total commands, 17 Subgroups, 0 group commands
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
	def astart(self):
		"""astart commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_astart'):
			from .Astart import AstartCls
			self._astart = AstartCls(self._core, self._cmd_group)
		return self._astart

	@property
	def acomplete(self):
		"""acomplete commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_acomplete'):
			from .Acomplete import AcompleteCls
			self._acomplete = AcompleteCls(self._core, self._cmd_group)
		return self._acomplete

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
	def adevice(self):
		"""adevice commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_adevice'):
			from .Adevice import AdeviceCls
			self._adevice = AdeviceCls(self._core, self._cmd_group)
		return self._adevice

	@property
	def amode(self):
		"""amode commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_amode'):
			from .Amode import AmodeCls
			self._amode = AmodeCls(self._core, self._cmd_group)
		return self._amode

	@property
	def adbStart(self):
		"""adbStart commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_adbStart'):
			from .AdbStart import AdbStartCls
			self._adbStart = AdbStartCls(self._core, self._cmd_group)
		return self._adbStart

	@property
	def aaccess(self):
		"""aaccess commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_aaccess'):
			from .Aaccess import AaccessCls
			self._aaccess = AaccessCls(self._core, self._cmd_group)
		return self._aaccess

	@property
	def rwbStart(self):
		"""rwbStart commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_rwbStart'):
			from .RwbStart import RwbStartCls
			self._rwbStart = RwbStartCls(self._core, self._cmd_group)
		return self._rwbStart

	@property
	def access(self):
		"""access commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_access'):
			from .Access import AccessCls
			self._access = AccessCls(self._core, self._cmd_group)
		return self._access

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
		"""fld commands group. 5 Sub-classes, 0 commands."""
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

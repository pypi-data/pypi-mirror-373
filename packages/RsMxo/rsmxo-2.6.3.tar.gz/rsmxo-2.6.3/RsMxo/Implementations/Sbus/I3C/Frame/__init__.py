from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal.RepeatedCapability import RepeatedCapability
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FrameCls:
	"""Frame commands group definition. 23 total commands, 20 Subgroups, 0 group commands
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
	def typePy(self):
		"""typePy commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_typePy'):
			from .TypePy import TypePyCls
			self._typePy = TypePyCls(self._core, self._cmd_group)
		return self._typePy

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
	def command(self):
		"""command commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_command'):
			from .Command import CommandCls
			self._command = CommandCls(self._core, self._cmd_group)
		return self._command

	@property
	def fcommand(self):
		"""fcommand commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fcommand'):
			from .Fcommand import FcommandCls
			self._fcommand = FcommandCls(self._core, self._cmd_group)
		return self._fcommand

	@property
	def astart(self):
		"""astart commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_astart'):
			from .Astart import AstartCls
			self._astart = AstartCls(self._core, self._cmd_group)
		return self._astart

	@property
	def address(self):
		"""address commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_address'):
			from .Address import AddressCls
			self._address = AddressCls(self._core, self._cmd_group)
		return self._address

	@property
	def faddress(self):
		"""faddress commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_faddress'):
			from .Faddress import FaddressCls
			self._faddress = FaddressCls(self._core, self._cmd_group)
		return self._faddress

	@property
	def symbol(self):
		"""symbol commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_symbol'):
			from .Symbol import SymbolCls
			self._symbol = SymbolCls(self._core, self._cmd_group)
		return self._symbol

	@property
	def ackStart(self):
		"""ackStart commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_ackStart'):
			from .AckStart import AckStartCls
			self._ackStart = AckStartCls(self._core, self._cmd_group)
		return self._ackStart

	@property
	def ack(self):
		"""ack commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_ack'):
			from .Ack import AckCls
			self._ack = AckCls(self._core, self._cmd_group)
		return self._ack

	@property
	def rwbStart(self):
		"""rwbStart commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_rwbStart'):
			from .RwbStart import RwbStartCls
			self._rwbStart = RwbStartCls(self._core, self._cmd_group)
		return self._rwbStart

	@property
	def rwbIt(self):
		"""rwbIt commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_rwbIt'):
			from .RwbIt import RwbItCls
			self._rwbIt = RwbItCls(self._core, self._cmd_group)
		return self._rwbIt

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

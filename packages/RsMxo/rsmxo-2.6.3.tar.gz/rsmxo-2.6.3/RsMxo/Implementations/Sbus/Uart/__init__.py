from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class UartCls:
	"""Uart commands group definition. 52 total commands, 15 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("uart", core, parent)

	@property
	def polarity(self):
		"""polarity commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_polarity'):
			from .Polarity import PolarityCls
			self._polarity = PolarityCls(self._core, self._cmd_group)
		return self._polarity

	@property
	def ssize(self):
		"""ssize commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_ssize'):
			from .Ssize import SsizeCls
			self._ssize = SsizeCls(self._core, self._cmd_group)
		return self._ssize

	@property
	def wcount(self):
		"""wcount commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_wcount'):
			from .Wcount import WcountCls
			self._wcount = WcountCls(self._core, self._cmd_group)
		return self._wcount

	@property
	def parity(self):
		"""parity commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_parity'):
			from .Parity import ParityCls
			self._parity = ParityCls(self._core, self._cmd_group)
		return self._parity

	@property
	def sbit(self):
		"""sbit commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_sbit'):
			from .Sbit import SbitCls
			self._sbit = SbitCls(self._core, self._cmd_group)
		return self._sbit

	@property
	def border(self):
		"""border commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_border'):
			from .Border import BorderCls
			self._border = BorderCls(self._core, self._cmd_group)
		return self._border

	@property
	def bitrate(self):
		"""bitrate commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_bitrate'):
			from .Bitrate import BitrateCls
			self._bitrate = BitrateCls(self._core, self._cmd_group)
		return self._bitrate

	@property
	def packets(self):
		"""packets commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_packets'):
			from .Packets import PacketsCls
			self._packets = PacketsCls(self._core, self._cmd_group)
		return self._packets

	@property
	def timeout(self):
		"""timeout commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_timeout'):
			from .Timeout import TimeoutCls
			self._timeout = TimeoutCls(self._core, self._cmd_group)
		return self._timeout

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
	def tx(self):
		"""tx commands group. 5 Sub-classes, 0 commands."""
		if not hasattr(self, '_tx'):
			from .Tx import TxCls
			self._tx = TxCls(self._core, self._cmd_group)
		return self._tx

	@property
	def rx(self):
		"""rx commands group. 5 Sub-classes, 0 commands."""
		if not hasattr(self, '_rx'):
			from .Rx import RxCls
			self._rx = RxCls(self._core, self._cmd_group)
		return self._rx

	@property
	def word(self):
		"""word commands group. 7 Sub-classes, 0 commands."""
		if not hasattr(self, '_word'):
			from .Word import WordCls
			self._word = WordCls(self._core, self._cmd_group)
		return self._word

	@property
	def filterPy(self):
		"""filterPy commands group. 16 Sub-classes, 0 commands."""
		if not hasattr(self, '_filterPy'):
			from .FilterPy import FilterPyCls
			self._filterPy = FilterPyCls(self._core, self._cmd_group)
		return self._filterPy

	def clone(self) -> 'UartCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = UartCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group

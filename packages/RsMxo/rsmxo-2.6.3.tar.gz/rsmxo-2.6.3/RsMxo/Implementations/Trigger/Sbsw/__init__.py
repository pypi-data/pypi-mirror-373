from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SbswCls:
	"""Sbsw commands group definition. 402 total commands, 17 Subgroups, 0 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("sbsw", core, parent)

	@property
	def arinc(self):
		"""arinc commands group. 13 Sub-classes, 0 commands."""
		if not hasattr(self, '_arinc'):
			from .Arinc import ArincCls
			self._arinc = ArincCls(self._core, self._cmd_group)
		return self._arinc

	@property
	def can(self):
		"""can commands group. 16 Sub-classes, 0 commands."""
		if not hasattr(self, '_can'):
			from .Can import CanCls
			self._can = CanCls(self._core, self._cmd_group)
		return self._can

	@property
	def hbto(self):
		"""hbto commands group. 16 Sub-classes, 0 commands."""
		if not hasattr(self, '_hbto'):
			from .Hbto import HbtoCls
			self._hbto = HbtoCls(self._core, self._cmd_group)
		return self._hbto

	@property
	def i2C(self):
		"""i2C commands group. 16 Sub-classes, 0 commands."""
		if not hasattr(self, '_i2C'):
			from .I2C import I2CCls
			self._i2C = I2CCls(self._core, self._cmd_group)
		return self._i2C

	@property
	def i3C(self):
		"""i3C commands group. 16 Sub-classes, 0 commands."""
		if not hasattr(self, '_i3C'):
			from .I3C import I3CCls
			self._i3C = I3CCls(self._core, self._cmd_group)
		return self._i3C

	@property
	def lin(self):
		"""lin commands group. 16 Sub-classes, 0 commands."""
		if not hasattr(self, '_lin'):
			from .Lin import LinCls
			self._lin = LinCls(self._core, self._cmd_group)
		return self._lin

	@property
	def milstd(self):
		"""milstd commands group. 16 Sub-classes, 0 commands."""
		if not hasattr(self, '_milstd'):
			from .Milstd import MilstdCls
			self._milstd = MilstdCls(self._core, self._cmd_group)
		return self._milstd

	@property
	def nrzc(self):
		"""nrzc commands group. 16 Sub-classes, 0 commands."""
		if not hasattr(self, '_nrzc'):
			from .Nrzc import NrzcCls
			self._nrzc = NrzcCls(self._core, self._cmd_group)
		return self._nrzc

	@property
	def nrzu(self):
		"""nrzu commands group. 16 Sub-classes, 0 commands."""
		if not hasattr(self, '_nrzu'):
			from .Nrzu import NrzuCls
			self._nrzu = NrzuCls(self._core, self._cmd_group)
		return self._nrzu

	@property
	def qspi(self):
		"""qspi commands group. 16 Sub-classes, 0 commands."""
		if not hasattr(self, '_qspi'):
			from .Qspi import QspiCls
			self._qspi = QspiCls(self._core, self._cmd_group)
		return self._qspi

	@property
	def rffe(self):
		"""rffe commands group. 16 Sub-classes, 0 commands."""
		if not hasattr(self, '_rffe'):
			from .Rffe import RffeCls
			self._rffe = RffeCls(self._core, self._cmd_group)
		return self._rffe

	@property
	def sent(self):
		"""sent commands group. 16 Sub-classes, 0 commands."""
		if not hasattr(self, '_sent'):
			from .Sent import SentCls
			self._sent = SentCls(self._core, self._cmd_group)
		return self._sent

	@property
	def swire(self):
		"""swire commands group. 16 Sub-classes, 0 commands."""
		if not hasattr(self, '_swire'):
			from .Swire import SwireCls
			self._swire = SwireCls(self._core, self._cmd_group)
		return self._swire

	@property
	def spi(self):
		"""spi commands group. 16 Sub-classes, 0 commands."""
		if not hasattr(self, '_spi'):
			from .Spi import SpiCls
			self._spi = SpiCls(self._core, self._cmd_group)
		return self._spi

	@property
	def spmi(self):
		"""spmi commands group. 16 Sub-classes, 0 commands."""
		if not hasattr(self, '_spmi'):
			from .Spmi import SpmiCls
			self._spmi = SpmiCls(self._core, self._cmd_group)
		return self._spmi

	@property
	def tnos(self):
		"""tnos commands group. 16 Sub-classes, 0 commands."""
		if not hasattr(self, '_tnos'):
			from .Tnos import TnosCls
			self._tnos = TnosCls(self._core, self._cmd_group)
		return self._tnos

	@property
	def uart(self):
		"""uart commands group. 16 Sub-classes, 0 commands."""
		if not hasattr(self, '_uart'):
			from .Uart import UartCls
			self._uart = UartCls(self._core, self._cmd_group)
		return self._uart

	def clone(self) -> 'SbswCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = SbswCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group

from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal.RepeatedCapability import RepeatedCapability
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SbusCls:
	"""Sbus commands group definition. 1051 total commands, 27 Subgroups, 0 group commands
	Repeated Capability: SerialBus, default value after init: SerialBus.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("sbus", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_serialBus_get', 'repcap_serialBus_set', repcap.SerialBus.Nr1)

	def repcap_serialBus_set(self, serialBus: repcap.SerialBus) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to SerialBus.Default.
		Default value after init: SerialBus.Nr1"""
		self._cmd_group.set_repcap_enum_value(serialBus)

	def repcap_serialBus_get(self) -> repcap.SerialBus:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def arinc(self):
		"""arinc commands group. 16 Sub-classes, 0 commands."""
		if not hasattr(self, '_arinc'):
			from .Arinc import ArincCls
			self._arinc = ArincCls(self._core, self._cmd_group)
		return self._arinc

	@property
	def can(self):
		"""can commands group. 18 Sub-classes, 0 commands."""
		if not hasattr(self, '_can'):
			from .Can import CanCls
			self._can = CanCls(self._core, self._cmd_group)
		return self._can

	@property
	def hbto(self):
		"""hbto commands group. 12 Sub-classes, 0 commands."""
		if not hasattr(self, '_hbto'):
			from .Hbto import HbtoCls
			self._hbto = HbtoCls(self._core, self._cmd_group)
		return self._hbto

	@property
	def i2C(self):
		"""i2C commands group. 11 Sub-classes, 0 commands."""
		if not hasattr(self, '_i2C'):
			from .I2C import I2CCls
			self._i2C = I2CCls(self._core, self._cmd_group)
		return self._i2C

	@property
	def i3C(self):
		"""i3C commands group. 12 Sub-classes, 0 commands."""
		if not hasattr(self, '_i3C'):
			from .I3C import I3CCls
			self._i3C = I3CCls(self._core, self._cmd_group)
		return self._i3C

	@property
	def lin(self):
		"""lin commands group. 13 Sub-classes, 0 commands."""
		if not hasattr(self, '_lin'):
			from .Lin import LinCls
			self._lin = LinCls(self._core, self._cmd_group)
		return self._lin

	@property
	def milstd(self):
		"""milstd commands group. 12 Sub-classes, 0 commands."""
		if not hasattr(self, '_milstd'):
			from .Milstd import MilstdCls
			self._milstd = MilstdCls(self._core, self._cmd_group)
		return self._milstd

	@property
	def nrzc(self):
		"""nrzc commands group. 12 Sub-classes, 0 commands."""
		if not hasattr(self, '_nrzc'):
			from .Nrzc import NrzcCls
			self._nrzc = NrzcCls(self._core, self._cmd_group)
		return self._nrzc

	@property
	def nrzu(self):
		"""nrzu commands group. 12 Sub-classes, 2 commands."""
		if not hasattr(self, '_nrzu'):
			from .Nrzu import NrzuCls
			self._nrzu = NrzuCls(self._core, self._cmd_group)
		return self._nrzu

	@property
	def qspi(self):
		"""qspi commands group. 15 Sub-classes, 0 commands."""
		if not hasattr(self, '_qspi'):
			from .Qspi import QspiCls
			self._qspi = QspiCls(self._core, self._cmd_group)
		return self._qspi

	@property
	def rffe(self):
		"""rffe commands group. 14 Sub-classes, 0 commands."""
		if not hasattr(self, '_rffe'):
			from .Rffe import RffeCls
			self._rffe = RffeCls(self._core, self._cmd_group)
		return self._rffe

	@property
	def sent(self):
		"""sent commands group. 20 Sub-classes, 0 commands."""
		if not hasattr(self, '_sent'):
			from .Sent import SentCls
			self._sent = SentCls(self._core, self._cmd_group)
		return self._sent

	@property
	def typePy(self):
		"""typePy commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_typePy'):
			from .TypePy import TypePyCls
			self._typePy = TypePyCls(self._core, self._cmd_group)
		return self._typePy

	@property
	def state(self):
		"""state commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_state'):
			from .State import StateCls
			self._state = StateCls(self._core, self._cmd_group)
		return self._state

	@property
	def result(self):
		"""result commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_result'):
			from .Result import ResultCls
			self._result = ResultCls(self._core, self._cmd_group)
		return self._result

	@property
	def threshold(self):
		"""threshold commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_threshold'):
			from .Threshold import ThresholdCls
			self._threshold = ThresholdCls(self._core, self._cmd_group)
		return self._threshold

	@property
	def formatPy(self):
		"""formatPy commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_formatPy'):
			from .FormatPy import FormatPyCls
			self._formatPy = FormatPyCls(self._core, self._cmd_group)
		return self._formatPy

	@property
	def zcoupling(self):
		"""zcoupling commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_zcoupling'):
			from .Zcoupling import ZcouplingCls
			self._zcoupling = ZcouplingCls(self._core, self._cmd_group)
		return self._zcoupling

	@property
	def rmsBus(self):
		"""rmsBus commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_rmsBus'):
			from .RmsBus import RmsBusCls
			self._rmsBus = RmsBusCls(self._core, self._cmd_group)
		return self._rmsBus

	@property
	def trgHardware(self):
		"""trgHardware commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_trgHardware'):
			from .TrgHardware import TrgHardwareCls
			self._trgHardware = TrgHardwareCls(self._core, self._cmd_group)
		return self._trgHardware

	@property
	def trgSoftware(self):
		"""trgSoftware commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_trgSoftware'):
			from .TrgSoftware import TrgSoftwareCls
			self._trgSoftware = TrgSoftwareCls(self._core, self._cmd_group)
		return self._trgSoftware

	@property
	def expResult(self):
		"""expResult commands group. 4 Sub-classes, 1 commands."""
		if not hasattr(self, '_expResult'):
			from .ExpResult import ExpResultCls
			self._expResult = ExpResultCls(self._core, self._cmd_group)
		return self._expResult

	@property
	def swire(self):
		"""swire commands group. 11 Sub-classes, 0 commands."""
		if not hasattr(self, '_swire'):
			from .Swire import SwireCls
			self._swire = SwireCls(self._core, self._cmd_group)
		return self._swire

	@property
	def spi(self):
		"""spi commands group. 13 Sub-classes, 0 commands."""
		if not hasattr(self, '_spi'):
			from .Spi import SpiCls
			self._spi = SpiCls(self._core, self._cmd_group)
		return self._spi

	@property
	def spmi(self):
		"""spmi commands group. 15 Sub-classes, 0 commands."""
		if not hasattr(self, '_spmi'):
			from .Spmi import SpmiCls
			self._spmi = SpmiCls(self._core, self._cmd_group)
		return self._spmi

	@property
	def tnos(self):
		"""tnos commands group. 11 Sub-classes, 0 commands."""
		if not hasattr(self, '_tnos'):
			from .Tnos import TnosCls
			self._tnos = TnosCls(self._core, self._cmd_group)
		return self._tnos

	@property
	def uart(self):
		"""uart commands group. 15 Sub-classes, 0 commands."""
		if not hasattr(self, '_uart'):
			from .Uart import UartCls
			self._uart = UartCls(self._core, self._cmd_group)
		return self._uart

	def clone(self) -> 'SbusCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = SbusCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group

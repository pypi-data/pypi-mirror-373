from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal.RepeatedCapability import RepeatedCapability
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PbusCls:
	"""Pbus commands group definition. 25 total commands, 16 Subgroups, 1 group commands
	Repeated Capability: PwrBus, default value after init: PwrBus.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("pbus", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_pwrBus_get', 'repcap_pwrBus_set', repcap.PwrBus.Nr1)

	def repcap_pwrBus_set(self, pwrBus: repcap.PwrBus) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to PwrBus.Default.
		Default value after init: PwrBus.Nr1"""
		self._cmd_group.set_repcap_enum_value(pwrBus)

	def repcap_pwrBus_get(self) -> repcap.PwrBus:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def threshold(self):
		"""threshold commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_threshold'):
			from .Threshold import ThresholdCls
			self._threshold = ThresholdCls(self._core, self._cmd_group)
		return self._threshold

	@property
	def thCoupling(self):
		"""thCoupling commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_thCoupling'):
			from .ThCoupling import ThCouplingCls
			self._thCoupling = ThCouplingCls(self._core, self._cmd_group)
		return self._thCoupling

	@property
	def technology(self):
		"""technology commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_technology'):
			from .Technology import TechnologyCls
			self._technology = TechnologyCls(self._core, self._cmd_group)
		return self._technology

	@property
	def hysteresis(self):
		"""hysteresis commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_hysteresis'):
			from .Hysteresis import HysteresisCls
			self._hysteresis = HysteresisCls(self._core, self._cmd_group)
		return self._hysteresis

	@property
	def state(self):
		"""state commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_state'):
			from .State import StateCls
			self._state = StateCls(self._core, self._cmd_group)
		return self._state

	@property
	def skew(self):
		"""skew commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_skew'):
			from .Skew import SkewCls
			self._skew = SkewCls(self._core, self._cmd_group)
		return self._skew

	@property
	def clon(self):
		"""clon commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_clon'):
			from .Clon import ClonCls
			self._clon = ClonCls(self._core, self._cmd_group)
		return self._clon

	@property
	def clock(self):
		"""clock commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_clock'):
			from .Clock import ClockCls
			self._clock = ClockCls(self._core, self._cmd_group)
		return self._clock

	@property
	def clSlope(self):
		"""clSlope commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_clSlope'):
			from .ClSlope import ClSlopeCls
			self._clSlope = ClSlopeCls(self._core, self._cmd_group)
		return self._clSlope

	@property
	def scale(self):
		"""scale commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_scale'):
			from .Scale import ScaleCls
			self._scale = ScaleCls(self._core, self._cmd_group)
		return self._scale

	@property
	def position(self):
		"""position commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_position'):
			from .Position import PositionCls
			self._position = PositionCls(self._core, self._cmd_group)
		return self._position

	@property
	def digSignals(self):
		"""digSignals commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_digSignals'):
			from .DigSignals import DigSignalsCls
			self._digSignals = DigSignalsCls(self._core, self._cmd_group)
		return self._digSignals

	@property
	def display(self):
		"""display commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_display'):
			from .Display import DisplayCls
			self._display = DisplayCls(self._core, self._cmd_group)
		return self._display

	@property
	def bit(self):
		"""bit commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_bit'):
			from .Bit import BitCls
			self._bit = BitCls(self._core, self._cmd_group)
		return self._bit

	@property
	def data(self):
		"""data commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_data'):
			from .Data import DataCls
			self._data = DataCls(self._core, self._cmd_group)
		return self._data

	@property
	def decTable(self):
		"""decTable commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_decTable'):
			from .DecTable import DecTableCls
			self._decTable = DecTableCls(self._core, self._cmd_group)
		return self._decTable

	def clear(self, pwrBus=repcap.PwrBus.Default) -> None:
		"""PBUS<*>:CLEar \n
		Snippet: driver.pbus.clear(pwrBus = repcap.PwrBus.Default) \n
		Removes all assigned digital channels from the bus. \n
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
		"""
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		self._core.io.write(f'PBUS{pwrBus_cmd_val}:CLEar')

	def clear_and_wait(self, pwrBus=repcap.PwrBus.Default, opc_timeout_ms: int = -1) -> None:
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		"""PBUS<*>:CLEar \n
		Snippet: driver.pbus.clear_and_wait(pwrBus = repcap.PwrBus.Default) \n
		Removes all assigned digital channels from the bus. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'PBUS{pwrBus_cmd_val}:CLEar', opc_timeout_ms)

	def clone(self) -> 'PbusCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = PbusCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group

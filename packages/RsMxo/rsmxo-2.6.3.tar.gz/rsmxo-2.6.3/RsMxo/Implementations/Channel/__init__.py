from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal.RepeatedCapability import RepeatedCapability
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ChannelCls:
	"""Channel commands group definition. 43 total commands, 20 Subgroups, 0 group commands
	Repeated Capability: Channel, default value after init: Channel.Ch1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("channel", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_channel_get', 'repcap_channel_set', repcap.Channel.Ch1)

	def repcap_channel_set(self, channel: repcap.Channel) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Channel.Default.
		Default value after init: Channel.Ch1"""
		self._cmd_group.set_repcap_enum_value(channel)

	def repcap_channel_get(self) -> repcap.Channel:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def data(self):
		"""data commands group. 3 Sub-classes, 0 commands."""
		if not hasattr(self, '_data'):
			from .Data import DataCls
			self._data = DataCls(self._core, self._cmd_group)
		return self._data

	@property
	def bandwidth(self):
		"""bandwidth commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_bandwidth'):
			from .Bandwidth import BandwidthCls
			self._bandwidth = BandwidthCls(self._core, self._cmd_group)
		return self._bandwidth

	@property
	def coupling(self):
		"""coupling commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_coupling'):
			from .Coupling import CouplingCls
			self._coupling = CouplingCls(self._core, self._cmd_group)
		return self._coupling

	@property
	def invert(self):
		"""invert commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_invert'):
			from .Invert import InvertCls
			self._invert = InvertCls(self._core, self._cmd_group)
		return self._invert

	@property
	def offset(self):
		"""offset commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_offset'):
			from .Offset import OffsetCls
			self._offset = OffsetCls(self._core, self._cmd_group)
		return self._offset

	@property
	def position(self):
		"""position commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_position'):
			from .Position import PositionCls
			self._position = PositionCls(self._core, self._cmd_group)
		return self._position

	@property
	def range(self):
		"""range commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_range'):
			from .Range import RangeCls
			self._range = RangeCls(self._core, self._cmd_group)
		return self._range

	@property
	def scale(self):
		"""scale commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_scale'):
			from .Scale import ScaleCls
			self._scale = ScaleCls(self._core, self._cmd_group)
		return self._scale

	@property
	def eattenuation(self):
		"""eattenuation commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_eattenuation'):
			from .Eattenuation import EattenuationCls
			self._eattenuation = EattenuationCls(self._core, self._cmd_group)
		return self._eattenuation

	@property
	def eatScale(self):
		"""eatScale commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_eatScale'):
			from .EatScale import EatScaleCls
			self._eatScale = EatScaleCls(self._core, self._cmd_group)
		return self._eatScale

	@property
	def state(self):
		"""state commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_state'):
			from .State import StateCls
			self._state = StateCls(self._core, self._cmd_group)
		return self._state

	@property
	def impedance(self):
		"""impedance commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_impedance'):
			from .Impedance import ImpedanceCls
			self._impedance = ImpedanceCls(self._core, self._cmd_group)
		return self._impedance

	@property
	def filDesign(self):
		"""filDesign commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_filDesign'):
			from .FilDesign import FilDesignCls
			self._filDesign = FilDesignCls(self._core, self._cmd_group)
		return self._filDesign

	@property
	def filFrequency(self):
		"""filFrequency commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_filFrequency'):
			from .FilFrequency import FilFrequencyCls
			self._filFrequency = FilFrequencyCls(self._core, self._cmd_group)
		return self._filFrequency

	@property
	def fila(self):
		"""fila commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_fila'):
			from .Fila import FilaCls
			self._fila = FilaCls(self._core, self._cmd_group)
		return self._fila

	@property
	def overload(self):
		"""overload commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_overload'):
			from .Overload import OverloadCls
			self._overload = OverloadCls(self._core, self._cmd_group)
		return self._overload

	@property
	def warnOverload(self):
		"""warnOverload commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_warnOverload'):
			from .WarnOverload import WarnOverloadCls
			self._warnOverload = WarnOverloadCls(self._core, self._cmd_group)
		return self._warnOverload

	@property
	def adcState(self):
		"""adcState commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_adcState'):
			from .AdcState import AdcStateCls
			self._adcState = AdcStateCls(self._core, self._cmd_group)
		return self._adcState

	@property
	def ppSupply(self):
		"""ppSupply commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_ppSupply'):
			from .PpSupply import PpSupplyCls
			self._ppSupply = PpSupplyCls(self._core, self._cmd_group)
		return self._ppSupply

	@property
	def skew(self):
		"""skew commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_skew'):
			from .Skew import SkewCls
			self._skew = SkewCls(self._core, self._cmd_group)
		return self._skew

	def clone(self) -> 'ChannelCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ChannelCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group

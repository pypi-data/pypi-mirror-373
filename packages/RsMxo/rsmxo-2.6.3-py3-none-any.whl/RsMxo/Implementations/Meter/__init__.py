from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.RepeatedCapability import RepeatedCapability
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MeterCls:
	"""Meter commands group definition. 9 total commands, 1 Subgroups, 2 group commands
	Repeated Capability: Voltmeter, default value after init: Voltmeter.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("meter", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_voltmeter_get', 'repcap_voltmeter_set', repcap.Voltmeter.Nr1)

	def repcap_voltmeter_set(self, voltmeter: repcap.Voltmeter) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Voltmeter.Default.
		Default value after init: Voltmeter.Nr1"""
		self._cmd_group.set_repcap_enum_value(voltmeter)

	def repcap_voltmeter_get(self) -> repcap.Voltmeter:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	@property
	def dvMeter(self):
		"""dvMeter commands group. 4 Sub-classes, 0 commands."""
		if not hasattr(self, '_dvMeter'):
			from .DvMeter import DvMeterCls
			self._dvMeter = DvMeterCls(self._core, self._cmd_group)
		return self._dvMeter

	# noinspection PyTypeChecker
	def get_bandwidth(self) -> enums.MeterBandwidth:
		"""METer:BANDwidth \n
		Snippet: value: enums.MeterBandwidth = driver.meter.get_bandwidth() \n
		Sets the filter bandwidth. \n
			:return: bandwidth: B20M: 20 MHz B10M: 10 MHz B5M: 5 MHz B2M: 2 MHz B1M: 1 MHz B500: 500 kHz B200: 200 kHz
		"""
		response = self._core.io.query_str('METer:BANDwidth?')
		return Conversions.str_to_scalar_enum(response, enums.MeterBandwidth)

	def set_bandwidth(self, bandwidth: enums.MeterBandwidth) -> None:
		"""METer:BANDwidth \n
		Snippet: driver.meter.set_bandwidth(bandwidth = enums.MeterBandwidth.B100) \n
		Sets the filter bandwidth. \n
			:param bandwidth: B20M: 20 MHz B10M: 10 MHz B5M: 5 MHz B2M: 2 MHz B1M: 1 MHz B500: 500 kHz B200: 200 kHz
		"""
		param = Conversions.enum_scalar_to_str(bandwidth, enums.MeterBandwidth)
		self._core.io.write(f'METer:BANDwidth {param}')

	def get_mtime(self) -> float:
		"""METer:MTIMe \n
		Snippet: value: float = driver.meter.get_mtime() \n
		Sets the measurement time. The time begins in the moment that a measurement is enabled. \n
			:return: meas_time: No help available
		"""
		response = self._core.io.query_str('METer:MTIMe?')
		return Conversions.str_to_float(response)

	def set_mtime(self, meas_time: float) -> None:
		"""METer:MTIMe \n
		Snippet: driver.meter.set_mtime(meas_time = 1.0) \n
		Sets the measurement time. The time begins in the moment that a measurement is enabled. \n
			:param meas_time: No help available
		"""
		param = Conversions.decimal_value_to_str(meas_time)
		self._core.io.write(f'METer:MTIMe {param}')

	def clone(self) -> 'MeterCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = MeterCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group

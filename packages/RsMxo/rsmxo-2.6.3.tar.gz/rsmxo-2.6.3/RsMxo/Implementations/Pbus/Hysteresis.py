from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.RepeatedCapability import RepeatedCapability
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HysteresisCls:
	"""Hysteresis commands group definition. 1 total commands, 0 Subgroups, 1 group commands
	Repeated Capability: Hyst, default value after init: Hyst.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("hysteresis", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_hyst_get', 'repcap_hyst_set', repcap.Hyst.Nr1)

	def repcap_hyst_set(self, hyst: repcap.Hyst) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Hyst.Default.
		Default value after init: Hyst.Nr1"""
		self._cmd_group.set_repcap_enum_value(hyst)

	def repcap_hyst_get(self) -> repcap.Hyst:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	def set(self, hysteresis: enums.Hysteresis, pwrBus=repcap.PwrBus.Default, hyst=repcap.Hyst.Default) -> None:
		"""PBUS<*>:HYSTeresis<*> \n
		Snippet: driver.pbus.hysteresis.set(hysteresis = enums.Hysteresis.MAXimum, pwrBus = repcap.PwrBus.Default, hyst = repcap.Hyst.Default) \n
		Defines the size of the hysteresis for the respective channels. \n
			:param hysteresis:
				- MAXIMUM = MAXimum: Maximum value that is possible and useful for the signal and its settings
				- ROBUST = ROBust: Different hysteresis values for falling and rising edges to avoid an undefined state of the trigger system.
				- NORMAL = NORMal: The instrument sets a value suitable for the signal and its settings.
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:param hyst: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Hysteresis')"""
		param = Conversions.enum_scalar_to_str(hysteresis, enums.Hysteresis)
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		hyst_cmd_val = self._cmd_group.get_repcap_cmd_value(hyst, repcap.Hyst)
		self._core.io.write(f'PBUS{pwrBus_cmd_val}:HYSTeresis{hyst_cmd_val} {param}')

	# noinspection PyTypeChecker
	def get(self, pwrBus=repcap.PwrBus.Default, hyst=repcap.Hyst.Default) -> enums.Hysteresis:
		"""PBUS<*>:HYSTeresis<*> \n
		Snippet: value: enums.Hysteresis = driver.pbus.hysteresis.get(pwrBus = repcap.PwrBus.Default, hyst = repcap.Hyst.Default) \n
		Defines the size of the hysteresis for the respective channels. \n
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:param hyst: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Hysteresis')
			:return: hysteresis:
				- MAXIMUM = MAXimum: Maximum value that is possible and useful for the signal and its settings
				- ROBUST = ROBust: Different hysteresis values for falling and rising edges to avoid an undefined state of the trigger system.
				- NORMAL = NORMal: The instrument sets a value suitable for the signal and its settings."""
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		hyst_cmd_val = self._cmd_group.get_repcap_cmd_value(hyst, repcap.Hyst)
		response = self._core.io.query_str(f'PBUS{pwrBus_cmd_val}:HYSTeresis{hyst_cmd_val}?')
		return Conversions.str_to_scalar_enum(response, enums.Hysteresis)

	def clone(self) -> 'HysteresisCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = HysteresisCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group

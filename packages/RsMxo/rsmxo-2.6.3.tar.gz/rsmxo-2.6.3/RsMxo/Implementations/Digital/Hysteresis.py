from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HysteresisCls:
	"""Hysteresis commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("hysteresis", core, parent)

	def set(self, hysteresis: enums.Hysteresis, digital=repcap.Digital.Default) -> None:
		"""DIGital<*>:HYSTeresis \n
		Snippet: driver.digital.hysteresis.set(hysteresis = enums.Hysteresis.MAXimum, digital = repcap.Digital.Default) \n
		Sets the hysteresis for the indicated digital channel. The setting affects only the settings of the first MSO bus
		(Logic1) . You can set the hysteresis for all buses with PBUS<pb>:HYSTeresis<n>. \n
			:param hysteresis:
				- MAXimum: Maximum value that is possible and useful for the signal and its settings, to be used for noisy signals.
				- ROBust: Different hysteresis values for falling and rising edges to avoid an undefined state of the trigger system, to be used for very noisy signals.
				- NORMal: Small value suitable for the signal and its settings, to be used for clean signals.
			:param digital: optional repeated capability selector. Default value: Nr0 (settable in the interface 'Digital')"""
		param = Conversions.enum_scalar_to_str(hysteresis, enums.Hysteresis)
		digital_cmd_val = self._cmd_group.get_repcap_cmd_value(digital, repcap.Digital)
		self._core.io.write(f'DIGital{digital_cmd_val}:HYSTeresis {param}')

	# noinspection PyTypeChecker
	def get(self, digital=repcap.Digital.Default) -> enums.Hysteresis:
		"""DIGital<*>:HYSTeresis \n
		Snippet: value: enums.Hysteresis = driver.digital.hysteresis.get(digital = repcap.Digital.Default) \n
		Sets the hysteresis for the indicated digital channel. The setting affects only the settings of the first MSO bus
		(Logic1) . You can set the hysteresis for all buses with PBUS<pb>:HYSTeresis<n>. \n
			:param digital: optional repeated capability selector. Default value: Nr0 (settable in the interface 'Digital')
			:return: hysteresis:
				- MAXimum: Maximum value that is possible and useful for the signal and its settings, to be used for noisy signals.
				- ROBust: Different hysteresis values for falling and rising edges to avoid an undefined state of the trigger system, to be used for very noisy signals.
				- NORMal: Small value suitable for the signal and its settings, to be used for clean signals."""
		digital_cmd_val = self._cmd_group.get_repcap_cmd_value(digital, repcap.Digital)
		response = self._core.io.query_str(f'DIGital{digital_cmd_val}:HYSTeresis?')
		return Conversions.str_to_scalar_enum(response, enums.Hysteresis)

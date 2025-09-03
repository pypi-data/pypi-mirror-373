from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ClSlopeCls:
	"""ClSlope commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("clSlope", core, parent)

	def set(self, clock_slope: enums.PulseSlope, pwrBus=repcap.PwrBus.Default) -> None:
		"""PBUS<*>:CLSLope \n
		Snippet: driver.pbus.clSlope.set(clock_slope = enums.PulseSlope.EITHer, pwrBus = repcap.PwrBus.Default) \n
		Selects the slope of the clock signal at which all digital channels of the bus are analyzed. \n
			:param clock_slope: No help available
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
		"""
		param = Conversions.enum_scalar_to_str(clock_slope, enums.PulseSlope)
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		self._core.io.write(f'PBUS{pwrBus_cmd_val}:CLSLope {param}')

	# noinspection PyTypeChecker
	def get(self, pwrBus=repcap.PwrBus.Default) -> enums.PulseSlope:
		"""PBUS<*>:CLSLope \n
		Snippet: value: enums.PulseSlope = driver.pbus.clSlope.get(pwrBus = repcap.PwrBus.Default) \n
		Selects the slope of the clock signal at which all digital channels of the bus are analyzed. \n
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:return: clock_slope: No help available"""
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		response = self._core.io.query_str(f'PBUS{pwrBus_cmd_val}:CLSLope?')
		return Conversions.str_to_scalar_enum(response, enums.PulseSlope)

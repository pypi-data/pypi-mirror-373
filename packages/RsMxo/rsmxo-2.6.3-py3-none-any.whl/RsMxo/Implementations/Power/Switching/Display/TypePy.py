from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TypePyCls:
	"""TypePy commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("typePy", core, parent)

	def set(self, unit: enums.PowerUnit, power=repcap.Power.Default) -> None:
		"""POWer<*>:SWITching:DISPlay:TYPE \n
		Snippet: driver.power.switching.display.typePy.set(unit = enums.PowerUnit.ENERgy, power = repcap.Power.Default) \n
		Selects the measurement type: power or energy. \n
			:param unit: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.enum_scalar_to_str(unit, enums.PowerUnit)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:SWITching:DISPlay:TYPE {param}')

	# noinspection PyTypeChecker
	def get(self, power=repcap.Power.Default) -> enums.PowerUnit:
		"""POWer<*>:SWITching:DISPlay:TYPE \n
		Snippet: value: enums.PowerUnit = driver.power.switching.display.typePy.get(power = repcap.Power.Default) \n
		Selects the measurement type: power or energy. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: unit: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:SWITching:DISPlay:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.PowerUnit)

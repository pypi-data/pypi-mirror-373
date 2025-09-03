from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TypePyCls:
	"""TypePy commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("typePy", core, parent)

	def set(self, type_py: enums.PowerType, power=repcap.Power.Default) -> None:
		"""POWer<*>:TYPE \n
		Snippet: driver.power.typePy.set(type_py = enums.PowerType.EFFiciency, power = repcap.Power.Default) \n
		Sets the type for the respective power analysis measurement. \n
			:param type_py: SWITching = switching loss ONOFf = turn on/off time
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.PowerType)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:TYPE {param}')

	# noinspection PyTypeChecker
	def get(self, power=repcap.Power.Default) -> enums.PowerType:
		"""POWer<*>:TYPE \n
		Snippet: value: enums.PowerType = driver.power.typePy.get(power = repcap.Power.Default) \n
		Sets the type for the respective power analysis measurement. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: type_py: SWITching = switching loss ONOFf = turn on/off time"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.PowerType)

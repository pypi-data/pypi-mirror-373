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

	def set(self, input_type: enums.PowerCoupling, power=repcap.Power.Default) -> None:
		"""POWer<*>:ONOFf:INPut:TYPE \n
		Snippet: driver.power.onOff.inputPy.typePy.set(input_type = enums.PowerCoupling.AC, power = repcap.Power.Default) \n
		Selects whether the input signal is AC or CD. \n
			:param input_type: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.enum_scalar_to_str(input_type, enums.PowerCoupling)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:ONOFf:INPut:TYPE {param}')

	# noinspection PyTypeChecker
	def get(self, power=repcap.Power.Default) -> enums.PowerCoupling:
		"""POWer<*>:ONOFf:INPut:TYPE \n
		Snippet: value: enums.PowerCoupling = driver.power.onOff.inputPy.typePy.get(power = repcap.Power.Default) \n
		Selects whether the input signal is AC or CD. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: input_type: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:ONOFf:INPut:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.PowerCoupling)

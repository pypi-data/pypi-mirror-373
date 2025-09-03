from .......Internal.Core import Core
from .......Internal.CommandsGroup import CommandsGroup
from .......Internal import Conversions
from ....... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ValueCls:
	"""Value commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("value", core, parent)

	def set(self, input_dc_thres_abs: float, power=repcap.Power.Default) -> None:
		"""POWer<*>:ONOFf:INPut:DC:ABSolute[:VALue] \n
		Snippet: driver.power.onOff.inputPy.dc.absolute.value.set(input_dc_thres_abs = 1.0, power = repcap.Power.Default) \n
		Sets the threshold for the DC input signal. \n
			:param input_dc_thres_abs: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.decimal_value_to_str(input_dc_thres_abs)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:ONOFf:INPut:DC:ABSolute:VALue {param}')

	def get(self, power=repcap.Power.Default) -> float:
		"""POWer<*>:ONOFf:INPut:DC:ABSolute[:VALue] \n
		Snippet: value: float = driver.power.onOff.inputPy.dc.absolute.value.get(power = repcap.Power.Default) \n
		Sets the threshold for the DC input signal. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: input_dc_thres_abs: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:ONOFf:INPut:DC:ABSolute:VALue?')
		return Conversions.str_to_float(response)

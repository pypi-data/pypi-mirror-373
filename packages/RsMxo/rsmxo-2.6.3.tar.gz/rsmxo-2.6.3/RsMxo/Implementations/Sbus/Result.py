from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ResultCls:
	"""Result commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("result", core, parent)

	def set(self, shw_res_tbl: bool, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:RESult \n
		Snippet: driver.sbus.result.set(shw_res_tbl = False, serialBus = repcap.SerialBus.Default) \n
		Enables a table with decoded data of the serial signal. The function requires the option for the analyzed protocol. \n
			:param shw_res_tbl: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.bool_to_str(shw_res_tbl)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:RESult {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> bool:
		"""SBUS<*>:RESult \n
		Snippet: value: bool = driver.sbus.result.get(serialBus = repcap.SerialBus.Default) \n
		Enables a table with decoded data of the serial signal. The function requires the option for the analyzed protocol. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: shw_res_tbl: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:RESult?')
		return Conversions.str_to_bool(response)

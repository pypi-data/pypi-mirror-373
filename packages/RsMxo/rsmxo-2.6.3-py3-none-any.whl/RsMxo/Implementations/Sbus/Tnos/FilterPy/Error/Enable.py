from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EnableCls:
	"""Enable commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("enable", core, parent)

	def set(self, enable: bool, serialBus=repcap.SerialBus.Default, error=repcap.Error.Default) -> None:
		"""SBUS<*>:TNOS:FILTer:ERRor<*>:ENABle \n
		Snippet: driver.sbus.tnos.filterPy.error.enable.set(enable = False, serialBus = repcap.SerialBus.Default, error = repcap.Error.Default) \n
		rcset \n
			:param enable: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param error: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Error')
		"""
		param = Conversions.bool_to_str(enable)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		error_cmd_val = self._cmd_group.get_repcap_cmd_value(error, repcap.Error)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:TNOS:FILTer:ERRor{error_cmd_val}:ENABle {param}')

	def get(self, serialBus=repcap.SerialBus.Default, error=repcap.Error.Default) -> bool:
		"""SBUS<*>:TNOS:FILTer:ERRor<*>:ENABle \n
		Snippet: value: bool = driver.sbus.tnos.filterPy.error.enable.get(serialBus = repcap.SerialBus.Default, error = repcap.Error.Default) \n
		rcset \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param error: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Error')
			:return: enable: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		error_cmd_val = self._cmd_group.get_repcap_cmd_value(error, repcap.Error)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:TNOS:FILTer:ERRor{error_cmd_val}:ENABle?')
		return Conversions.str_to_bool(response)

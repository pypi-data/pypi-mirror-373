from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class GidValueCls:
	"""GidValue commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("gidValue", core, parent)

	def set(self, gs_id: int, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:SPMI:GIDValue \n
		Snippet: driver.sbus.spmi.gidValue.set(gs_id = 1, serialBus = repcap.SerialBus.Default) \n
		Sets a value for the group sub index. Available, if method RsMxo.Sbus.Spmi.GsidEnable.set is set to ON. \n
			:param gs_id: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(gs_id)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:SPMI:GIDValue {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> int:
		"""SBUS<*>:SPMI:GIDValue \n
		Snippet: value: int = driver.sbus.spmi.gidValue.get(serialBus = repcap.SerialBus.Default) \n
		Sets a value for the group sub index. Available, if method RsMxo.Sbus.Spmi.GsidEnable.set is set to ON. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: gs_id: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SPMI:GIDValue?')
		return Conversions.str_to_int(response)

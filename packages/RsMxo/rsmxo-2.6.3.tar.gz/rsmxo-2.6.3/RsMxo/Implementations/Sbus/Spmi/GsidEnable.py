from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class GsidEnableCls:
	"""GsidEnable commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("gsidEnable", core, parent)

	def set(self, use_gsid: bool, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:SPMI:GSIDenable \n
		Snippet: driver.sbus.spmi.gsidEnable.set(use_gsid = False, serialBus = repcap.SerialBus.Default) \n
		Enables the use of the group sub ID (GSID) . You can set the GSID with method RsMxo.Sbus.Spmi.GidValue.set. \n
			:param use_gsid: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.bool_to_str(use_gsid)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:SPMI:GSIDenable {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> bool:
		"""SBUS<*>:SPMI:GSIDenable \n
		Snippet: value: bool = driver.sbus.spmi.gsidEnable.get(serialBus = repcap.SerialBus.Default) \n
		Enables the use of the group sub ID (GSID) . You can set the GSID with method RsMxo.Sbus.Spmi.GidValue.set. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: use_gsid: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:SPMI:GSIDenable?')
		return Conversions.str_to_bool(response)

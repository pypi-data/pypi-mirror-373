from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ShdiCls:
	"""Shdi commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("shdi", core, parent)

	def set(self, shw_dig_signs: bool, pwrBus=repcap.PwrBus.Default) -> None:
		"""PBUS<*>:DISPlay:SHDI \n
		Snippet: driver.pbus.display.shdi.set(shw_dig_signs = False, pwrBus = repcap.PwrBus.Default) \n
		If enabled, the selected digital channels are shown in the diagram. Each channel is displayed as a logic signal. \n
			:param shw_dig_signs: No help available
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
		"""
		param = Conversions.bool_to_str(shw_dig_signs)
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		self._core.io.write(f'PBUS{pwrBus_cmd_val}:DISPlay:SHDI {param}')

	def get(self, pwrBus=repcap.PwrBus.Default) -> bool:
		"""PBUS<*>:DISPlay:SHDI \n
		Snippet: value: bool = driver.pbus.display.shdi.get(pwrBus = repcap.PwrBus.Default) \n
		If enabled, the selected digital channels are shown in the diagram. Each channel is displayed as a logic signal. \n
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:return: shw_dig_signs: No help available"""
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		response = self._core.io.query_str(f'PBUS{pwrBus_cmd_val}:DISPlay:SHDI?')
		return Conversions.str_to_bool(response)

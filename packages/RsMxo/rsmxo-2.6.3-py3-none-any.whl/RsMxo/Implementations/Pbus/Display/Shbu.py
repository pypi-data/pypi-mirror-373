from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ShbuCls:
	"""Shbu commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("shbu", core, parent)

	def set(self, show_bus: bool, pwrBus=repcap.PwrBus.Default) -> None:
		"""PBUS<*>:DISPlay:SHBU \n
		Snippet: driver.pbus.display.shbu.set(show_bus = False, pwrBus = repcap.PwrBus.Default) \n
		If enabled, the resulting bus signal and bus values are displayed in the diagram. \n
			:param show_bus: No help available
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
		"""
		param = Conversions.bool_to_str(show_bus)
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		self._core.io.write(f'PBUS{pwrBus_cmd_val}:DISPlay:SHBU {param}')

	def get(self, pwrBus=repcap.PwrBus.Default) -> bool:
		"""PBUS<*>:DISPlay:SHBU \n
		Snippet: value: bool = driver.pbus.display.shbu.get(pwrBus = repcap.PwrBus.Default) \n
		If enabled, the resulting bus signal and bus values are displayed in the diagram. \n
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:return: show_bus: No help available"""
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		response = self._core.io.query_str(f'PBUS{pwrBus_cmd_val}:DISPlay:SHBU?')
		return Conversions.str_to_bool(response)

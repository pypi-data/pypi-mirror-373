from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StateCls:
	"""State commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("state", core, parent)

	def set(self, state: bool, pwrBus=repcap.PwrBus.Default) -> None:
		"""PBUS<*>:STATe \n
		Snippet: driver.pbus.state.set(state = False, pwrBus = repcap.PwrBus.Default) \n
		Enables the selected logic group. The corresponding signal icon appears on the signal bar. Dependencies: At least one
		digital channel must be enabled for the selected bus, otherwise the command does not work.
		The bus is enabled automatically if the first digital channel is enabled with method RsMxo.Pbus.Bit.State.set. \n
			:param state: No help available
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
		"""
		param = Conversions.bool_to_str(state)
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		self._core.io.write(f'PBUS{pwrBus_cmd_val}:STATe {param}')

	def get(self, pwrBus=repcap.PwrBus.Default) -> bool:
		"""PBUS<*>:STATe \n
		Snippet: value: bool = driver.pbus.state.get(pwrBus = repcap.PwrBus.Default) \n
		Enables the selected logic group. The corresponding signal icon appears on the signal bar. Dependencies: At least one
		digital channel must be enabled for the selected bus, otherwise the command does not work.
		The bus is enabled automatically if the first digital channel is enabled with method RsMxo.Pbus.Bit.State.set. \n
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:return: state: No help available"""
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		response = self._core.io.query_str(f'PBUS{pwrBus_cmd_val}:STATe?')
		return Conversions.str_to_bool(response)

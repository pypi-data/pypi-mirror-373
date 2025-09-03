from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StateCls:
	"""State commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("state", core, parent)

	def set(self, assigned: bool, pwrBus=repcap.PwrBus.Default, bit=repcap.Bit.Default) -> None:
		"""PBUS<*>:BIT<*>[:STATe] \n
		Snippet: driver.pbus.bit.state.set(assigned = False, pwrBus = repcap.PwrBus.Default, bit = repcap.Bit.Default) \n
		Enables the selected logic group. The corresponding signal icon appears on the signal bar. If another active bus already
		uses the selected digital channel, the instrument disables the other bus to avoid conflicts. \n
			:param assigned: No help available
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:param bit: optional repeated capability selector. Default value: Nr0 (settable in the interface 'Bit')
		"""
		param = Conversions.bool_to_str(assigned)
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		bit_cmd_val = self._cmd_group.get_repcap_cmd_value(bit, repcap.Bit)
		self._core.io.write(f'PBUS{pwrBus_cmd_val}:BIT{bit_cmd_val}:STATe {param}')

	def get(self, pwrBus=repcap.PwrBus.Default, bit=repcap.Bit.Default) -> bool:
		"""PBUS<*>:BIT<*>[:STATe] \n
		Snippet: value: bool = driver.pbus.bit.state.get(pwrBus = repcap.PwrBus.Default, bit = repcap.Bit.Default) \n
		Enables the selected logic group. The corresponding signal icon appears on the signal bar. If another active bus already
		uses the selected digital channel, the instrument disables the other bus to avoid conflicts. \n
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:param bit: optional repeated capability selector. Default value: Nr0 (settable in the interface 'Bit')
			:return: assigned: No help available"""
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		bit_cmd_val = self._cmd_group.get_repcap_cmd_value(bit, repcap.Bit)
		response = self._core.io.query_str(f'PBUS{pwrBus_cmd_val}:BIT{bit_cmd_val}:STATe?')
		return Conversions.str_to_bool(response)

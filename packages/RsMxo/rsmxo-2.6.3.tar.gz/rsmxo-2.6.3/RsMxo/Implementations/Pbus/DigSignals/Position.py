from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PositionCls:
	"""Position commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("position", core, parent)

	def set(self, dig_sign_rotational_pos: int, pwrBus=repcap.PwrBus.Default) -> None:
		"""PBUS<*>:DIGSignals:POSition \n
		Snippet: driver.pbus.digSignals.position.set(dig_sign_rotational_pos = 1, pwrBus = repcap.PwrBus.Default) \n
		Sets the vertical position of all active digital channels. \n
			:param dig_sign_rotational_pos: No help available
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
		"""
		param = Conversions.decimal_value_to_str(dig_sign_rotational_pos)
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		self._core.io.write(f'PBUS{pwrBus_cmd_val}:DIGSignals:POSition {param}')

	def get(self, pwrBus=repcap.PwrBus.Default) -> int:
		"""PBUS<*>:DIGSignals:POSition \n
		Snippet: value: int = driver.pbus.digSignals.position.get(pwrBus = repcap.PwrBus.Default) \n
		Sets the vertical position of all active digital channels. \n
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:return: dig_sign_rotational_pos: No help available"""
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		response = self._core.io.query_str(f'PBUS{pwrBus_cmd_val}:DIGSignals:POSition?')
		return Conversions.str_to_int(response)

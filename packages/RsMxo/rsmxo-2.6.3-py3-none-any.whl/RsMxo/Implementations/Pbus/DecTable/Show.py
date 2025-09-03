from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ShowCls:
	"""Show commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("show", core, parent)

	def set(self, shw_decode_tbl: bool, pwrBus=repcap.PwrBus.Default) -> None:
		"""PBUS<*>:DECTable:SHOW \n
		Snippet: driver.pbus.decTable.show.set(shw_decode_tbl = False, pwrBus = repcap.PwrBus.Default) \n
		If enabled, a result table is shown with decoded values and corresponding points in time of the bus signal. Each clock
		edge corresponds to one row in the table. The decode table is only available for clocked buses to check the data words. \n
			:param shw_decode_tbl: No help available
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
		"""
		param = Conversions.bool_to_str(shw_decode_tbl)
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		self._core.io.write(f'PBUS{pwrBus_cmd_val}:DECTable:SHOW {param}')

	def get(self, pwrBus=repcap.PwrBus.Default) -> bool:
		"""PBUS<*>:DECTable:SHOW \n
		Snippet: value: bool = driver.pbus.decTable.show.get(pwrBus = repcap.PwrBus.Default) \n
		If enabled, a result table is shown with decoded values and corresponding points in time of the bus signal. Each clock
		edge corresponds to one row in the table. The decode table is only available for clocked buses to check the data words. \n
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:return: shw_decode_tbl: No help available"""
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		response = self._core.io.query_str(f'PBUS{pwrBus_cmd_val}:DECTable:SHOW?')
		return Conversions.str_to_bool(response)

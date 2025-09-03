from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CountCls:
	"""Count commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("count", core, parent)

	def get(self, pwrBus=repcap.PwrBus.Default) -> int:
		"""PBUS<*>:DECTable:COUNt \n
		Snippet: value: int = driver.pbus.decTable.count.get(pwrBus = repcap.PwrBus.Default) \n
		Returns the number of rows in the decode table. Each clock edge corresponds to one row in the table. The decode table is
		only available for clocked buses. \n
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:return: count: Number of rows"""
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		response = self._core.io.query_str(f'PBUS{pwrBus_cmd_val}:DECTable:COUNt?')
		return Conversions.str_to_int(response)

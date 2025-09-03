from typing import List

from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DataCls:
	"""Data commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("data", core, parent)

	def get(self, pwrBus=repcap.PwrBus.Default) -> List[float]:
		"""PBUS<*>:DECTable:DATA \n
		Snippet: value: List[float] = driver.pbus.decTable.data.get(pwrBus = repcap.PwrBus.Default) \n
		Returns a list of decoded values and corresponding points in time from the decode table. Each data pair corresponds to
		one clock edge, which is one row in the table. The decode table is only available for clocked buses. \n
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:return: data: Comma-separated list of values"""
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		response = self._core.io.query_bin_or_ascii_float_list(f'PBUS{pwrBus_cmd_val}:DECTable:DATA?')
		return response

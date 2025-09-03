from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ResultCls:
	"""Result commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("result", core, parent)

	def get(self, voltmeter=repcap.Voltmeter.Default) -> float:
		"""METer:DVMeter<*>:DC:RESult \n
		Snippet: value: float = driver.meter.dvMeter.dc.result.get(voltmeter = repcap.Voltmeter.Default) \n
		Returns the result of the DC voltmeter measurement. \n
			:param voltmeter: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Meter')
			:return: results_dc: No help available"""
		voltmeter_cmd_val = self._cmd_group.get_repcap_cmd_value(voltmeter, repcap.Voltmeter)
		response = self._core.io.query_str(f'METer:DVMeter{voltmeter_cmd_val}:DC:RESult?')
		return Conversions.str_to_float(response)

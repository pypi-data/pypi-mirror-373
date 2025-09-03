from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EnableCls:
	"""Enable commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("enable", core, parent)

	def get(self, voltmeter=repcap.Voltmeter.Default) -> bool:
		"""METer:DVMeter<*>:ENABle \n
		Snippet: value: bool = driver.meter.dvMeter.enable.get(voltmeter = repcap.Voltmeter.Default) \n
		Queries the state of the voltmeter for the respective channel. \n
			:param voltmeter: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Meter')
			:return: state: No help available"""
		voltmeter_cmd_val = self._cmd_group.get_repcap_cmd_value(voltmeter, repcap.Voltmeter)
		response = self._core.io.query_str(f'METer:DVMeter{voltmeter_cmd_val}:ENABle?')
		return Conversions.str_to_bool(response)

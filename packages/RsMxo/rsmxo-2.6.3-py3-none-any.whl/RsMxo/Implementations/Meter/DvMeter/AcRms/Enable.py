from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EnableCls:
	"""Enable commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("enable", core, parent)

	def set(self, acrms_results_st: bool, voltmeter=repcap.Voltmeter.Default) -> None:
		"""METer:DVMeter<*>:ACRMs:ENABle \n
		Snippet: driver.meter.dvMeter.acRms.enable.set(acrms_results_st = False, voltmeter = repcap.Voltmeter.Default) \n
		Enables the AC RMS voltmeter measurement for the respective channel. \n
			:param acrms_results_st: No help available
			:param voltmeter: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Meter')
		"""
		param = Conversions.bool_to_str(acrms_results_st)
		voltmeter_cmd_val = self._cmd_group.get_repcap_cmd_value(voltmeter, repcap.Voltmeter)
		self._core.io.write(f'METer:DVMeter{voltmeter_cmd_val}:ACRMs:ENABle {param}')

	def get(self, voltmeter=repcap.Voltmeter.Default) -> bool:
		"""METer:DVMeter<*>:ACRMs:ENABle \n
		Snippet: value: bool = driver.meter.dvMeter.acRms.enable.get(voltmeter = repcap.Voltmeter.Default) \n
		Enables the AC RMS voltmeter measurement for the respective channel. \n
			:param voltmeter: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Meter')
			:return: acrms_results_st: No help available"""
		voltmeter_cmd_val = self._cmd_group.get_repcap_cmd_value(voltmeter, repcap.Voltmeter)
		response = self._core.io.query_str(f'METer:DVMeter{voltmeter_cmd_val}:ACRMs:ENABle?')
		return Conversions.str_to_bool(response)

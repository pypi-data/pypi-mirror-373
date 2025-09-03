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

	def get(self, digital=repcap.Digital.Default, probeDigital=repcap.ProbeDigital.Default) -> bool:
		"""DIGital<*>:PROBe<*>[:ENABle] \n
		Snippet: value: bool = driver.digital.probe.enable.get(digital = repcap.Digital.Default, probeDigital = repcap.ProbeDigital.Default) \n
		Enables one digital probe. \n
			:param digital: optional repeated capability selector. Default value: Nr0 (settable in the interface 'Digital')
			:param probeDigital: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: probe_connected: No help available"""
		digital_cmd_val = self._cmd_group.get_repcap_cmd_value(digital, repcap.Digital)
		probeDigital_cmd_val = self._cmd_group.get_repcap_cmd_value(probeDigital, repcap.ProbeDigital)
		response = self._core.io.query_str(f'DIGital{digital_cmd_val}:PROBe{probeDigital_cmd_val}:ENABle?')
		return Conversions.str_to_bool(response)

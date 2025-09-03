from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class UseAutoZeroCls:
	"""UseAutoZero commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("useAutoZero", core, parent)

	def set(self, use_auto_zero_offset: bool, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SETup:OFFSet:USEautozero \n
		Snippet: driver.probe.setup.offset.useAutoZero.set(use_auto_zero_offset = False, probe = repcap.Probe.Default) \n
		Corrects the zero error of the probe. The zero error is detected with method RsMxo.Probe.Setup.Offset.Azero.set. \n
			:param use_auto_zero_offset: No help available
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
		"""
		param = Conversions.bool_to_str(use_auto_zero_offset)
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SETup:OFFSet:USEautozero {param}')

	def get(self, probe=repcap.Probe.Default) -> bool:
		"""PROBe<*>:SETup:OFFSet:USEautozero \n
		Snippet: value: bool = driver.probe.setup.offset.useAutoZero.get(probe = repcap.Probe.Default) \n
		Corrects the zero error of the probe. The zero error is detected with method RsMxo.Probe.Setup.Offset.Azero.set. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: use_auto_zero_offset: No help available"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:OFFSet:USEautozero?')
		return Conversions.str_to_bool(response)

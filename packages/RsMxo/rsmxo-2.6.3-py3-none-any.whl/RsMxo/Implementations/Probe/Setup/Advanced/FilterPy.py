from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FilterPyCls:
	"""FilterPy commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("filterPy", core, parent)

	def set(self, bw_filter_st: bool, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SETup:ADVanced:FILTer \n
		Snippet: driver.probe.setup.advanced.filterPy.set(bw_filter_st = False, probe = repcap.Probe.Default) \n
		Activates the lowpass filter in the probe control box. The filter frequency depends on the probe type and is indicated on
		the probe control box. \n
			:param bw_filter_st: No help available
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
		"""
		param = Conversions.bool_to_str(bw_filter_st)
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SETup:ADVanced:FILTer {param}')

	def get(self, probe=repcap.Probe.Default) -> bool:
		"""PROBe<*>:SETup:ADVanced:FILTer \n
		Snippet: value: bool = driver.probe.setup.advanced.filterPy.get(probe = repcap.Probe.Default) \n
		Activates the lowpass filter in the probe control box. The filter frequency depends on the probe type and is indicated on
		the probe control box. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: bw_filter_st: No help available"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:ADVanced:FILTer?')
		return Conversions.str_to_bool(response)

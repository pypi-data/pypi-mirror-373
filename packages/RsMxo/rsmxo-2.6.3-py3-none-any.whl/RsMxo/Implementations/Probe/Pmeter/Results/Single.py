from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SingleCls:
	"""Single commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("single", core, parent)

	def get(self, probe=repcap.Probe.Default) -> float:
		"""PROBe<*>:PMETer:RESults:SINGle \n
		Snippet: value: float = driver.probe.pmeter.results.single.get(probe = repcap.Probe.Default) \n
		Returns the R&S ProbeMeter measurement result of single-ended active Rohde & Schwarz probes, the voltage measured between
		the probe tip and the ground. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: sg_end_meas_res: No help available"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:PMETer:RESults:SINGle?')
		return Conversions.str_to_float(response)

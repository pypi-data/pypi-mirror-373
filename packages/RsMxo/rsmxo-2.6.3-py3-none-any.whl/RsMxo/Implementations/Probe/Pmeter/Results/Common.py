from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CommonCls:
	"""Common commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("common", core, parent)

	def get(self, probe=repcap.Probe.Default) -> float:
		"""PROBe<*>:PMETer:RESults:COMMon \n
		Snippet: value: float = driver.probe.pmeter.results.common.get(probe = repcap.Probe.Default) \n
		Returns the R&S ProbeMeter measurement result of differential active R&S probes: the common mode voltage, which is the
		mean voltage between the signal sockets and the ground socket. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: common_md_meas_res: No help available"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:PMETer:RESults:COMMon?')
		return Conversions.str_to_float(response)

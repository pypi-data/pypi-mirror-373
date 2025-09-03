from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SkeStateCls:
	"""SkeState commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("skeState", core, parent)

	def set(self, prb_deskew_st: bool, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SKEState \n
		Snippet: driver.probe.skeState.set(prb_deskew_st = False, probe = repcap.Probe.Default) \n
		No command help available \n
			:param prb_deskew_st: No help available
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
		"""
		param = Conversions.bool_to_str(prb_deskew_st)
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SKEState {param}')

	def get(self, probe=repcap.Probe.Default) -> bool:
		"""PROBe<*>:SKEState \n
		Snippet: value: bool = driver.probe.skeState.get(probe = repcap.Probe.Default) \n
		No command help available \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: prb_deskew_st: No help available"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SKEState?')
		return Conversions.str_to_bool(response)

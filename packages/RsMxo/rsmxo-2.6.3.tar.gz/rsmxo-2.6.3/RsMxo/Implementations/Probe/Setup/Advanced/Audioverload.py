from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AudioverloadCls:
	"""Audioverload commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("audioverload", core, parent)

	def set(self, audib_ovrrg: bool, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SETup:ADVanced:AUDioverload \n
		Snippet: driver.probe.setup.advanced.audioverload.set(audib_ovrrg = False, probe = repcap.Probe.Default) \n
		Activates the acoustic overrange warning in the probe control box. The command is relevant for R&S RT-ZHD probes. \n
			:param audib_ovrrg: No help available
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
		"""
		param = Conversions.bool_to_str(audib_ovrrg)
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SETup:ADVanced:AUDioverload {param}')

	def get(self, probe=repcap.Probe.Default) -> bool:
		"""PROBe<*>:SETup:ADVanced:AUDioverload \n
		Snippet: value: bool = driver.probe.setup.advanced.audioverload.get(probe = repcap.Probe.Default) \n
		Activates the acoustic overrange warning in the probe control box. The command is relevant for R&S RT-ZHD probes. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: audib_ovrrg: No help available"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:ADVanced:AUDioverload?')
		return Conversions.str_to_bool(response)

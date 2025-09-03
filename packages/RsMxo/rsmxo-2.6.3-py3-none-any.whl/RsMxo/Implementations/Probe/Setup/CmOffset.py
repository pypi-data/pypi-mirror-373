from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CmOffsetCls:
	"""CmOffset commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("cmOffset", core, parent)

	def set(self, cm_offset: float, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SETup:CMOFfset \n
		Snippet: driver.probe.setup.cmOffset.set(cm_offset = 1.0, probe = repcap.Probe.Default) \n
		Sets the common-mode offset to compensate for a common DC voltage that is applied to both input sockets (referenced to
		the ground socket) . The setting is available for Rohde & Schwarz differential probes and for modular probes in CM
		measurement mode. \n
			:param cm_offset: No help available
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
		"""
		param = Conversions.decimal_value_to_str(cm_offset)
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SETup:CMOFfset {param}')

	def get(self, probe=repcap.Probe.Default) -> float:
		"""PROBe<*>:SETup:CMOFfset \n
		Snippet: value: float = driver.probe.setup.cmOffset.get(probe = repcap.Probe.Default) \n
		Sets the common-mode offset to compensate for a common DC voltage that is applied to both input sockets (referenced to
		the ground socket) . The setting is available for Rohde & Schwarz differential probes and for modular probes in CM
		measurement mode. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: cm_offset: No help available"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:CMOFfset?')
		return Conversions.str_to_float(response)

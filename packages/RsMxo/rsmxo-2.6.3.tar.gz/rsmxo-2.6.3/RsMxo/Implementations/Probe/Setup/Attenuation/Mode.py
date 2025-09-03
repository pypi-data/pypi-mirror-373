from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ModeCls:
	"""Mode commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mode", core, parent)

	def set(self, prb_att_md: enums.AutoManualMode, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SETup:ATTenuation:MODE \n
		Snippet: driver.probe.setup.attenuation.mode.set(prb_att_md = enums.AutoManualMode.AUTO, probe = repcap.Probe.Default) \n
		Set the mode to MANual if the instrument does not detect the passive probe. \n
			:param prb_att_md: No help available
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
		"""
		param = Conversions.enum_scalar_to_str(prb_att_md, enums.AutoManualMode)
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SETup:ATTenuation:MODE {param}')

	# noinspection PyTypeChecker
	def get(self, probe=repcap.Probe.Default) -> enums.AutoManualMode:
		"""PROBe<*>:SETup:ATTenuation:MODE \n
		Snippet: value: enums.AutoManualMode = driver.probe.setup.attenuation.mode.get(probe = repcap.Probe.Default) \n
		Set the mode to MANual if the instrument does not detect the passive probe. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: prb_att_md: No help available"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:ATTenuation:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.AutoManualMode)

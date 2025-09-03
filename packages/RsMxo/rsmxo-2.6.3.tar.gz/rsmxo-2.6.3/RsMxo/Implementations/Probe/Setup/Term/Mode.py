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

	def set(self, mode: enums.AutoManualMode, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SETup:TERM:MODE \n
		Snippet: driver.probe.setup.term.mode.set(mode = enums.AutoManualMode.AUTO, probe = repcap.Probe.Default) \n
		Selects the voltage that is used for termination. \n
			:param mode: AUTO: the instrument uses the measured common mode voltage for termination. MANual: enter the voltage to be used for termination with method RsMxo.Probe.Setup.Term.Adjust.set.
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
		"""
		param = Conversions.enum_scalar_to_str(mode, enums.AutoManualMode)
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SETup:TERM:MODE {param}')

	# noinspection PyTypeChecker
	def get(self, probe=repcap.Probe.Default) -> enums.AutoManualMode:
		"""PROBe<*>:SETup:TERM:MODE \n
		Snippet: value: enums.AutoManualMode = driver.probe.setup.term.mode.get(probe = repcap.Probe.Default) \n
		Selects the voltage that is used for termination. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: mode: AUTO: the instrument uses the measured common mode voltage for termination. MANual: enter the voltage to be used for termination with method RsMxo.Probe.Setup.Term.Adjust.set."""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:TERM:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.AutoManualMode)

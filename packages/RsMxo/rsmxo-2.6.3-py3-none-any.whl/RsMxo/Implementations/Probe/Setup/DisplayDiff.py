from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DisplayDiffCls:
	"""DisplayDiff commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("displayDiff", core, parent)

	def set(self, display_diff: enums.DisplayDiff, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SETup:DISPlaydiff \n
		Snippet: driver.probe.setup.displayDiff.set(display_diff = enums.DisplayDiff.DIFFerential, probe = repcap.Probe.Default) \n
		Selects the voltage to be measured by the R&S ProbeMeter of differential active probes: \n
			:param display_diff:
				- DIFFerential: Measures differential and common mode voltages
				- SINGleended: Measures the voltage between the positive/negative signal socket and the ground.
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')"""
		param = Conversions.enum_scalar_to_str(display_diff, enums.DisplayDiff)
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SETup:DISPlaydiff {param}')

	# noinspection PyTypeChecker
	def get(self, probe=repcap.Probe.Default) -> enums.DisplayDiff:
		"""PROBe<*>:SETup:DISPlaydiff \n
		Snippet: value: enums.DisplayDiff = driver.probe.setup.displayDiff.get(probe = repcap.Probe.Default) \n
		Selects the voltage to be measured by the R&S ProbeMeter of differential active probes: \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: display_diff:
				- DIFFerential: Measures differential and common mode voltages
				- SINGleended: Measures the voltage between the positive/negative signal socket and the ground."""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:DISPlaydiff?')
		return Conversions.str_to_scalar_enum(response, enums.DisplayDiff)

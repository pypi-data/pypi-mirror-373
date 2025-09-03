from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PrModeCls:
	"""PrMode commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("prMode", core, parent)

	def set(self, prb_meas_md: enums.ProbeMeasMode, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SETup:PRMode \n
		Snippet: driver.probe.setup.prMode.set(prb_meas_md = enums.ProbeMeasMode.CMODe, probe = repcap.Probe.Default) \n
		Sets the measurement mode of modular probes. \n
			:param prb_meas_md:
				- DMODe: Differential mode input voltage (Vdm) , the voltage between the positive and negative input terminal.
				- CMODe: Common mode input voltage (Vcm) , the mean voltage between the positive and negative input terminal vs. ground.
				- PMODe: Positive single-ended input voltage (Vp) . the voltage between the positive input terminal and ground.
				- NMODe: Negative single-ended input voltage (VN) . the voltage between the negative input terminal and ground.
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')"""
		param = Conversions.enum_scalar_to_str(prb_meas_md, enums.ProbeMeasMode)
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SETup:PRMode {param}')

	# noinspection PyTypeChecker
	def get(self, probe=repcap.Probe.Default) -> enums.ProbeMeasMode:
		"""PROBe<*>:SETup:PRMode \n
		Snippet: value: enums.ProbeMeasMode = driver.probe.setup.prMode.get(probe = repcap.Probe.Default) \n
		Sets the measurement mode of modular probes. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: prb_meas_md:
				- DMODe: Differential mode input voltage (Vdm) , the voltage between the positive and negative input terminal.
				- CMODe: Common mode input voltage (Vcm) , the mean voltage between the positive and negative input terminal vs. ground.
				- PMODe: Positive single-ended input voltage (Vp) . the voltage between the positive input terminal and ground.
				- NMODe: Negative single-ended input voltage (VN) . the voltage between the negative input terminal and ground."""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:PRMode?')
		return Conversions.str_to_scalar_enum(response, enums.ProbeMeasMode)

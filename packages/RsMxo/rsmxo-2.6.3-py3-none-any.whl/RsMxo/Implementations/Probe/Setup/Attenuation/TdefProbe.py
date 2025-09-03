from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TdefProbeCls:
	"""TdefProbe commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("tdefProbe", core, parent)

	def set(self, tek_predef_prb: enums.TekPredefProbe, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SETup:ATTenuation:TDEFprobe \n
		Snippet: driver.probe.setup.attenuation.tdefProbe.set(tek_predef_prb = enums.TekPredefProbe.NONE, probe = repcap.Probe.Default) \n
		Selects the Tektronix probe that is connected to the R&S RT-Z2T adapter. \n
			:param tek_predef_prb: No help available
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
		"""
		param = Conversions.enum_scalar_to_str(tek_predef_prb, enums.TekPredefProbe)
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SETup:ATTenuation:TDEFprobe {param}')

	# noinspection PyTypeChecker
	def get(self, probe=repcap.Probe.Default) -> enums.TekPredefProbe:
		"""PROBe<*>:SETup:ATTenuation:TDEFprobe \n
		Snippet: value: enums.TekPredefProbe = driver.probe.setup.attenuation.tdefProbe.get(probe = repcap.Probe.Default) \n
		Selects the Tektronix probe that is connected to the R&S RT-Z2T adapter. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: tek_predef_prb: No help available"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:ATTenuation:TDEFprobe?')
		return Conversions.str_to_scalar_enum(response, enums.TekPredefProbe)

from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class UnitCls:
	"""Unit commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("unit", core, parent)

	def set(self, prb_att_unt: enums.ProbeAttUnits, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SETup:ATTenuation:UNIT \n
		Snippet: driver.probe.setup.attenuation.unit.set(prb_att_unt = enums.ProbeAttUnits.A, probe = repcap.Probe.Default) \n
		Returns the unit of the connected probe if the probe is detected or predefined. For unknown probes, you can select the
		required unit. \n
			:param prb_att_unt: Voltage probe (V) , current probe (A) , power probe (W)
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
		"""
		param = Conversions.enum_scalar_to_str(prb_att_unt, enums.ProbeAttUnits)
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SETup:ATTenuation:UNIT {param}')

	# noinspection PyTypeChecker
	def get(self, probe=repcap.Probe.Default) -> enums.ProbeAttUnits:
		"""PROBe<*>:SETup:ATTenuation:UNIT \n
		Snippet: value: enums.ProbeAttUnits = driver.probe.setup.attenuation.unit.get(probe = repcap.Probe.Default) \n
		Returns the unit of the connected probe if the probe is detected or predefined. For unknown probes, you can select the
		required unit. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: prb_att_unt: No help available"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:ATTenuation:UNIT?')
		return Conversions.str_to_scalar_enum(response, enums.ProbeAttUnits)

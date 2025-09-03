from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RangeCls:
	"""Range commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("range", core, parent)

	def set(self, probe_range: enums.ProbeRange, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SETup:ADVanced:RANGe \n
		Snippet: driver.probe.setup.advanced.range.set(probe_range = enums.ProbeRange.AUTO, probe = repcap.Probe.Default) \n
		Sets the voltage range of an R&S RT-ZHD probe. \n
			:param probe_range:
				- AUTO: The voltage range is set with CHANnelch:SCALe.
				- MHIGh: Sets the higher voltage range of the connected probe. To query the value, use PROBech:SETup:ATTenuation[:AUTO]?.
				- MLOW: Sets the lower voltage range of the connected probe. To query the value, use PROBech:SETup:ATTenuation[:AUTO]?.
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')"""
		param = Conversions.enum_scalar_to_str(probe_range, enums.ProbeRange)
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SETup:ADVanced:RANGe {param}')

	# noinspection PyTypeChecker
	def get(self, probe=repcap.Probe.Default) -> enums.ProbeRange:
		"""PROBe<*>:SETup:ADVanced:RANGe \n
		Snippet: value: enums.ProbeRange = driver.probe.setup.advanced.range.get(probe = repcap.Probe.Default) \n
		Sets the voltage range of an R&S RT-ZHD probe. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: probe_range:
				- AUTO: The voltage range is set with CHANnelch:SCALe.
				- MHIGh: Sets the higher voltage range of the connected probe. To query the value, use PROBech:SETup:ATTenuation[:AUTO]?.
				- MLOW: Sets the lower voltage range of the connected probe. To query the value, use PROBech:SETup:ATTenuation[:AUTO]?."""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:ADVanced:RANGe?')
		return Conversions.str_to_scalar_enum(response, enums.ProbeRange)

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

	def set(self, select_unit: enums.Unit, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SETup:ADVanced:UNIT \n
		Snippet: driver.probe.setup.advanced.unit.set(select_unit = enums.Unit.A, probe = repcap.Probe.Default) \n
		Sets the unit of the R&S RT-ZISO signal. \n
			:param select_unit: No help available
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
		"""
		param = Conversions.enum_scalar_to_str(select_unit, enums.Unit)
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SETup:ADVanced:UNIT {param}')

	# noinspection PyTypeChecker
	def get(self, probe=repcap.Probe.Default) -> enums.Unit:
		"""PROBe<*>:SETup:ADVanced:UNIT \n
		Snippet: value: enums.Unit = driver.probe.setup.advanced.unit.get(probe = repcap.Probe.Default) \n
		Sets the unit of the R&S RT-ZISO signal. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: select_unit: No help available"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:ADVanced:UNIT?')
		return Conversions.str_to_scalar_enum(response, enums.Unit)

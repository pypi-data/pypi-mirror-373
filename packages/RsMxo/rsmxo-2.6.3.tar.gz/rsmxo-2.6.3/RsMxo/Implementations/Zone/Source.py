from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SourceCls:
	"""Source commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("source", core, parent)

	def set(self, source: enums.Source, zone=repcap.Zone.Default) -> None:
		"""ZONE<*>:SOURce \n
		Snippet: driver.zone.source.set(source = enums.Source.C1, zone = repcap.Zone.Default) \n
		Sets the source of the zone trigger. \n
			:param source: No help available
			:param zone: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zone')
		"""
		param = Conversions.enum_scalar_to_str(source, enums.Source)
		zone_cmd_val = self._cmd_group.get_repcap_cmd_value(zone, repcap.Zone)
		self._core.io.write(f'ZONE{zone_cmd_val}:SOURce {param}')

	# noinspection PyTypeChecker
	def get(self, zone=repcap.Zone.Default) -> enums.Source:
		"""ZONE<*>:SOURce \n
		Snippet: value: enums.Source = driver.zone.source.get(zone = repcap.Zone.Default) \n
		Sets the source of the zone trigger. \n
			:param zone: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zone')
			:return: source: No help available"""
		zone_cmd_val = self._cmd_group.get_repcap_cmd_value(zone, repcap.Zone)
		response = self._core.io.query_str(f'ZONE{zone_cmd_val}:SOURce?')
		return Conversions.str_to_scalar_enum(response, enums.Source)

from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AcombinationCls:
	"""Acombination commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("acombination", core, parent)

	def set(self, area_combination: enums.AreaCombination, zone=repcap.Zone.Default) -> None:
		"""ZONE<*>:ACOMbination \n
		Snippet: driver.zone.acombination.set(area_combination = enums.AreaCombination.ABS, zone = repcap.Zone.Default) \n
		Sets the logic combination that applies to all areas in the indicated zone. \n
			:param area_combination: No help available
			:param zone: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zone')
		"""
		param = Conversions.enum_scalar_to_str(area_combination, enums.AreaCombination)
		zone_cmd_val = self._cmd_group.get_repcap_cmd_value(zone, repcap.Zone)
		self._core.io.write(f'ZONE{zone_cmd_val}:ACOMbination {param}')

	# noinspection PyTypeChecker
	def get(self, zone=repcap.Zone.Default) -> enums.AreaCombination:
		"""ZONE<*>:ACOMbination \n
		Snippet: value: enums.AreaCombination = driver.zone.acombination.get(zone = repcap.Zone.Default) \n
		Sets the logic combination that applies to all areas in the indicated zone. \n
			:param zone: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zone')
			:return: area_combination: No help available"""
		zone_cmd_val = self._cmd_group.get_repcap_cmd_value(zone, repcap.Zone)
		response = self._core.io.query_str(f'ZONE{zone_cmd_val}:ACOMbination?')
		return Conversions.str_to_scalar_enum(response, enums.AreaCombination)

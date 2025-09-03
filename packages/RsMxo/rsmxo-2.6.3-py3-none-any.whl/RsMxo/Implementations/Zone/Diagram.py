from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DiagramCls:
	"""Diagram commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("diagram", core, parent)

	def set(self, sign_diag_key: str, zone=repcap.Zone.Default) -> None:
		"""ZONE<*>:DIAGram \n
		Snippet: driver.zone.diagram.set(sign_diag_key = 'abc', zone = repcap.Zone.Default) \n
		Selects the diagram on which the zone trigger is applied, for example layoutset1 diagram1 (L1_D1) . For more information
		about the SmartGrid definition, see 'SmartGrid'. \n
			:param sign_diag_key: String that indicates the layout set and the diagram, e.g. 'L1_D1'.
			:param zone: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zone')
		"""
		param = Conversions.value_to_quoted_str(sign_diag_key)
		zone_cmd_val = self._cmd_group.get_repcap_cmd_value(zone, repcap.Zone)
		self._core.io.write(f'ZONE{zone_cmd_val}:DIAGram {param}')

	def get(self, zone=repcap.Zone.Default) -> str:
		"""ZONE<*>:DIAGram \n
		Snippet: value: str = driver.zone.diagram.get(zone = repcap.Zone.Default) \n
		Selects the diagram on which the zone trigger is applied, for example layoutset1 diagram1 (L1_D1) . For more information
		about the SmartGrid definition, see 'SmartGrid'. \n
			:param zone: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Zone')
			:return: sign_diag_key: String that indicates the layout set and the diagram, e.g. 'L1_D1'."""
		zone_cmd_val = self._cmd_group.get_repcap_cmd_value(zone, repcap.Zone)
		response = self._core.io.query_str(f'ZONE{zone_cmd_val}:DIAGram?')
		return trim_str_response(response)

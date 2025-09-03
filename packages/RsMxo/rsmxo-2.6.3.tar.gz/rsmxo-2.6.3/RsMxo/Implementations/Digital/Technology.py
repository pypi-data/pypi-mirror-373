from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TechnologyCls:
	"""Technology commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("technology", core, parent)

	def set(self, technology: enums.Technology, digital=repcap.Digital.Default) -> None:
		"""DIGital<*>:TECHnology \n
		Snippet: driver.digital.technology.set(technology = enums.Technology.CUSTom, digital = repcap.Digital.Default) \n
		Selects the threshold voltage for various types of integrated circuits and applies it to all digital channels.
		The setting affects only the settings of the first MSO bus (Logic1) . You can set the technology value for all buses with
		method RsMxo.Pbus.Technology.set. \n
			:param technology: See method RsMxo.Pbus.Technology.set.
			:param digital: optional repeated capability selector. Default value: Nr0 (settable in the interface 'Digital')
		"""
		param = Conversions.enum_scalar_to_str(technology, enums.Technology)
		digital_cmd_val = self._cmd_group.get_repcap_cmd_value(digital, repcap.Digital)
		self._core.io.write(f'DIGital{digital_cmd_val}:TECHnology {param}')

	# noinspection PyTypeChecker
	def get(self, digital=repcap.Digital.Default) -> enums.Technology:
		"""DIGital<*>:TECHnology \n
		Snippet: value: enums.Technology = driver.digital.technology.get(digital = repcap.Digital.Default) \n
		Selects the threshold voltage for various types of integrated circuits and applies it to all digital channels.
		The setting affects only the settings of the first MSO bus (Logic1) . You can set the technology value for all buses with
		method RsMxo.Pbus.Technology.set. \n
			:param digital: optional repeated capability selector. Default value: Nr0 (settable in the interface 'Digital')
			:return: technology: See method RsMxo.Pbus.Technology.set."""
		digital_cmd_val = self._cmd_group.get_repcap_cmd_value(digital, repcap.Digital)
		response = self._core.io.query_str(f'DIGital{digital_cmd_val}:TECHnology?')
		return Conversions.str_to_scalar_enum(response, enums.Technology)

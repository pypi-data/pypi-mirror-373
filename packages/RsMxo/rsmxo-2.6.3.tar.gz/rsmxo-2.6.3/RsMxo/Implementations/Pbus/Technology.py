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

	def set(self, technology: enums.Technology, pwrBus=repcap.PwrBus.Default) -> None:
		"""PBUS<*>:TECHnology \n
		Snippet: driver.pbus.technology.set(technology = enums.Technology.CUSTom, pwrBus = repcap.PwrBus.Default) \n
		Selects the threshold voltage for various types of integrated circuits and applies it to all digital channels. \n
			:param technology: V15: TTL V25: CMOS 5.0 V V165: CMOS 3.3 V V125: CMOS 2.5 V V09: CMOS 1.85 V VM13: ECL, -1.3 V V38: PECL V20: LVPECL V0: Ground MANual: Set a user-defined threshold value with method RsMxo.Digital.Threshold.set.
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
		"""
		param = Conversions.enum_scalar_to_str(technology, enums.Technology)
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		self._core.io.write(f'PBUS{pwrBus_cmd_val}:TECHnology {param}')

	# noinspection PyTypeChecker
	def get(self, pwrBus=repcap.PwrBus.Default) -> enums.Technology:
		"""PBUS<*>:TECHnology \n
		Snippet: value: enums.Technology = driver.pbus.technology.get(pwrBus = repcap.PwrBus.Default) \n
		Selects the threshold voltage for various types of integrated circuits and applies it to all digital channels. \n
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:return: technology: V15: TTL V25: CMOS 5.0 V V165: CMOS 3.3 V V125: CMOS 2.5 V V09: CMOS 1.85 V VM13: ECL, -1.3 V V38: PECL V20: LVPECL V0: Ground MANual: Set a user-defined threshold value with method RsMxo.Digital.Threshold.set."""
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		response = self._core.io.query_str(f'PBUS{pwrBus_cmd_val}:TECHnology?')
		return Conversions.str_to_scalar_enum(response, enums.Technology)

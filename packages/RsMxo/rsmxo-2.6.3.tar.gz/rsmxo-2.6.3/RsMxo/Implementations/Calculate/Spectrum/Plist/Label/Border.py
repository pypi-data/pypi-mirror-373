from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import enums
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class BorderCls:
	"""Border commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("border", core, parent)

	def set(self, label_border: enums.LabelBorder, spectrum=repcap.Spectrum.Default) -> None:
		"""CALCulate:SPECtrum<*>:PLISt:LABel:BORDer \n
		Snippet: driver.calculate.spectrum.plist.label.border.set(label_border = enums.LabelBorder.FULL, spectrum = repcap.Spectrum.Default) \n
		Defines the layout of the labels, full border or none. \n
			:param label_border: FULL: Full border
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
		"""
		param = Conversions.enum_scalar_to_str(label_border, enums.LabelBorder)
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		self._core.io.write(f'CALCulate:SPECtrum{spectrum_cmd_val}:PLISt:LABel:BORDer {param}')

	# noinspection PyTypeChecker
	def get(self, spectrum=repcap.Spectrum.Default) -> enums.LabelBorder:
		"""CALCulate:SPECtrum<*>:PLISt:LABel:BORDer \n
		Snippet: value: enums.LabelBorder = driver.calculate.spectrum.plist.label.border.get(spectrum = repcap.Spectrum.Default) \n
		Defines the layout of the labels, full border or none. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: label_border: FULL: Full border"""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		response = self._core.io.query_str(f'CALCulate:SPECtrum{spectrum_cmd_val}:PLISt:LABel:BORDer?')
		return Conversions.str_to_scalar_enum(response, enums.LabelBorder)

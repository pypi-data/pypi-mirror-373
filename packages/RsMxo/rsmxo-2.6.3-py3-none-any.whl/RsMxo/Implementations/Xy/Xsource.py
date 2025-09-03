from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class XsourceCls:
	"""Xsource commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("xsource", core, parent)

	def set(self, xsource: enums.Source, xyAxis=repcap.XyAxis.Default) -> None:
		"""XY<*>:XSOurce \n
		Snippet: driver.xy.xsource.set(xsource = enums.Source.C1, xyAxis = repcap.XyAxis.Default) \n
		Defines the signal source that supplies the x-values of the XY-diagram. \n
			:param xsource: No help available
			:param xyAxis: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Xy')
		"""
		param = Conversions.enum_scalar_to_str(xsource, enums.Source)
		xyAxis_cmd_val = self._cmd_group.get_repcap_cmd_value(xyAxis, repcap.XyAxis)
		self._core.io.write(f'XY{xyAxis_cmd_val}:XSOurce {param}')

	# noinspection PyTypeChecker
	def get(self, xyAxis=repcap.XyAxis.Default) -> enums.Source:
		"""XY<*>:XSOurce \n
		Snippet: value: enums.Source = driver.xy.xsource.get(xyAxis = repcap.XyAxis.Default) \n
		Defines the signal source that supplies the x-values of the XY-diagram. \n
			:param xyAxis: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Xy')
			:return: xsource: No help available"""
		xyAxis_cmd_val = self._cmd_group.get_repcap_cmd_value(xyAxis, repcap.XyAxis)
		response = self._core.io.query_str(f'XY{xyAxis_cmd_val}:XSOurce?')
		return Conversions.str_to_scalar_enum(response, enums.Source)

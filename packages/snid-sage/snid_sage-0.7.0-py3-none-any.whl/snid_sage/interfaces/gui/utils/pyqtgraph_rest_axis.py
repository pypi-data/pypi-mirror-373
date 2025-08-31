"""
PyQtGraph Rest Wavelength Axis
==============================

Provides a top axis that displays Rest Wavelength (Å) labels while the plot's
X axis remains in observed wavelength units. The rest labels are computed as
lambda_rest = lambda_observed / (1 + z).

This axis is linked to the same ViewBox as the plot, so it updates on zoom/pan.
"""

from typing import List

try:
	import pyqtgraph as pg  # type: ignore
except Exception:  # pragma: no cover
	pg = None  # type: ignore


class RestWavelengthAxisItem(pg.AxisItem):  # type: ignore[misc]
	"""AxisItem that formats tick labels as rest wavelengths.

	Set redshift via set_redshift(). Attach to a PlotItem as the 'top' axis and
	link it to the PlotItem's ViewBox to keep ticks aligned with observed values.
	"""

	def __init__(self, orientation: str = 'top', *, units_label: str = 'Rest Wavelength (Å)') -> None:
		super().__init__(orientation=orientation)
		self._z: float = 0.0
		self._units_label: str = units_label
		self.setLabel(self._units_label)
		# Hide tick marks; keep only numeric labels
		try:
			self.setStyle(tickLength=0)
		except Exception:
			pass

	def set_redshift(self, z: float) -> None:
		"""Update the redshift used for rest-wavelength conversion and refresh labels."""
		try:
			z_val = float(z or 0.0)
		except Exception:
			z_val = 0.0
		self._z = max(0.0, z_val)
		# Invalidate cached picture and update
		self.picture = None
		self.update()

	def tickStrings(self, values: List[float], scale: float, spacing: float) -> List[str]:  # type: ignore[override]
		# Convert observed tick values to rest wavelength
		denom = 1.0 + (self._z if self._z is not None else 0.0)
		if denom <= 0:
			denom = 1.0
		rest_vals = [v / denom for v in values]
		# Choose precision based on spacing for clean labels
		try:
			if spacing >= 1000:
				fmt = "{:.0f}"
			elif spacing >= 100:
				fmt = "{:.0f}"
			elif spacing >= 10:
				fmt = "{:.1f}"
			else:
				fmt = "{:.2f}"
		except Exception:
			fmt = "{:.1f}"
		return [fmt.format(rv) for rv in rest_vals]

	def tickValues(self, minVal, maxVal, size):  # type: ignore[override]
		"""Return only major tick values to avoid drawing minor (small) ticks on the top axis.

		This filters the levels provided by the base class to keep only the coarsest
		(major) tick level, removing minor tick levels (the short little ticks).
		"""
		try:
			levels = super().tickValues(minVal, maxVal, size)
			if isinstance(levels, list) and len(levels) > 0:
				# Keep major and medium levels to increase label density, omit minor
				if len(levels) >= 2:
					return [levels[0], levels[1]]
				return [levels[0]]
			return levels
		except Exception:
			# Fallback to base behavior on any error
			return pg.AxisItem.tickValues(self, minVal, maxVal, size)



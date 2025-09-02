#!/usr/bin/env python3

#---------------------------------
# Author: Ankit Anand
# Date: 26/08/25
# Email: ankit0.anand0@gmail.com
#---------------------------------

from pathlib import Path
import matplotlib as mpl
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Rectangle
import numpy as np
import fnmatch

#===== Loading Devanagari font ========
def _load_devanagari_font():
	"""
	Load devanagari font as it works for both English and Hindi.
	"""
	
	# Path to your bundled font
	font_path = Path(__file__).resolve().parents[1] / "fonts" / "NotoSansDevanagari-Regular.ttf"
	
	# Register the font with matplotlib
	fm.fontManager.addfont(str(font_path))
	
	# Get the font family name from the file
	hindi_font = fm.FontProperties(fname=str(font_path))
	
	# Set as default rcParam
	mpl.rcParams['font.family'] = hindi_font.get_name()
	
_load_devanagari_font()
#==============

class Fig:
	"""
	A utility class that provides easy-to-use API for 
	plotting 1D/2D signals along with clean representations 
	of annotations, events.
	"""
	
	def __init__(self, arrangement="asm", xlim=None):
		
		self._xlim = xlim
		self._curr_row_idx = 1 # Starting from 1 because row 0 is reserved for reference subplot
		self._curr_color_idx = 0 # So that we have different color across all the subplots to avoid legend confusion
		
		# Subplot setup
		self._fig, self._axs = self._generate_subplots(arrangement) # This will fill in the all the above variables
		
		
	def _get_curr_row(self):
		"""
		Get the active row where you can add
		either annotations or events.
		"""
		curr_row = self._axs[self._curr_row_idx]
		self._curr_row_idx += 1
		
		return curr_row
	
	def _get_new_color(self):
		"""
		Get a new color for different lines.
		"""
		colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
		self._curr_color_idx += 1
		
		return colors[self._curr_color_idx]
	
	def _calculate_extent(self, x, y, o):
		"""
		
		Parameters
		----------
		o: str
			- Origin
		"""
		# Handle spacing safely
		if len(x) > 1:
			dx = x[1] - x[0]
		else:
			dx = 1  # Default spacing for single value
		if len(y) > 1:
			dy = y[1] - y[0]
		else:
			dy = 1  # Default spacing for single value
			
		if o == "lower":
			return  [x[0] - dx / 2, x[-1] + dx / 2, y[0] - dy / 2, y[-1] + dy / 2]
		else:
			return [x[0] - dx / 2, x[-1] + dx / 2, y[-1] + dy / 2, y[0] - dy / 2]
	
	
	def _generate_subplots(self, arrangement):
		"""
		Generate subplots based on the configuration.
		"""
		
		xlim = self._xlim
		
		n_aux_sp = arrangement.count("a")
		n_signal_sp = arrangement.count("s")
		n_matrix_sp = arrangement.count("m")
		n_sp = 1 + n_aux_sp + n_signal_sp + n_matrix_sp # +1 is for the first reference subplot
		
		# Decide heights of different subplots type
		height = {}
		height["r"] = 0.0 # Reference height
		height["a"] = 0.4 # Aux height
		height["s"] = 2.0 # Signal height
		height["m"] = 4.0 # Matrix height
		cbar_width = 0.01
		
		arrangement = "r" + arrangement # "r" is to include the reference
		
		# Calculate height ratios list based on the arrangement
		for char in arrangement:
			height_ratios = [height[char] for char in arrangement]
			
		# Calculate total fig height
		fig_height = height["r"] + (n_aux_sp * height["a"]) + (n_signal_sp * height["s"]) + (n_matrix_sp * height["m"])
		
		# Create figure and axs
		fig, axs = plt.subplots(n_sp, 2, figsize=(16, fig_height), height_ratios=height_ratios, width_ratios=[1, cbar_width])
		
		for i, char in enumerate(arrangement): # For each of the subplots, we modify the layout accordingly
			if char == "r":
				axs[i, 0].axis("off")
				axs[i, 1].axis("off")
			elif char == "a": # Remove ticks and labels from all the aux subplots
				axs[i, 0].tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
				axs[i, 0].grid(True, linestyle=':', linewidth=0.7, color='gray', alpha=0.7)
				axs[i, 1].axis("off")
			elif char == "s":
				axs[i, 0].tick_params(bottom=False, labelbottom=False)
				axs[i, 0].grid(True, linestyle=':', linewidth=0.7, color='gray', alpha=0.7)
				axs[i, 1].axis("off")
			elif char == "m":
				axs[i, 0].grid(True, linestyle=':', linewidth=0.7, color='gray', alpha=0.7)
				axs[i, 0].tick_params(bottom=False, labelbottom=False)
				
			axs[i, 0].sharex(axs[0, 0])
		
		axs[-1, 0].tick_params(bottom=True, labelbottom=True)
		
		# xlim should be applied on reference subplot, rest all subplots will automatically adjust
		if xlim is not None:
			axs[0, 0].set_xlim(xlim)
			
		fig.subplots_adjust(hspace=0.2, wspace=0.05)
		
		return fig, axs
	
	def add_signal(self, y, x=None, c=None, ls=None, lw=None, m=None, ms=3, label=None, ylabel=None, ylim=None, ax=None):
		"""
		Add signal to the figure.
			
		Parameters
		----------
		y: np.ndarray
			- Signal y values.
		x: np.ndarray | None
			- Signal x values.
			- Default: None (indices will be used)
		c: str
			- Color of the line.
			- Default: None
		ls: str
			- Linestyle
			- Default: None
		lw: Number
			- Linewidth
			- Default: None
		m: str
			- Marker
			- Default: None
		ms: number
			- Markersize
			- Default: 3
		label: str
			- Label for the plot.
			- Legend will use this.
			- Default: None
		ylabel: str
			- y-label for the plot.
			- Default: None
		ylim: tuple
			- y-lim for the plot.
			- Default: None
		ax: int
			- Which specific axis to plot (1, 2, 3, ...)
			- None

		Returns
		-------
		None
		"""
		
		curr_row = self._get_curr_row() if ax is None else self._axs[ax]
		
		if x is None: x = np.arange(y.size)
		
		if c is None: c = self._get_new_color()
		
		curr_row[0].plot(x, y, color=c, linestyle=ls, linewidth=lw, marker=m, markersize=ms, label=label)
		
		if ylabel is not None: curr_row[0].set_ylabel(ylabel)
		
		if ylim is not None: curr_row[0].set_ylim(ylim)
		
	def add_matrix(self, M, y=None, x=None, c="gray_r", o="upper", label=None, ylabel=None, ylim=None, cbar=True, ax=None):
		"""
		Add matrix to the figure.
			
		Parameters
		----------
		M: np.ndarray
			- Matrix (2D) array
		y: np.ndarray | None
			- y axis values.
		x: np.ndarray | None (indices will be used)
			- x axis values.
			- Default: None (indices will be used)
		c: str
			- cmap for the matrix.
			- Default: None
		o: str
			- origin
			- Default: "lower"
		label: str
			- Label for the plot.
			- Legend will use this.
			- Default: None
		ylabel: str
			- y-label for the plot.
			- Default: None
		ylim: tuple
			- y-lim for the plot.
			- Default: None
		cbar: bool
			- Show colorbar
			- Default: True
		ax: int
			- Which specific axis to plot (1, 2, 3, ...)
			- None
		
		Returns
		-------
		None
		"""
		if x is None: x = np.arange(M.shape[1])
		if y is None: y = np.arange(M.shape[0])
		
		curr_row = self._get_curr_row() if ax is None else self._axs[ax]
		
		extent = self._calculate_extent(x, y, o)
		
		im = curr_row[0].imshow(M, aspect="auto", origin=o, cmap=c, extent=extent)
		
		if ylabel is not None: curr_row[0].set_ylabel(ylabel)
		
		if ylim is not None:
			if o == "lower":
				curr_row[0].set_ylim(ylim)
			elif o == "upper":
				curr_row[0].set_ylim(ylim[::-1])
		
		if cbar is True:
			cbar = plt.colorbar(im, cax=curr_row[1])
			if label is not None:
				cbar.set_label(label, labelpad=5)
				
				
	def add_events(self, events, c=None, ls=None, lw=None, label=None, ax=None):
		"""
		Add events to the figure.
		
		Parameters
		----------
		events: np.ndarray
			- All the event marker values.
		c: str
			- Color of the event marker.
			- Default: "k"
		ls: str
			- Line style.
			- Default: "-"
		lw: float
			- Linewidth.
			- Default: 1.5
		label: str
			- Label for the event type.
			- This will appear in the legend.
			- Default: None
		ax: int
			- Which specific axis to plot (1, 2, 3, ...)
			- None

		Returns
		-------
		None
		"""
		
		curr_row = self._get_curr_row() if ax is None else self._axs[ax]
		
		if c is None: c = self._get_new_color()
		
		xlim = self._xlim
		
		for i, event in enumerate(events):
			if xlim is not None:
				if xlim[0] <= event <= xlim[1]:
					if i == 0: # Label should be set only once for all the events
						curr_row[0].axvline(x=event, color=c, linestyle=ls, linewidth=lw, label=label)
					else:
						curr_row[0].axvline(x=event, color=c, linestyle=ls, linewidth=lw)
			else:
				if i == 0: # Label should be set only once for all the events
					curr_row[0].axvline(x=event, color=c, linestyle=ls, linewidth=lw, label=label)
				else:
					curr_row[0].axvline(x=event, color=c, linestyle=ls, linewidth=lw)
					
	def add_annotation(self, ann, label=None, patterns=None, ax=None, ylim=(0, 1), text_loc="middle"):
		"""
		Add annotation to the figure.
		
		Parameters
		----------
		ann : list[tuple[Number, Number, str]] | None
			- A list of annotation spans. Each tuple should be (start, end, label).
			- Default: None (no annotations).
		label: str
			- Label for the annotation type.
			- This will appear to the right of the aux plot.
			- Default: None
		patterns: list[str]
			- Patterns to group annotations
			- E.g., "*R" or "<tag>*" or ["A*", "*B"]
			- All elements in a group will have same color.
		ax: int
			- Which specific axis to plot (1, 2, 3, ...)
			- None
		ylim: tuple[number, number]
			- Y-limit for the annotation.
			- Default: (0, 1)
		text_loc: str
			- Location of text relative to the box. (b for bottom, m for middle, t for top)
			- Default: "middle"
		Returns
		-------
		None
		"""
		curr_row = self._get_curr_row() if ax is None else self._axs[ax]
		
		xlim = self._xlim
		
		if isinstance(patterns, str): patterns = [patterns]
		ann_copy = ann.copy()
		
		if patterns is not None:
			for i, (start, end, tag) in enumerate(ann_copy):
				group = None
				for j, pattern in enumerate(patterns):
					if fnmatch.fnmatch(tag, pattern):
						group = j
						break
				ann_copy[i] = (start, end, tag, group)
		else:
			for i, (start, end, tag) in enumerate(ann_copy):
				ann_copy[i] = (start, end, tag, None)
					
		colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
		
		# Text Location
		if text_loc == "b": 
			text_yloc = ylim[0] + 0.1 * (ylim[1] - ylim[0])
		elif text_loc == "t":
			text_yloc = ylim[1] - 0.1 * (ylim[1] - ylim[0])
		else:
			text_yloc = (ylim[1] + ylim[0]) / 2
		
		for i, (start, end, tag, group) in enumerate(ann_copy):
			# We make sure that we only plot annotation that are within the x range of the current view
			if xlim is not None:
				if start >= xlim[1] or end <= xlim[0]:
					continue
				
				# Clip boundaries to xlim
				start = max(start, xlim[0])
				end = min(end, xlim[1])
			
				
				if group is not None:
					box_color = colors[group]
				else:
					box_color = "lightgray"
				
				width = end - start
				rect = Rectangle((start, ylim[0]), width, ylim[1] - ylim[0], facecolor=box_color, edgecolor="black", alpha=0.7)
				curr_row[0].add_patch(rect)
				
				text_obj = curr_row[0].text(
					(start + end) / 2, text_yloc, tag,
					ha='center', va='center',
					fontsize=10, color="black", fontweight='bold', zorder=10, clip_on=True
				)
				
				text_obj.set_clip_path(rect)
			else:
				if group is not None:
					box_color = colors[group]
				else:
					box_color = "lightgray"
				
				width = end - start
				rect = Rectangle((start, ylim[0]), width, ylim[1] - ylim[0], facecolor=box_color, edgecolor="black", alpha=0.7)
				curr_row[0].add_patch(rect)
				
				text_obj = curr_row[0].text(
					(start + end) / 2, text_yloc, tag,
					ha='center', va='center',
					fontsize=10, color="black", fontweight='bold', zorder=10, clip_on=True
				)
				
				text_obj.set_clip_path(rect)
				
		if label is not None:
			curr_row[0].set_ylabel(label, rotation=0, ha="center", va="center")
			curr_row[0].yaxis.set_label_position("right")
			curr_row[0].yaxis.set_label_coords(1.05, 0.75)
			
	def add_legend(self, ypos=1.0):
		"""
		Add legend to the figure.

		Parameters
		----------
		ypos: float
			- y position from the top.
			- > 1 to push it higher, < 1 to push it lower
			- Default: 1.3
		
		Returns
		-------
		None
		"""
		axs = self._axs
		fig = self._fig
		
		all_handles, all_labels = [], []
		
		for ax in axs:
			handles, labels = ax[0].get_legend_handles_labels()
			all_handles.extend(handles)
			all_labels.extend(labels)
			
		# remove duplicates if needed
		fig.legend(all_handles, all_labels, loc='upper right', bbox_to_anchor=(0.95, ypos), ncol=3, frameon=True, bbox_transform=fig.transFigure)
		
	def add_title(self, title=None, s=13):
		"""
		Add title to the figure.

		Parameters
		----------
		title: str | None
			- Title of the figure.
			- Default: None
		s: Number
			- Font size.
			- Default: None
		"""
		axs = self._axs
		ref_ax = axs[0, 0] # Title is added to the top subplot (ref subplot)
		
		if title is not None:
			ref_ax.set_title(title, pad=10, size=s)
			
			
	def add_xlabel(self, xlabel=None, s=None):
		"""
		Add shared x-label to the figure.

		Parameters
		----------
		xlabel: str | None
			- xlabel for the figure.
			- Default: None
		s: Number
			- Font size.
			- Default: None
		"""
		axs = self._axs
		ref_ax = axs[-1, 0] # X-label is added to the last subplot
		if xlabel is not None:
			ref_ax.set_xlabel(xlabel, size=s)
			
	def add_xticks(self, xticks=None):
		"""
		Not implemented yet
		"""
		raise NotImplementedError("Please raise a github issue https://github.com/meluron-toolbox/modusa/issues")
		
	def save(self, path="./figure.png"):
		"""
		Save the figure.

		Parameters
		----------
		path: str
			- Path to the output file.

		Returns
		-------
		None
		"""
		fig = self._fig
		fig.savefig(path, bbox_inches="tight")
		


#======== Plot distribution ===========
def plot_dist(*args, ann=None, xlim=None, ylim=None, ylabel=None, xlabel=None, title=None, legend=None, show_hist=True, npoints=200, bins=30):
		"""
		Plot distribution.

		.. code-block:: python
			
			import modusa as ms
			import numpy as np
			np.random.seed(42)
			data = np.random.normal(loc=1, scale=1, size=1000)
			ms.plot_dist(data, data+5, data-10, ann=[(0, 1, "A")], legend=("D1", "D2", "D3"), ylim=(0, 1), xlabel="X", ylabel="Counts", title="Distribution")

		Parameters
		----------
		*args: ndarray
			- Data arrays for which distribution needs to be plotted.
			- Arrays will be flattened.
		ann : list[tuple[Number, Number, str] | None
			- A list of annotations to mark specific points. Each tuple should be of the form (start, end, label).
			- Default: None => No annotation.
		events : list[Number] | None
			- A list of x-values where vertical lines (event markers) will be drawn.
			- Default: None
		xlim : tuple[Number, Number] | None
			- Limits for the x-axis as (xmin, xmax).
			- Default: None
		ylim : tuple[Number, Number] | None
			- Limits for the y-axis as (ymin, ymax).
			- Default: None
		xlabel : str | None
			- Label for the x-axis.
			- - Default: None
		ylabel : str | None
			- Label for the y-axis.
			- Default: None
		title : str | None
			- Title of the plot.
			- Default: None
		legend : list[str] | None
			- List of legend labels corresponding to each signal if plotting multiple distributions.
			- Default: None
		show_hist: bool
			- Want to show histogram as well.
		npoints: int
			- Number of points for which gaussian needs to be computed between min and max.
			- Higher value means more points are evaluated with the fitted gaussian, thereby higher resolution.
		bins: int
			- The number of bins for histogram.
			- This is used only to plot the histogram.

		Returns
		-------
		plt.Figure
			- Matplotlib figure.
		"""
		from scipy.stats import gaussian_kde
	
		if isinstance(legend, str):
			legend = (legend, )
			
		if legend is not None:
			if len(legend) < len(args):
				raise ValueError(f"Legend should be provided for each signal.")
				
		# Create figure
		fig = plt.figure(figsize=(16, 4))
		gs = gridspec.GridSpec(2, 1, height_ratios=[0.1, 1])
	
		colors = plt.get_cmap('tab10').colors
	
		dist_ax = fig.add_subplot(gs[1, 0])
		annotation_ax = fig.add_subplot(gs[0, 0], sharex=dist_ax)
	
		# Set limits
		if xlim is not None:
			dist_ax.set_xlim(xlim)
			
		if ylim is not None:
			dist_ax.set_ylim(ylim)
			
		# Add plot
		for i, data in enumerate(args):
			# Fit gaussian to the data
			kde = gaussian_kde(data)
			
			# Create points to evaluate KDE
			x = np.linspace(np.min(data), np.max(data), npoints)
			y = kde(x)
			
			if legend is not None:
				dist_ax.plot(x, y, color=colors[i], label=legend[i])
				if show_hist is True:
					dist_ax.hist(data, bins=bins, density=True, alpha=0.3, facecolor=colors[i], edgecolor='black', label=legend[i])
			else:
				dist_ax.plot(x, y, color=colors[i])
				if show_hist is True:
					dist_ax.hist(data, bins=bins, density=True, alpha=0.3, facecolor=colors[i], edgecolor='black')
					
		# Add annotations
		if ann is not None:
			annotation_ax.set_ylim(0, 1) # For consistent layout
			# Determine visible x-range
			x_view_min = xlim[0] if xlim is not None else np.min(x)
			x_view_max = xlim[1] if xlim is not None else np.max(x)
			for i, (start, end, tag) in enumerate(ann):
				# We make sure that we only plot annotation that are within the x range of the current view
				if start >= x_view_max or end <= x_view_min:
					continue
				
				# Clip boundaries to xlim
				start = max(start, x_view_min)
				end = min(end, x_view_max)
				
				color = colors[i % len(colors)]
				width = end - start
				rect = Rectangle((start, 0), width, 1, color=color, alpha=0.7)
				annotation_ax.add_patch(rect)
				
				text_obj = annotation_ax.text((start + end) / 2, 0.5, tag, ha='center', va='center', fontsize=10, color='white', fontweight='bold', zorder=10, clip_on=True)
				text_obj.set_clip_path(rect)
				
		# Add legend
		if legend is not None:
			handles, labels = dist_ax.get_legend_handles_labels()
			fig.legend(handles, labels, loc='upper right', bbox_to_anchor=(0.9, 1.1), ncol=len(legend), frameon=True)
			
		# Set title, labels
		if title is not None:
			annotation_ax.set_title(title, pad=10, size=11)
		if xlabel is not None:
			dist_ax.set_xlabel(xlabel)
		if ylabel is not None:
			dist_ax.set_ylabel(ylabel)
			
		# Remove the boundaries and ticks from annotation axis
		if ann is not None:
			annotation_ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
		else:
			annotation_ax.axis("off")
			
		fig.subplots_adjust(hspace=0.01, wspace=0.05)
		plt.close()
		return fig
	

	
		
	
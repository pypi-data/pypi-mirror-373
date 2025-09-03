import plotly.graph_objects as go
from plotly.subplots import make_subplots
import polars as pl
from typing import List, Optional
import warnings

def make_plot(
    traces: List[go.Trace],
    subplot_titles: List[str] = ["Transcript Structure"],
    horizontal_spacing: float = 0.02,
    vertical_spacing: float = 0.02,
    showlegend: bool = True,
    height: int = 900,
    width: int = 1800,
    template: str = "plotly_white",
    boxgroupgap: float = 0.8,
    boxgap: float = 0.2,
    vert_grid_transcript_structure_plot: bool = True,
    horz_grid_transcript_structure_plot: bool = True,
    vert_grid_expression_plot: bool = True,
    horz_grid_expression_plot: bool = True,
    legend_font_size: int = 12,
    xaxis_font_size: int = 12,
    yaxis_font_size: int = 12,
    subplot_title_font_size: int = 16,
    legend_title_font_size: int = 14,
    hover_font_size: int = 12,
    hovermode: str = "closest",
    column_widths: list = None
) -> go.Figure:
    """
    Creates a multi-panel Plotly figure combining transcript structure plots and expression data plots.

    This function constructs a Plotly figure with multiple subplots arranged horizontally. It accepts a list of
    Plotly traces representing different data types (e.g., transcript structures, expression data) and organizes them
    into subplots. The function customizes the layout, axes, and appearance of each subplot based on the provided
    parameters, allowing for flexible visualization of genomic data alongside expression metrics.

    **Expected Structure of `traces`:**
    - The `traces` list should contain multiple sublists, each representing traces for a subplot.
    - The last element in `traces` must be a dictionary (`y_dict`) mapping transcript identifiers to y-axis positions.

    Parameters
    ----------
    traces : List[List[go.Trace]] or List[List[dict]]
        A list where each element is a list of Plotly traces (either `go.Trace` objects or dictionaries for transcript structures).
        The last element must be a dictionary mapping transcript identifiers to y-axis positions.
    subplot_titles : List[str], optional
        A list of titles for each subplot. Default is ["Transcript Structure"].
    horizontal_spacing : float, optional
        Horizontal spacing between subplots as a fraction of the average subplot width. Default is 0.02.
    vertical_spacing : float, optional
        Vertical spacing between subplots as a fraction of the average subplot height. Default is 0.02.
    showlegend : bool, optional
        Whether to display the legend. Default is True.
    height : int, optional
        The height of the figure in pixels. Default is 800.
    width : int, optional
        The width of the figure in pixels. Default is 1800.
    template : str, optional
        The Plotly template to use for styling. Default is "plotly_white".
    boxgroupgap : float, optional
        Gap between grouped boxes in box or violin plots. Default is 0.8.
    boxgap : float, optional
        Gap between individual boxes in box or violin plots. Default is 0.2.
    vert_grid_transcript_structure_plot : bool, optional
        Whether to show vertical grid lines in transcript structure plots. Default is True.
    horz_grid_transcript_structure_plot : bool, optional
        Whether to show horizontal grid lines in transcript structure plots. Default is True.
    vert_grid_expression_plot : bool, optional
        Whether to show vertical grid lines in expression plots. Default is True.
    horz_grid_expression_plot : bool, optional
        Whether to show horizontal grid lines in expression plots. Default is True.
    legend_font_size : int, optional
        Font size for legend text. Default is 12.
    xaxis_font_size : int, optional
        Font size for x-axis labels. Default is 12.
    yaxis_font_size : int, optional
        Font size for y-axis labels. Default is 12.
    subplot_title_font_size : int, optional
        Font size for subplot titles. Default is 16.
    legend_title_font_size : int, optional
        Font size for the legend title. Default is 14.
    hover_font_size : int, optional
        Font size for hover text labels. Default is 12.
    hovermode : str, optional
        Hover mode for the figure. Options include "closest", "x", "y", "x unified", "y unified", etc. Default is "closest".
    column_widths: list, optional
        A list of floats containing the same number of items as the number of subplots you are trying to generate.
        For a figure with three subplots you could pass [0.4, 0.3, 0.3] to make the first subplot take up
        40% of the horizontal space and the second and third subplot each take 30% of the horizontal space.
        By default it is set to `None` which will make the subplots have proportional sizes.

    Returns
    -------
    go.Figure
        A Plotly Figure object containing the assembled subplots with customized layout and styling.

    Raises
    ------
    ValueError
        If `traces` does not contain at least one set of traces and a `y_dict` mapping.

    Examples
    --------
    Create a figure with transcript structure and expression data:

    >>> import plotly.graph_objects as go
    >>> from RNApysoforms import make_plot
    >>> fig = make_plot(
    ...     traces=traces,
    ...     subplot_titles=["Transcript Structure", "Expression Levels"],
    ...     height=600,
    ...     width=1200
    ... )
    >>> fig.show()

    Notes
    -----
    - The function expects the last element of `traces` to be a dictionary (`y_dict`) mapping transcript identifiers to y-axis positions.
    - Traces are classified into transcript structure traces or expression data traces based on their content:
        - Transcript traces are expected to be dictionaries (usually shapes or annotations).
        - Expression traces are expected to be Plotly trace objects with a 'type' attribute (e.g., `go.Box`, `go.Violin`).
    - The function dynamically assigns traces to subplots and customizes axes and layout based on the type of data.
    - The y-axis is shared across subplots to align transcript structures with their corresponding expression data.
    - Hover settings can be customized using the `hovermode` parameter.

    """

    ## Separate traces and dictionary
    y_dict = traces[-1]
    full_trace_list = traces[:-1]

    ## Define column widths
    if column_widths == None:
        column_width = (1/len(full_trace_list))
        column_widths = [column_width] * len(full_trace_list)
    elif (len(column_widths) != len(full_trace_list)) or (not isinstance(column_widths, list)):
        warnings.warn("The `column_widths` parameter must be a list of the same length as the number of subplots being generated"
                          "\nMaking all subplots have the same size as default option")
        column_width = (1/len(full_trace_list))
        column_widths = [column_width] * len(full_trace_list)


    # Initialize the subplot figure with shared y-axes
    fig = make_subplots(
        rows=1,
        cols=len(full_trace_list),
        subplot_titles=subplot_titles,
        horizontal_spacing=horizontal_spacing,
        vertical_spacing=vertical_spacing,
        column_widths=column_widths,
        shared_yaxes=True,  # Share y-axes across all subplots
    )

    # Initialize lists to separate transcript and expression traces and their subplot indexes
    transcript_traces = []
    expression_traces = []
    transcript_indexes = []
    expression_indexes = []

    # Classify traces into transcript or expression traces based on their content
    index = 1  # Start subplot index from 1
    for trace in full_trace_list:
        if hasattr(trace[0], 'type'):
            # If the trace has a 'type' attribute, it's an expression trace (e.g., go.Box, go.Violin)
            expression_traces.extend(trace)
            expression_indexes.append(index)
        elif isinstance(trace[0], dict):
            # If the trace is a dictionary, it's a transcript trace (e.g., shapes or annotations)
            transcript_traces.append(trace)
            transcript_indexes.append(index)
        index += 1  # Increment subplot index

    # Add all traces to their respective subplots
    for i, subplot_traces in enumerate(full_trace_list, start=1):
        fig.add_traces(
            subplot_traces,
            rows=[1] * len(subplot_traces),
            cols=[i] * len(subplot_traces)
        )

    # Customize axes and layout for transcript structure subplots
    for i in transcript_indexes:
        # Customize x-axes for transcript structure plots (hide tick labels)
        fig.update_xaxes(
            showticklabels=False,
            title="",
            row=1,
            col=i,
            showgrid=vert_grid_transcript_structure_plot
        )
        # Customize y-axes for transcript structure plots (show transcript labels)
        fig.update_yaxes(
            showticklabels=False,
            tickvals=list(y_dict.values()),
            ticktext=list(y_dict.keys()),
            tickfont=dict(size=10, family='DejaVu Sans', color='black'),
            title="",  # Optional title for y-axis
            row=1,
            col=i,
            showgrid=horz_grid_transcript_structure_plot
        )

    # Customize axes and layout for expression data subplots
    for i in expression_indexes:
        # Customize x-axes for expression plots (show tick labels)
        fig.update_xaxes(
            showticklabels=True,
            title="",  # Optional title for x-axis
            row=1,
            col=i,
            showgrid=vert_grid_expression_plot
        )
        # Customize y-axes for expression plots (hide tick labels)
        fig.update_yaxes(
            showticklabels=False,
            tickvals=list(y_dict.values()),
            ticktext=list(y_dict.keys()),
            ticks='',  # Hide ticks
            row=1,
            col=i,
            range=[-0.8, (len(y_dict) - 0.2)],  # Adjust y-axis range to align with transcript plots
            showgrid=horz_grid_expression_plot
        )

    # Ensure the first subplot's y-axis shows tick labels (transcript identifiers)
    fig.update_yaxes(
        showticklabels=True,
        row=1,
        col=1
    )

    # Update overall layout settings
    fig.update_layout(
        title_text="",  # Optional overall title
        showlegend=showlegend,
        height=height,
        width=width,
        hovermode=hovermode,
        hoverlabel=dict(font=dict(size=hover_font_size)),
        margin=dict(l=100, r=50, t=100, b=50),  # Adjust margins as needed
        boxmode='group',
        legend_tracegroupgap=7,
        boxgroupgap=boxgroupgap,
        boxgap=boxgap,
        violinmode='group',
        violingroupgap=boxgroupgap,
        violingap=boxgap,
        yaxis=dict(
            range=[-0.8, (len(y_dict) - 0.2)],
            tickfont=dict(size=yaxis_font_size)
        ),
        legend=dict(font=dict(size=legend_font_size), grouptitlefont=dict(size=legend_title_font_size)),
        template=template,
        annotations=[dict(font=dict(size=subplot_title_font_size)) for annotation in fig['layout']['annotations']])
    
    """
    There is a bug in plotly and the tickfont for the x-axis has to be updated in this manner,
    it can't be done using the `update_layout` function. See: https://github.com/plotly/plotly.py/issues/2922
    """
    fig.update_xaxes(tickfont_size=(xaxis_font_size))

    return fig  # Return the assembled figure

"""Display when motion is detected onto a quad (bar) graph, through the capture.py script"""

from capture import times_df            #execute capture.py and get the times_df from it
from bokeh.plotting import figure, show, output_file
from bokeh.models import HoverTool, ColumnDataSource

#format the date and time data to be displayed
times_df["Start_string"] = times_df["Start"].dt.strftime("%Y-%m-%d %H:%M:%S")       
times_df["End_string"] = times_df["End"].dt.strftime("%Y-%m-%d %H:%M:%S")

#used to display the date and times properly
cds = ColumnDataSource(times_df)

#format the graph
p = figure(x_axis_type='datetime', height = 200, width = 600, title = "Motion Graph", sizing_mode='stretch_both')
p.yaxis.minor_tick_line_color=None
p.ygrid[0].ticker.desired_num_ticks = 1

#show the start and end time for each quad (bar) in the graph when mouse hovers over it
hover = HoverTool(tooltips=[("Start", "@Start_string"), ("End", "@End_string")])
p.add_tools(hover)

#create the quads on the graph corresponding to motion or foreign objects detected in frame
q = p.quad(left="Start", right="End", bottom=0, top=1, color="blue", source = cds)

output_file("Graph.html")
show(p)
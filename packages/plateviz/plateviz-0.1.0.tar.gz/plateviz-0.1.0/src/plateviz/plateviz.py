import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import customtkinter as ctk
from tkextrafont import Font
from importlib import resources
from cycler import cycler
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.metrics import r2_score
from scipy.optimize import curve_fit
from synergy_file_reader import SynergyFile, SynergyPlate

ctk.set_appearance_mode('light')
sns.set_style('ticks')
sns.set_context('talk', font_scale=0.8)

font_path = resources.files('plateviz') / 'resources' / 'Raleway-VariableFont_wght.ttf'

mpl_font_path = resources.files('plateviz') / 'resources' / 'Raleway-Regular.ttf'
fm.fontManager.addfont(mpl_font_path)
plt.rcParams['font.family'] = 'Raleway'

theme_path = resources.files('plateviz') / 'resources' / 'Goldilocks.json'
ctk.set_default_color_theme(theme_path)

AUTHOR = 'Radium2000'
BRAND = 'plateviz by Radium2000'

class PlateApp(ctk.CTk):

    def __init__(self, plate_data, channels, nick, cmap):

        super().__init__()

        # Loading font into customtkinter
        self.font = Font(file=font_path)

        self.data = plate_data
        self.channels = np.array(channels)
        self.color_cycle = plt.cycler(color=['#3C73C5', '#fb4b4e', '#37b632', '#7D42E2'])

        # Nickname dictionary. This enables the user to define nicknames for all channels.
        self.nick_dict = dict(zip(self.channels, nick))

        # Setting the colormap.
        custom_cmap = plt.get_cmap(cmap)
        multicolor = [custom_cmap(i) for i in np.linspace(0.1, 0.9, 12)]
        plt.rcParams['axes.prop_cycle'] = cycler(color=multicolor)
        
        # Setting up the customtkinter app layout
        self.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.geometry('900x765')
        self.resizable(False, False)
        
        self.title('plate-viz tool')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # MAIN FRAME
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        self.main_frame.grid_columnconfigure(0, weight=10)
        self.main_frame.grid_columnconfigure(1, weight=1)
        
        # EXTRAS FRAME
        self.extras_frame = ctk.CTkFrame(self.main_frame, corner_radius=6,
                                         height=325)
        self.extras_frame.grid(row=0, column=1, padx=10, pady=10, sticky='n')
        self.extras_label = ctk.CTkLabel(self.extras_frame, text='Channels',
                                         font=('Raleway', 16, 'bold'))
        self.extras_label.grid(row=0, column=0)
        self.extras_frame.grid_columnconfigure(0, weight=1)
        self.extras_frame.grid_propagate(False)
        
        # CHANNEL CHECKBOXES
        self.checkboxes = {}
        self.checkbox_states = {}
        for i, channel in enumerate(self.channels):
            cb_state = ctk.BooleanVar(value=False)
            self.checkbox_states[channel] = cb_state
            self.checkboxes[channel] = ctk.CTkCheckBox(
                self.extras_frame, 
                text=self.nick_dict[channel],
                font=ctk.CTkFont('Raleway', 14, 'bold'),
                variable=cb_state,
                command=self.on_checkbox_select
            )
            self.checkboxes[channel].grid(row=i+1, column=0, padx=10, pady=5, sticky='w')
        
        # If only one channel exists, remove the ability to select/deselect channels. Select the only possible one and then disable the checkbox.
        if len(self.channels)==1:
            self.checkbox_states[self.channels[0]].set(True)
            self.checkboxes[self.channels[0]].configure(state='disabled')
        
        # INTERACTIVE MODE SWITCH
        self.int_state = ctk.BooleanVar(value=False)
        self.interact_switch = ctk.CTkSwitch(self.extras_frame, text='Interactive',
                                           font=ctk.CTkFont('Raleway', 16, 'bold'),
                                           variable=self.int_state,
                                           command=self.on_int_switch
                                           )
        self.interact_switch.grid(row=len(self.channels)+1, column=0, padx=10, pady=10, sticky='nw')

        # MULTIWELL SWITCH
        self.mw_state = ctk.BooleanVar(value=False)
        self.multiwell_switch = ctk.CTkSwitch(self.extras_frame, text='Multi Well',
                                           font=ctk.CTkFont('Raleway', 16, 'bold'), 
                                           variable=self.mw_state,
                                           command=self.on_multi_switch
                                           )
        self.multiwell_switch.grid(row=len(self.channels)+2, column=0, padx=10, pady=10, sticky='nw')

        # CLEAR PLOT BUTTON
        clr_btn = ctk.CTkButton(
            self.extras_frame,
            text='Clear Plot',
            font=ctk.CTkFont('Raleway', 16, 'bold'),
            command=self.clear_frame
        )
        clr_btn.grid(row=len(self.channels)+3, column=0, padx=10, pady=10)

        # GROWTH RATE BUTTON
        self.growth_btn = ctk.CTkButton(
            self.extras_frame,
            text='Growth Rate',
            font=ctk.CTkFont('Raleway', 16, 'bold'),
            command=self.calc_growth_rate,
            state='disabled'
        )
        self.growth_btn.grid(row=len(self.channels)+4, column=0, padx=10, pady=10)

        # GRAPH SETTINGS FRAME
        self.graph_frame = ctk.CTkFrame(self.main_frame, border_width=0)
        self.graph_frame.grid(row=1, column=1, pady=50, sticky='nw')

        # LOG SCALE BUTTON
        self.log_state = ctk.BooleanVar(value=False)
        log_btn = ctk.CTkCheckBox(
            self.graph_frame,
            text = 'log scale',
            font = ctk.CTkFont('Raleway', 16),
            variable=self.log_state,
            command=self.set_log_scale
        )
        log_btn.grid(row=0, column=0, padx=10, pady=10)

        # BUTTON FRAME
        self.button_frame = ctk.CTkFrame(self.main_frame, corner_radius=6)
        self.button_frame.grid(row=0, column=0, padx=10, pady=10)
        
        # column labels
        for j in range(12):
            label = ctk.CTkLabel(self.button_frame, text=str(j+1),
                                 font=ctk.CTkFont('Raleway', 14, 'bold'))
            label.grid(row=0, column=j+1, padx=2, pady=2)
        
        # row labels
        for i in range(8):
            label = ctk.CTkLabel(self.button_frame, text=chr(65+i),
                                 font=ctk.CTkFont('Raleway', 14, 'bold'))
            label.grid(row=i+1, column=0, padx=2, pady=2)
        
        # WELL BUTTONS
        for i in range(8):
            for j in range(12):
                btn = ctk.CTkButton(
                    self.button_frame,
                    text='',
                    width=30,
                    height=30,
                    corner_radius=15,
                    command=lambda x=j, y=i: self.on_button_click(x, y)
                )
                btn.grid(row=i+1, column=j+1, padx=2, pady=2)
        
        # FIGURE AND CANVAS
        self.fig, self.ax = plt.subplots(figsize=(6, 4), facecolor='#fce5b7')
        self.ax.set_facecolor('#fce5b7')
        self.ax.set_title(BRAND, fontsize=14, color='#57311a')
        self.ax.grid(True, color='#57311a', alpha=0.3)
        self.ax.spines['bottom'].set_color('#57311a')
        self.ax.spines['top'].set_color('#57311a')
        self.ax.spines['right'].set_color('#57311a')
        self.ax.spines['left'].set_color('#57311a')
        self.ax.tick_params(colors='#57311a')
        self.ax.grid(True)
        plt.tight_layout()
        
        # Embed the figure.
        self.canvas_frame = ctk.CTkFrame(self.main_frame, border_width=0)
        self.canvas_frame.grid(row=1, column=0, padx=10, sticky='e')
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0)

        # TEXT BOX
        self.output_txt = ctk.CTkTextbox(
            self.graph_frame,
            wrap = 'word',
            font=ctk.CTkFont('Raleway', 14),
            state = 'disabled'
        )
        self.output_txt.grid(row=2, column=0, padx=10, pady=10, sticky='nw')

        self.tbox_label = ctk.CTkLabel(self.graph_frame, text='Growth Rates',
                                        font=ctk.CTkFont('Raleway', 16, 'bold'))
        self.tbox_label.grid(row=1, column=0, sticky='n')

    def on_checkbox_select(self):

        # Growth rate determination is only allowed if exactly one channel is selected.
        selected_cbs = [var.get() for _, var in self.checkbox_states.items()]

        # To fix the issue of there being more than one line on the plot when the growth rate button is pressed.
        num_lines = len(self.ax.get_lines())

        if (sum(selected_cbs)!=1) or (num_lines!=1):
            self.growth_btn.configure(state='disabled')
        else:
            self.growth_btn.configure(state='normal')

    def on_multi_switch(self):

        # To disable growth rate determination in multiwell mode.
        state = self.mw_state.get()
        num_lines = len(self.ax.get_lines())
        if (state==True) and (num_lines!=1):
            self.growth_btn.configure(state='disabled')
        else:
            self.growth_btn.configure(state='normal')
    
    def clear_frame(self):

        self.ax.clear()
        self.ax.grid(True)
        self.ax.set_title(BRAND, fontsize=14, color='#57311a')
        if self.log_state.get():
            self.ax.set_yscale('log')
        self.canvas.draw()
    
    def on_closing(self):

        plt.close(self.fig)
        self.quit()
        self.destroy()

    def set_log_scale(self):
        
        state = self.log_state.get()
        if state:
            self.ax.set_yscale('log')
            self.canvas.draw()
        else:
            self.ax.set_yscale('linear')
            self.canvas.draw()

    def calc_growth_rate(self):

        if self.ax.get_title()==BRAND:
            return
        
        for line in self.ax.get_lines():
            times, population = line.get_xdata(), line.get_ydata()
        
        t = np.linspace(min(times), max(times), 500)

        # Guess for initial parameters for the sigmoidal curve.
        init_params = [max(population), np.median(times), 1, min(population)]

        # To catch run time errors
        try:
            params, _ = curve_fit(sigmoid, xdata=times, ydata=population, p0=init_params)
            goodness = r2_score(population, sigmoid(times, *params))

            # Based on `r2_score` reject any fits with goodness of fit less than 0.85
            if goodness>0.85:
                
                # Remove 'not a sigmoidal curve' warning text if exists.
                for text in self.ax.texts:
                    text.remove()
                
                # Getting labels from the legend to prevent plotting of multiple fits. The second part of the following if statement is to prevent the determination of growth rate if a single line is displayed while in multiwell mode. 
                _, labels = self.ax.get_legend_handles_labels()

                if ('fit' not in labels) and (self.ax.get_title()!='Multi-Well Plotting'):
                    self.ax.plot(t, sigmoid(t, *params), ls='--', label='fit')
                    self.ax.legend(loc='upper right', fontsize='x-small')
                    self.canvas.draw()
                    self.output_txt.configure(state='normal')
                    self.output_txt.insert('end', f'{labels[0]}@{self.ax.get_title()} = {round(params[2], 2)} u/hr\n')
                    self.output_txt.configure(state='disabled')

            else:
                
                # Display a warning on the plot if the fitting is below 0.85 goodness level.
                self.ax.text(0.05, 0.9, 'not a sigmoidal curve', 
                         transform=self.ax.transAxes,
                         horizontalalignment='left', verticalalignment='center',
                         fontsize=12, color='#57311a',
                         bbox=dict(facecolor='w', boxstyle='round', alpha=0.5))
                self.canvas.draw()

        except RuntimeError as e:
            for text in self.ax.texts:
                text.remove()
            self.ax.text(0.05, 0.9, 'optimal parameters not found;\nmaybe not a sigmoid', 
                         transform=self.ax.transAxes,
                         horizontalalignment='left', verticalalignment='center',
                         fontsize=12, color='#57311a',
                         bbox=dict(facecolor='w', boxstyle='round', alpha=0.5))
            self.canvas.draw()

    def on_int_switch(self):

        # Get the current state of the switch.
        state = self.int_state.get()
        
        # If the switch is on, pop the current view of the embedded figure into a dedicated matplotlib figure window.
        if state:

            # Simultaneously disable the multiwell switch to prevent multiplot functionality in the interactive mode.
            self.mw_state.set(False)
            self.multiwell_switch.configure(state='disabled')

            # This prevents the brand plot to be popped out into a new window.
            if self.ax.get_title()!=BRAND:
                plt.close(self.fig)
                _, new_ax = plt.subplots()
                new_ax.clear()
                new_ax.set_prop_cycle(self.color_cycle)
                new_ax.grid(True)

                # Copy all lines.
                for line in self.ax.get_lines():
                    line_label = str(line.get_label())
                    new_ax.plot(line.get_xdata(), line.get_ydata(), label=line_label, ls=line.get_linestyle())
                
                # In case of a scatter plot, copy all collections. 
                for coll in self.ax.collections:
                    offsets = coll.get_offsets()
                    facecolors = coll.get_facecolors()
                    sizes = coll.get_sizes()
                    edgecolors = coll.get_edgecolors()
                    labels = coll.get_label()
                    new_ax.scatter(
                        offsets[:, 0],
                        offsets[:, 1],
                        s=sizes,
                        c=facecolors,
                        edgecolors=edgecolors,
                        label=labels
                    )
                new_ax.legend(loc='upper right', fontsize='x-small')
                new_ax.set_title(self.ax.get_title(), color='#57311a')
                new_ax.set_xlim(self.ax.get_xlim())
                new_ax.set_ylim(self.ax.get_ylim())
                new_ax.set_xlabel(self.ax.get_xlabel())
                new_ax.set_ylabel(self.ax.get_ylabel())
                if self.log_state.get():
                    new_ax.set_yscale('log')
                plt.tight_layout()
                plt.show(block=False)

            # Clear the axis for a better viewing experience. 
            self.ax.clear()
            self.ax.grid(True)
            self.ax.set_title(BRAND, fontsize=14, color='#57311a')
            if self.log_state.get():    
                self.ax.set_yscale('log')
            self.canvas.draw()
    
        # If the interactive switch is off enable the multiplot switch and do nothing else. 
        else:
            self.multiwell_switch.configure(state='normal')

    def on_button_click(self, x, y):

        # Raise KeyError on KeyError.
        try:

            # Get current state of the checkboxes. If none are selected, diaplay a "warning" screen.
            current_states = [var.get() for _, var in self.checkbox_states.items()]
            if np.array(current_states).any() == False:
                self.ax.clear()
                self.ax.set_prop_cycle(self.color_cycle)
                self.ax.grid(True)
                self.ax.set_title(BRAND, fontsize=14, color='#57311a')
                self.ax.text(0.5, 0.5, 'Select a channel to start plotting', 
                            transform=self.ax.transAxes,
                            horizontalalignment='center', verticalalignment='center',
                            fontsize=16, color='#57311a')
                if self.log_state.get():
                    self.ax.set_yscale('log')
                self.canvas.draw()

            else:

                # Create a list of all channels that need to be plotted.
                to_plot = self.channels[current_states]
                
                # Checking state of multiwell_switch.
                if self.mw_state.get() == False:
                    
                    # If interactive mode is on, don't use the embedded figure. Using matplotlibs inbuilt plotter. 
                    if self.int_state.get():
                        self.multiwell_switch.configure(state='disabled')
                        plt.close(self.fig)
                        _, new_ax = plt.subplots()
                        new_ax.clear()
                        new_ax.set_prop_cycle(self.color_cycle)
                        new_ax.set_title(f'{chr(65+y)}{x+1}', color='#57311a')
                        new_ax.grid(True)
                        new_ax.set_xlabel('time [hrs]', color='#57311a', fontsize=14)
                        for channel in to_plot:
                            new_ax.plot(self.data.times[channel]/3600, self.data[chr(65+y), x+1, channel], label=self.nick_dict[channel])
                            new_ax.legend(loc='upper right', fontsize='x-small')
                        if self.log_state.get():
                            new_ax.set_yscale('log')
                        plt.show(block=False)
                    
                    # If interactive mode is off, use the embedded figure (self.ax)
                    else:
                        self.multiwell_switch.configure(state='normal')
                        self.ax.clear()
                        self.ax.set_prop_cycle(self.color_cycle)
                        self.ax.set_title(f'{chr(65+y)}{x+1}', color='#57311a')
                        self.ax.set_xlabel('time [hrs]', color='#57311a', fontsize=14)
                        self.ax.grid(True)
                        for channel in to_plot:
                            self.ax.plot(self.data.times[channel]/3600, self.data[chr(65+y), x+1, channel], label=self.nick_dict[channel])
                        self.ax.legend(loc='upper right', fontsize='x-small')
                        if self.log_state.get():
                            self.ax.set_yscale('log')
                        self.canvas.draw()

                else:

                    # Clearing the axis if brand plot is on screen.
                    if self.ax.get_title()==BRAND:
                        self.ax.clear()

                    # Checking if current plot is part of multiwell. Get all the labels in the current legend.
                    _, labels = self.ax.get_legend_handles_labels()
                    flag = True

                    # The flag is set to False if any label that is akin to either the channel name or channel nickname is found. An exact match means that multiplot is not enabled on the current view. All multiplot labels are accompanied by a well coordinate.
                    for item in self.channels:
                        if (item in labels) or (self.nick_dict[item] in labels):
                            flag = False
                            self.ax.clear()
                    
                    # Checking if selected well has already been plotted by looking up the axis legend. This will only plot if the flag is set to True, i.e., the existing plot is part of multiwell plotting.
                    plotted_wells=[label.split('@')[1] for label in labels if flag==True]
                    if chr(65+y)+str(x+1) not in plotted_wells:
                        self.ax.set_title('Multi-Well Plotting', color='#57311a')
                        self.ax.grid(True)
                        self.ax.set_xlabel('time [hrs]', color='#57311a', fontsize=14)
                        for channel in to_plot:
                            self.ax.plot(self.data.times[channel]/3600, self.data[chr(65+y), x+1, channel], label=f'{self.nick_dict[channel]}@{chr(65+y)}{x+1}')
                            self.ax.legend(loc='upper right', fontsize='xx-small')
                        if self.log_state.get():
                            self.ax.set_yscale('log')
                        self.canvas.draw()
        
        except KeyError as e:
            print('Key', e, 'not found')
        
        # Re-enabling the growth rate button if there is only one line on the plot and if multiwell plotting is not enabled.
        num_lines = len(self.ax.get_lines())
        if (num_lines==1) and (self.mw_state.get()==False):
            self.growth_btn.configure(state='normal')

def sigmoid(x:float|np.ndarray, K:float, x0:float, r:float, y_offset:float):
    '''Sigmoid function.

    Parameters
    ----------
    x : float | np.ndarray
        number or numpy array containing values for determination
    K : float
        carrying capacity
    x0 : float
        point where the function is half of its maximum value
    r : float
        growth rate
    y_offset : float
        y-offset to account for non-zero starting population

    Returns
    -------
    float | np.ndarray
        value of the sigmoid function at `x`
    '''
    y = K / (1 + np.exp(-r*(x-x0))) + y_offset
    return y

def plateDisplay(plate_data:SynergyPlate, channels:list, nick:list=None, cmap:str='gnuplot'):
    '''Launches the PlateViz tool.

    Parameters
    ----------
    plate_data : SynergyPlate
        Data in the form of SynergyPlate class as generated by the `synergy-file-reader` library.
    channels : list
        List containing the channel names as written in the `plate_data` keys.
    nick : list, optional
        Nicknames that you want to give to the respective channels instead of the auto-generated plate reader ones, by default None
    cmap : str, optional
        Any `matplotlib` consistent color map; used for multiwell plotting, by default 'gnuplot'
    '''
    if nick is None:
        nick = channels
    if isinstance(plate_data, SynergyPlate):
        app = PlateApp(plate_data=plate_data, channels=channels, nick=nick, cmap=cmap)
        app.mainloop()
    else:
        raise TypeError("plate_data not of type SynergyPlate")
        pass

example_data_path = resources.files('plateviz') / 'resources' / 'example_data.txt'
example_data = SynergyFile(example_data_path)[0]

# For testing purposes.
if __name__ == "__main__":
    od = 'Read 1:600'
    fl1 = 'Read 2:520,560'
    fl2 = 'Read 2:433,475'
    plateDisplay(example_data, channels=[od, fl1, fl2], nick=['OD', 'Venus', 'Cerulean'])
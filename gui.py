import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import tkintermapview as tkm
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database_handler import fetch
from datetime import *
import datetime
import json


with open('conf/node_config.json', 'r') as f:
    nodes = json.load(f)


nodes_name=[]
for i in nodes:
    nodes_name.append(i['name'])


#function to get the data and insert them in the tree
def get_data():
    data = []
    x = []
    y = []
    y2 = []
    #This calls the fetch fucntion from database_handler and return a list of data
    data = fetch(entry_sensor.get(), cal.get_date(), cal2.get_date())
    jdata = json.loads(data)
    #clear tree data
    for item in tree.get_children():    
      tree.delete(item)

    #clear output text data
    output.delete(1.0,tk.END) 
     
    for z in jdata:
        date_obj = datetime.datetime.fromisoformat(z['timestamp'])
        try:
            tree.insert("", 0, value=(z["dev_id"],z["humidity"], z["temperature"], date_obj))
            y.append(z['humidity'])
            y2.append(z['temperature'])
            x.append(date_obj)
        except:
            y2.append(z['temperature'])
            x.append(date_obj)
            tree.insert("", 0, value=(z["dev_id"], "", z["temperature"], date_obj))
    try:   
        plot(x, y, y2)
    except:
        plot(x, 0, y2)
    get_dss(data)

#function to draw the diagram with the data  
def plot(x, y, y2):
    fig.clear()
    #adding the subplot
    plot1 = fig.add_subplot(111)
    #plotting the graph
    try:
        plot1.plot(x, y, label="hum")
        plot1.plot(x, y2, label="tmp")
    except:
        plot1.plot(x, y2, label="tmp")
    plot1.legend()
    plot1.set_xticklabels("")
    plot1.set_xlabel('time')
    canvas.draw()
    return

#function to get dss output
def get_dss(data):
    jdata = json.loads(data)
    try:
        if jdata[0]['location'] == "romagna":
            with open('conf/dss_config_romagna.json', 'r') as f2:
                dss_data = json.load(f2)
        else:
            with open('conf/dss_config_toscana.json', 'r') as f2:
                dss_data = json.load(f2)

        tmp = []
        tmp_day = []
        tmp_night = []
        morning_time_str = dss_data["day"]
        morning_time = datetime.datetime.fromisoformat(morning_time_str)
        evening_time_str = dss_data["night"]
        evening_time = datetime.datetime.fromisoformat(evening_time_str)

        #Dividing temperature data between day and nighth to calculate the average temperature
        for i in jdata:
            date_obj = datetime.datetime.fromisoformat(i['timestamp'])
            tmp.append(i['temperature'])
            if date_obj.time() > morning_time.time() and date_obj.time() < evening_time.time():
                tmp_day.append(i['temperature'])
            elif date_obj.time() < morning_time.time() or date_obj.time() > evening_time.time():
                tmp_night.append(i['temperature'])
    except:
        output.insert(1.0, "No data for this period of time\n") 

    try: 
        #This is the algorithm of the dss which uses data from temperature, humidity to analize the field situation
        for z in jdata:
            date_obj = datetime.datetime.fromisoformat(z['timestamp'])
            if z['humidity'] == dss_data["error_0"]:
                output.insert(tk.END, "ERROR!!\nThe humidity level is not real (0)\n" + str(date_obj) + "\n\n", "err")
            elif z['humidity'] < dss_data["wilting_point"]:
                output.insert(tk.END, "WARNING!!\nThe humidity is in the range of the wilting point\n" + str(date_obj) + "\n\n", "warn")
            elif z['humidity'] > dss_data["wilting_point"] and z['humidity'] < dss_data["low_humidity"] and z['temperature'] < dss_data["temperature"]:
                output.insert(tk.END, "The humidity is low, solutions:\nIrrigate the field\nIncrease shading or cooling\n" + str(date_obj) + "\n\n")
            elif z['humidity']>dss_data["high_humidity"] and z['temperature']>dss_data["temperature"] and date_obj.time()>morning_time.time() and date_obj.time()<evening_time.time():
                output.insert(tk.END, "The humidity is high, solutions:\nIncrease ventilation if in a greenhouse\nDo not water\n" + str(date_obj) + "\n\n")
            elif z['humidity'] > dss_data["error_100"]:
                output.insert(tk.END, "ERROR!!\nThe humidity level is not real (>100)\n" + str(date_obj) + "\n\n", "err")
    except:
        output.insert(1.0, "This sensor has no humidity data available\n")

    #Show output in the textbox 
    output.insert(1.0, "The max temperature is:\n" + str(max(tmp)) + "\n\n")
    output.insert(1.0, "The min temperature is:\n" + str(min(tmp)) + "\n")
    output.insert(1.0, "The average temperature is:\n" + str(round(sum(tmp) / len(tmp), 1)) + "\n")
    output.insert(1.0, "The average temperature at day is:\n" + str(round(sum(tmp_day) / len(tmp_day), 1)) + "\n")
    output.insert(1.0, "The average temperature at night is:\n" + str(round(sum(tmp_night) / len(tmp_night), 1)) + "\n")
    try:
        if jdata[0]['pressure']:
            output.insert(1.0, "This sensor has pressure data available\n\n")
    except:
        pass
    try:
        output.insert(1.0, "Taking the dss configuration from: " +jdata[0]["location"]+ "\n\n")
    except:
        pass
    



#Function to open the zoomed output window
def zoom_output():
    zoom_window = tk.Toplevel(window)
    zoom_window.state('zoomed')
    zoom_window.title("Finestra di Zoom")
    textbox = tk.Text(zoom_window, background="#d3d3d3")
    textbox.pack(fill=tk.BOTH, expand=True)
    data = output.get(1.0, tk.END)
    textbox.insert(tk.END, data)
    textbox.configure(font=("Ariel", 15), state="disabled")

#Function to open the zoomed data window
def zoom_data():
    data_window = tk.Toplevel(window)
    data_window.state('zoomed')
    data_window.title("Finestra di dati")
    tree1 = ttk.Treeview(data_window, column=("c1", "c2", "c3", "c4"), show='headings')
    tree1.column("#1", anchor=tk.CENTER)
    tree1.heading("#1", text="Dev_Id")
    tree1.column("#2", anchor=tk.CENTER)
    tree1.heading("#2", text="Humidity")
    tree1.column("#3", anchor=tk.CENTER)
    tree1.heading("#3", text="Temperature")
    tree1.column("#4", anchor=tk.CENTER)
    tree1.heading("#4", text="Timestamp")
    for item in tree1.get_children():    
      tree.delete(item)
    tree1.pack(fill=tk.BOTH, expand=True)
    items = tree.get_children()
    
    for item in items:
        data = tree.item(item)['values']
        tree1.insert("", 0, value=data)


#Starting the initial windows and dividing in a 3x3 grid
window = tk.Tk()
window.state('zoomed')
window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=3)
window.title('Progetto di tesi')
frame_a = tk.Frame(master=window, padx=5, pady=5, background='#d3d3d3')
frame_b = tk.Frame(master=window, padx=5, pady=5, background='#d3d3d3')
frame_c = tk.Frame(master=window, padx=5, pady=5, background='#d3d3d3')
frame_d = tk.Frame(master=window, padx=5, pady=5, background='#d3d3d3')
frame_e = tk.Frame(master=window, padx=5, pady=5, background='#d3d3d3')
frame_f = tk.Frame(master=window, padx=5, pady=5, background='#d3d3d3')
frame_g = tk.Frame(master=window, padx=5, pady=5, background='#d3d3d3')
frame_h = tk.Frame(master=window, padx=5, pady=5, background='#d3d3d3')
frame_i = tk.Frame(master=window, padx=5, pady=5, background='#d3d3d3')

#Form to get the user wanted data
lbl_node = tk.Label(master=frame_a, 
                    text="Please select the sensor", 
                    fg="black",pady=10, background='#d3d3d3')
entry_sensor = ttk.Combobox(master=frame_a, values=nodes_name)

#Calendars to get the wanted period 
cal = Calendar(frame_g, year=2020, month=1, day=1, date_pattern="yy-mm-dd")
t_cal = tk.Text(frame_g, width=30, height=1, background='#d3d3d3', borderwidth=0)
t_cal.insert(1.0, "Initial date period: ")
t_cal.configure(state="disabled")
cal2 = Calendar(frame_b, year=2020, month=12, day=31, date_pattern="yy-mm-dd")
t_cal2 = tk.Text(frame_b, width=30, height=1, background='#d3d3d3', borderwidth=0)
t_cal2.insert(1.0, "Final date period: ")
t_cal2.configure(state="disabled")

#putting calendars into the grid
t_cal.grid(padx=1)
cal.grid(pady=1)
t_cal2.grid(padx=1)
cal2.grid(pady=1)


#button to fetch the data from the database
button = tk.Button(master=frame_a, 
                   text="Fetch the data!", 
                   width=15, 
                   height=1, 
                   bg="white", 
                   fg="black",
                   command=get_data,
                   background='#d3d3d3')

#button to zoom the output
zoom_btn = tk.Button(master=frame_a,
                    text="Zoom the output!", 
                    width=15, 
                    height=1, 
                    bg="white", 
                    fg="black",
                    command=zoom_output,
                    background='#d3d3d3')

#button to zoom the data tree
data_btn = tk.Button(master=frame_a,
                    text="Zoom the data!", 
                    width=15, 
                    height=1, 
                    bg="white", 
                    fg="black",
                    command=zoom_data,
                    background='#d3d3d3')

#Label to show the dss output
output=tk.Text(master=frame_h, width=50, height=17, background='#d3d3d3')
output.configure(font=("Arial"))
output.tag_configure("err", foreground="red")
output.tag_configure("warn", foreground="#f09900")
output.grid()

#table tree to show the data
tree = ttk.Treeview(frame_e, column=("c1", "c2", "c3", "c4"), show='headings')

tree.column("#1", anchor=tk.CENTER)
tree.heading("#1", text="Dev_Id")

tree.column("#2", anchor=tk.CENTER)
tree.heading("#2", text="Humidity")

tree.column("#3", anchor=tk.CENTER)
tree.heading("#3", text="Temperature")

tree.column("#4", anchor=tk.CENTER)
tree.heading("#4", text="Timestamp")

#creating the map and markers
lbl_map=tk.Label(master=frame_d, bg="white")
map_widget = tkm.TkinterMapView(lbl_map, width=450, height=300)

#initial point
map_widget.set_position(44.04188001643735, 11.37823570557368) 
map_widget.set_zoom(8)
#Sensori con problemi, akeb:70B3D5499E59EED5, cod:23782876348FE2F2, 1287481723817287, 218DADFADFADFADF

#Creazione dei marker dei sensori sulla mappa
for item in nodes:
    map_widget.set_marker(item['lat'], item['long'], text=item['name'])

# the figure that will contain the plot
fig = Figure(figsize = (4,3), dpi = 100)
fig.set_facecolor("#d3d3d3")
canvas = FigureCanvasTkAgg(fig, master = frame_c)
# placing the canvas on the Tkinter window
canvas.get_tk_widget().grid(pady=5)

pag = tk.Text(master=frame_f, width=20, height=10, background='#d3d3d3', borderwidth=0)
pag.insert(1.0, "Giacomo Domeniconi\nMatricola 295742\nUniversità di Parma")
pag.configure(state="disabled")
pag.grid()

#Setting the positions in the app window
lbl_node.grid(pady=1)
entry_sensor.grid(pady=5)

button.grid(pady=1)
zoom_btn.grid(pady=1)
data_btn.grid(pady=1)

tree.grid(pady=5, sticky="E")

lbl_map.grid(padx=1)
map_widget.pack()

frame_a.grid(row=0, column=0, sticky="NW")
frame_b.grid(row=0, column=2, sticky="NE")
frame_c.grid(row=1, column=0, sticky="NW")
frame_d.grid(row=1, column=2, sticky="NE")
frame_e.grid(row=2, column=0, sticky="NW", columnspan=3)
frame_f.grid(row=2, column=2, sticky="SE")
frame_g.grid(row=0, column=1, sticky="NE")
frame_h.grid(row=1, column=1, sticky="NE")
frame_i.grid(row=2, column=1, sticky="N")

window['bg'] = '#d3d3d3'
window.mainloop()
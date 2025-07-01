import serial
import time
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import filedialog
import threading
import cv2
import platform
import serial.tools.list_ports

THIRTY_SECONDS = 30
PROGRAM_NAME = "Programa de Conexión Serial e iteraciones"
CANT_VALUES = 10
INPUTS_X = []
INPUTS_Y = []
INPUTS_Z = []  # Lista para almacenar valores Z

ORIGEN_CORRDINATES = "G92 X0 Y0 Z0"
ORIGIN_ABSOLUTE_POSITION = "G90"
SERIAL = serial.Serial()
WINDOWS_MAIN = tk.Tk()
WINDOWS_MAIN.title(PROGRAM_NAME)
STOP_THREAD = False
BLUE = "blue"
RED = "red"
GREEN = "Green"
EMPTY = ""

# Inicialización de cámara según sistema operativo
if platform.system() == 'Windows':
    CAM = cv2.VideoCapture(0, cv2.CAP_DSHOW)
else:
    CAM = cv2.VideoCapture(0)

CAM.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
CAM.set(cv2.CAP_PROP_FRAME_HEIGHT, 768)

width = int(CAM.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(CAM.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"Resolución real: {width}x{height}")

SAVE_FOLDER = ""

def grbl_startup_correctly():
    grbl_answer = SERIAL.readline().strip().decode('utf-8')
    log("GRBL answer: " + grbl_answer)
    return grbl_answer.find("Grbl") != -1

def obtain_thirty_seconds_later():
    current_time = time.time()
    return current_time + THIRTY_SECONDS

def yes_thirty_seconds_passed(thirty_seconds_later):
    time.sleep(0.1)
    current_time = time.time()
    return current_time >= thirty_seconds_later

def not_thirty_seconds_passed(thirty_seconds_later):
    return not yes_thirty_seconds_passed(thirty_seconds_later)

def load_connection_parameters():
    SERIAL.baudrate = baud_select.get()
    SERIAL.port = port_select.get()
    SERIAL.timeout = 15
    log("Port: " + port_select.get())
    log("Baud: " + baud_select.get())

def check_if_grbl_starts_correctly():
    thirty_seconds_later = obtain_thirty_seconds_later()
    while not_thirty_seconds_passed(thirty_seconds_later):
        if (grbl_startup_correctly()):
            return
    log("Error starting GRBL")
    raise Exception("Error starting GRBL")

def the_execution_of_the_command_ended():
    SERIAL.write(b"?")
    grbl_answer = SERIAL.readline().strip().decode('utf-8')
    return grbl_answer.find("Idle") != -1

def check_if_the_execution_of_the_command_finished():
    thirty_seconds_later = obtain_thirty_seconds_later()
    while not_thirty_seconds_passed(thirty_seconds_later):
        if the_execution_of_the_command_ended():
            return
    log_color("Error when executing command", RED)
    raise Exception("Error when executing command")

def check_if_the_command_sent_is_correct():
    grbl_answer = SERIAL.readline().strip().decode('utf-8')
    if grbl_answer != "ok":
        log_color("Grbl command error", RED)
        raise Exception("Grbl command error")

def open_connection():
    try:
        log("Starting connection ...")
        load_connection_parameters()
        SERIAL.open()
        check_if_grbl_starts_correctly()
        log_color("Successful connection", GREEN)
        define_origin_coordinates()
    except Exception as e:
        log("Connection error: " + str(e))

def thread_open_connection():
    thread = threading.Thread(target=open_connection)
    thread.start()

def close_connection():
    SERIAL.close()
    log_color("Connection closed", GREEN)

def grbl_send_command(command):
    log("Command: " + command)
    command_whit_n = command + "\n"
    SERIAL.write(command_whit_n.encode())
    check_if_the_command_sent_is_correct()
    check_if_the_execution_of_the_command_finished()

def grbl_send_command_color(command, color):
    log_color("Command: " + command, color)
    SERIAL.write(command.encode())
    check_if_the_command_sent_is_correct()
    check_if_the_execution_of_the_command_finished()

def stop_grbl():
    global STOP_THREAD
    STOP_THREAD = True
    log_color("Stopped the process.", GREEN)

def log(text):
    if text:
        text_area.config(state=tk.NORMAL)
        text_area.insert(tk.END, "\n" + text + "\n")
        text_area.config(state=tk.DISABLED)
        text_area.see(tk.END)
        text_area.update_idletasks()
        time.sleep(0.1)

def log_color(text, color):
    if text:
        text_area.config(state=tk.NORMAL)
        text_area.insert(tk.END, "\n" + text + "\n", color)
        text_area.config(state=tk.DISABLED)
        text_area.see(tk.END)
        text_area.update_idletasks()
        time.sleep(0.1)

def select_save_folder():
    global SAVE_FOLDER
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        SAVE_FOLDER = folder_selected
        log_color(f"Save Photos: {SAVE_FOLDER}", BLUE)

def define_origin_coordinates():
    log("Sets the current coordinate point, used to set an origin point of zero, commonly known as the home position.")
    grbl_send_command(ORIGEN_CORRDINATES)
    log("All distances and positions are Absolute values from the current origin.")
    grbl_send_command(ORIGIN_ABSOLUTE_POSITION)

def is_in_allowed_range(value):
    return value > -100 and value < 100

def is_float(value):
    try:
        float(value)
        return True
    except Exception as e:
        return False

def is_not_float(value):
    return not is_float(value)

def is_empty(value):
    return value == EMPTY

def is_not_in_allowed_range(value):
    return not is_in_allowed_range(value)

def there_are_empty(index):
    return is_empty(INPUTS_X[index].get()) or is_empty(INPUTS_Y[index].get()) or is_empty(INPUTS_Z[index].get())

def there_are_not_float(index):
    return is_not_float(INPUTS_X[index].get()) or is_not_float(INPUTS_Y[index].get()) or is_not_float(INPUTS_Z[index].get())

def there_are_not_in_allowed_range(index):
    value_x = float(INPUTS_X[index].get())
    value_y = float(INPUTS_Y[index].get())
    value_z = float(INPUTS_Z[index].get())
    return is_not_in_allowed_range(value_x) or is_not_in_allowed_range(value_y) or is_not_in_allowed_range(value_z)

def is_int(value):
    try:
        int(value)
        return True
    except Exception as e:
        return False

def is_not_int(value):
    return not is_int(value)

def is_positive(value):
    value = int(value)
    return value >= 0

def is_not_positive(value):
    return not is_positive(value)

def is_not_waiting_time_valid(value):
    return is_not_float(value) or is_not_positive(value)

def is_not_iteration_valid(value):
    return is_not_int(value) or is_not_positive(value)

def is_data_valid():
    if is_not_waiting_time_valid(input_waiting_time.get()):
        log_color("Is not waiting time valid", RED)
        return False

    if is_not_iteration_valid(input_iterations.get()):
        log_color("Is not iteration valid", RED)
        return False

    for i in range(CANT_VALUES):
        if there_are_empty(i):
            log_color("Values should not be empty", RED)
            return False
        if there_are_not_float(i):
            log_color("They should only be numerical values", RED)
            return False
        if there_are_not_in_allowed_range(i):
            log_color("The x and y values must at least be between 100 and -100", RED)
            return False
    return True

def is_not_data_valid():
    return not is_data_valid()

def build_command_x(value):
    return "G0 X" + value + " F10"

def build_command_y(value):
    return "G0 Y" + value + " F10"

def build_command_z(value):
    return "G0 Z" + value + " F10"

def to_position_start():
    log("Go to pa starting position")
    command_x = build_command_x(INPUTS_X[0].get())
    command_y = build_command_y(INPUTS_Y[0].get())
    grbl_send_command(command_x)
    if STOP_THREAD:
        return
    grbl_send_command(command_y)
    log("Go to pa starting position ok")
    time.sleep(float(input_waiting_time.get()))

def grbl_send_commands_xyz(j):
    command_x = build_command_x(INPUTS_X[j].get())
    command_y = build_command_y(INPUTS_Y[j].get())
    command_z = build_command_z(INPUTS_Z[j].get())
    grbl_send_command(command_x)
    if STOP_THREAD:
        return
    grbl_send_command(command_y)
    if STOP_THREAD:
        return
    grbl_send_command(command_z)

def start_iterations():
    for i in range(int(input_iterations.get())):
        if STOP_THREAD:
            break
        for j in range(CANT_VALUES):
            if STOP_THREAD:
                break
            log(f"Iteración: {i+1} Subiterción: {j+1}")
            grbl_send_commands_xyz(j)
            name_file = f"I{i+1}S{j+1}.jpg"
            take_photo(name_file)
            time.sleep(float(input_waiting_time.get()))
    to_position_start()
    if not STOP_THREAD:
        log_color("Process completed successfully", BLUE)

def thread_start_iterations():
    global STOP_THREAD
    if is_not_data_valid():
        return
    STOP_THREAD = False
    thread = threading.Thread(target=start_iterations)
    thread.start()

def take_photo(name_file):
    global SAVE_FOLDER
    ret, fotograma = CAM.read()
    if ret:
        if SAVE_FOLDER:  # Si se seleccionó una carpeta
            name_file = f"{SAVE_FOLDER}/{name_file}"  # Guardar en la carpeta seleccionada
        cv2.imwrite(name_file, fotograma)
        log_color(f"¡Foto guardada como: {name_file}", BLUE)
    else:
        log_color("Error al capturar la foto.", RED)

def show_capture():
    if not CAM.isOpened():
        print("Error: No se pudo abrir la cámara.")
        return

    while True:
        ret, frame = CAM.read()
        if not ret:
            print("Error: No se pudo capturar el fotograma.")
            break

        (h, w) = frame.shape[:2]
        new_width = 1024
        ratio = new_width / float(w)
        new_height = int(h * ratio)

        framegrande = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

        cv2.imshow('Captura de cámara', framegrande)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    CAM.release()
    cv2.destroyAllWindows()

def close_camera():
    if CAM.isOpened():
        CAM.release()
    cv2.destroyAllWindows()

def thread_show_capture():
    thread = threading.Thread(target=show_capture)
    thread.start()

thread_show_capture()

tk.Label(WINDOWS_MAIN, text="Port:").grid(row=0, column=0)

# Lista automática de puertos disponibles según sistema operativo
ports = serial.tools.list_ports.comports()
available_ports = [port.device for port in ports]

port_select = ttk.Combobox(WINDOWS_MAIN, values=available_ports)
port_select.grid(row=0, column=1, pady=3)
if available_ports:
    port_select.current(0)  # Selecciona el primer puerto disponible

tk.Label(WINDOWS_MAIN, text="Baud:").grid(row=1, column=0)
baud_select = ttk.Combobox(WINDOWS_MAIN,
                           values=["2400", "4800", "9600", "19200", "38400", "57600", "115200", "230400", "250000"])
baud_select.grid(row=1, column=1, pady=3)
baud_select.current(6)

btn_connection = tk.Button(WINDOWS_MAIN, text="Connect", command=thread_open_connection)
btn_connection.grid(row=2, column=0, columnspan=1)

btn_close_connection = tk.Button(WINDOWS_MAIN, text="Disconnect", command=close_connection)
btn_close_connection.grid(row=2, column=1, columnspan=1)

btn_select_folder = tk.Button(WINDOWS_MAIN, text="Save Photo", command=select_save_folder)
btn_select_folder.grid(column=0, row=0, padx=10, pady=10)

WINDOWS_MAIN.protocol("WM_DELETE_WINDOW", lambda: [close_camera(), WINDOWS_MAIN.quit()])

for i in range(CANT_VALUES):
    tk.Label(WINDOWS_MAIN, text=f"x{i + 1}:").grid(row=i, column=2)
    input_x = tk.Entry(WINDOWS_MAIN)
    input_x.grid(row=i, column=3, padx=10, pady=3)
    INPUTS_X.append(input_x)

for i in range(CANT_VALUES):
    tk.Label(WINDOWS_MAIN, text=f"y{i + 1}:").grid(row=i, column=4)
    input_y = tk.Entry(WINDOWS_MAIN)
    input_y.grid(row=i, column=5, padx=10, pady=3)
    INPUTS_Y.append(input_y)

for i in range(CANT_VALUES):
    tk.Label(WINDOWS_MAIN, text=f"z{i+1}:").grid(row=i, column=6)
    input_z = tk.Entry(WINDOWS_MAIN)
    input_z.grid(row=i, column=7, padx=10, pady=3)
    INPUTS_Z.append(input_z)

tk.Label(WINDOWS_MAIN, text="Iterations").grid(row=3, column=0)
input_iterations = tk.Entry(WINDOWS_MAIN)
input_iterations.grid(row=3, column=1)

tk.Label(WINDOWS_MAIN, text="Waiting time(s)").grid(row=4, column=0)
input_waiting_time = tk.Entry(WINDOWS_MAIN)
input_waiting_time.grid(row=4, column=1)

btn_start = tk.Button(WINDOWS_MAIN, text="START", command=thread_start_iterations)
btn_start.grid(row=5, column=0, columnspan=1)

btn_stop = tk.Button(WINDOWS_MAIN, text="STOP", command=stop_grbl)
btn_stop.grid(row=5, column=1, columnspan=1)

text_area = scrolledtext.ScrolledText(WINDOWS_MAIN, height=20, state=tk.DISABLED)
text_area.grid(row=18, column=0, columnspan=6, padx=10, pady=10)
text_area.tag_config(BLUE, foreground=BLUE)
text_area.tag_config(RED, foreground=RED)
text_area.tag_config(GREEN, foreground=GREEN)

WINDOWS_MAIN.mainloop()



#########################################################################################
# import serial, time
# import tkinter as tk
# from tkinter import ttk
# from tkinter import scrolledtext
# from tkinter import filedialog
# import threading
# import cv2
# import serial

# THIRTY_SECONDS = 30
# PROGRAM_NAME = "Programa de Conexión Serial e iteraciones"
# CANT_VALUES = 10
# INPUTS_X = []
# INPUTS_Y = []

# INPUTS_Z = []  # Lista para almacenar valores Z

# ORIGEN_CORRDINATES = "G92 X0 Y0 Z0"
# ORIGIN_ABSOLUTE_POSITION = "G90"
# SERIAL = serial.Serial()
# WINDOWS_MAIN = tk.Tk()
# WINDOWS_MAIN.title(PROGRAM_NAME)
# STOP_THREAD = False
# BLUE = "blue"
# RED = "red"
# GREEN = "Green"
# EMPTY = ""

# # CAM = cv2.VideoCapture(0)

# CAM = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# CAM.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
# CAM.set(cv2.CAP_PROP_FRAME_HEIGHT, 768)

# width = int(CAM.get(cv2.CAP_PROP_FRAME_WIDTH))
# height = int(CAM.get(cv2.CAP_PROP_FRAME_HEIGHT))
# print(f"Resolución real: {width}x{height}")

# # # Verificar la resolución real que se está usando
# # print(f"Resolución real de la cámara: {CAM.get(cv2.CAP_PROP_FRAME_WIDTH)}x{CAM.get(cv2.CAP_PROP_FRAME_HEIGHT)}")

# SAVE_FOLDER = ""

# def grbl_startup_correctly():
#     grbl_answer = SERIAL.readline().strip().decode('utf-8')
#     log("GRBL answer: " + grbl_answer)
#     return grbl_answer.find("Grbl") != -1


# def obtain_thirty_seconds_later():
#     current_time = time.time()
#     return current_time + THIRTY_SECONDS


# def yes_thirty_seconds_passed(thirty_seconds_later):
#     time.sleep(0.1)
#     current_time = time.time()
#     return current_time >= thirty_seconds_later


# def not_thirty_seconds_passed(thirty_seconds_later):
#     return not yes_thirty_seconds_passed(thirty_seconds_later)


# def load_connection_parameters():
#     SERIAL.baudrate = baud_select.get()
#     SERIAL.port = port_select.get()
#     SERIAL.timeout = 15
#     log("Port: " + port_select.get())
#     log("Baud: " + baud_select.get())


# def check_if_grbl_starts_correctly():
#     thirty_seconds_later = obtain_thirty_seconds_later()
#     while not_thirty_seconds_passed(thirty_seconds_later):
#         if (grbl_startup_correctly()):
#             return
#     log("Error starting GRBL")
#     raise Exception("Error starting GRBL")


# def the_execution_of_the_command_ended():
#     SERIAL.write(b"?")
#     grbl_answer = SERIAL.readline().strip().decode('utf-8')
#     return grbl_answer.find("Idle") != -1


# def check_if_the_execution_of_the_command_finished():
#     thirty_seconds_later = obtain_thirty_seconds_later()
#     while not_thirty_seconds_passed(thirty_seconds_later):
#         if the_execution_of_the_command_ended():
#             return
#     log_color("Error when executing command", RED)
#     raise Exception("Error when executing command")


# def check_if_the_command_sent_is_correct():
#     grbl_answer = SERIAL.readline().strip().decode('utf-8')
#     if grbl_answer != "ok":
#         log_color("Grbl command error", RED)
#         raise Exception("Grbl command error")


# def open_connection():
#     try:
#         log("Starting connection ...")
#         load_connection_parameters()
#         SERIAL.open()
#         check_if_grbl_starts_correctly()
#         log_color("Successful connection", GREEN)
#         define_origin_coordinates()
#     except Exception as e:
#         log("Connection error: " + str(e))


# def thread_open_connection():
#     thread = threading.Thread(target=open_connection)
#     thread.start()


# def close_connection():
#     SERIAL.close()
#     log_color("Connection closed", GREEN)


# def grbl_send_command(command):
#     log("Command: " + command)
#     command_whit_n = command + "\n"
#     SERIAL.write(command_whit_n.encode())
#     check_if_the_command_sent_is_correct()
#     check_if_the_execution_of_the_command_finished()


# def grbl_send_command_color(command, color):
#     log_color("Command: " + command, color)
#     SERIAL.write(command.encode())
#     check_if_the_command_sent_is_correct()
#     check_if_the_execution_of_the_command_finished()


# def stop_grbl():
#     global STOP_THREAD
#     STOP_THREAD = True
#     log_color("Stopped the process.", GREEN)


# def log(text):
#     if text:
#         text_area.config(state=tk.NORMAL)
#         text_area.insert(tk.END, "\n" + text + "\n")
#         text_area.config(state=tk.DISABLED)
#         text_area.see(tk.END)
#         text_area.update_idletasks()
#         time.sleep(0.1)


# def log_color(text, color):
#     if text:
#         text_area.config(state=tk.NORMAL)
#         text_area.insert(tk.END, "\n" + text + "\n", color)
#         text_area.config(state=tk.DISABLED)
#         text_area.see(tk.END)
#         text_area.update_idletasks()
#         time.sleep(0.1)


# def select_save_folder():
#     global SAVE_FOLDER
#     folder_selected = filedialog.askdirectory()
#     if folder_selected:
#         SAVE_FOLDER = folder_selected
#         log_color(f"Save Photos: {SAVE_FOLDER}", BLUE)



# def define_origin_coordinates():
#     log("Sets the current coordinate point, used to set an origin point of zero, commonly known as the home position.")
#     grbl_send_command(ORIGEN_CORRDINATES)
#     log("All distances and positions are Absolute values from the current origin.")
#     grbl_send_command(ORIGIN_ABSOLUTE_POSITION)


# def is_in_allowed_range(value):
#     return value > -100 and value < 100


# def is_float(value):
#     try:
#         float(value)
#         return True
#     except Exception as e:
#         return False


# def is_not_float(value):
#     return not is_float(value)


# def is_empty(value):
#     return value == EMPTY


# def is_not_in_allowed_range(value):
#     return not is_in_allowed_range(value)


# def there_are_empty(index):
#     return is_empty(INPUTS_X[index].get()) or is_empty(INPUTS_Y[index].get()) or is_empty(INPUTS_Z[index].get())

# def there_are_not_float(index):
#     return is_not_float(INPUTS_X[index].get()) or is_not_float(INPUTS_Y[index].get()) or is_not_float(INPUTS_Z[index].get())

# def there_are_not_in_allowed_range(index):
#     value_x = float(INPUTS_X[index].get())
#     value_y = float(INPUTS_Y[index].get())
#     value_z = float(INPUTS_Z[index].get())
#     return is_not_in_allowed_range(value_x) or is_not_in_allowed_range(value_y) or is_not_in_allowed_range(value_z)


# def is_int(value):
#     try:
#         int(value)
#         return True
#     except Exception as e:
#         return False


# def is_not_int(value):
#     return not is_int(value)


# def is_positive(value):
#     value = int(value)
#     return value >= 0


# def is_not_positive(value):
#     return not is_positive(value)


# def is_not_waiting_time_valid(value):
#     return is_not_float(value) or is_not_positive(value)


# def is_not_iteration_valid(value):
#     return is_not_int(value) or is_not_positive(value)


# def is_data_valid():
#     if is_not_waiting_time_valid(input_waiting_time.get()):
#         log_color("Is not waiting time valid", RED)
#         return False

#     if is_not_iteration_valid(input_iterations.get()):
#         log_color("Is not iteration valid", RED)
#         return False

#     for i in range(CANT_VALUES):
#         if there_are_empty(i):
#             log_color("Values should not be empty", RED)
#             return False
#         if there_are_not_float(i):
#             log_color("They should only be numerical values", RED)
#             return False
#         if there_are_not_in_allowed_range(i):
#             log_color("The x and y values must at least be between 100 and -100", RED)
#             return False
#     return True


# def is_not_data_valid():
#     return not is_data_valid()


# def build_command_x(value):
#     return "G0 X" + value + " F10"


# def build_command_y(value):
#     return "G0 Y" + value + " F10"


# def build_command_z(value):
#     return "G0 Z" + value + " F10"

# def to_position_start():
#     log("Go to pa starting position")
#     command_x = build_command_x(INPUTS_X[0].get())
#     command_y = build_command_y(INPUTS_Y[0].get())
#     grbl_send_command(command_x)
#     if STOP_THREAD:
#         return
#     grbl_send_command(command_y)
#     log("Go to pa starting position ok")
#     time.sleep(float(input_waiting_time.get()))


# def grbl_send_commands_xyz(j):
#     command_x = build_command_x(INPUTS_X[j].get())
#     command_y = build_command_y(INPUTS_Y[j].get())
#     command_z = build_command_z(INPUTS_Z[j].get())
#     grbl_send_command(command_x)
#     if STOP_THREAD:
#         return
#     grbl_send_command(command_y)
#     if STOP_THREAD:
#         return
#     grbl_send_command(command_z)



# def start_iterations():
#     for i in range(int(input_iterations.get())):
#         if STOP_THREAD:
#             break
#         for j in range(CANT_VALUES):
#             if STOP_THREAD:
#                 break
#             log(f"Iteración: {i+1} Subiterción: {j+1}")
#             grbl_send_commands_xyz(j)
#             name_file = f"I{i+1}S{j+1}.jpg"
#             take_photo(name_file)
#             time.sleep(float(input_waiting_time.get()))
#     to_position_start()
#     if not STOP_THREAD:
#         log_color("Process completed successfully", BLUE)

# def thread_start_iterations():
#     global STOP_THREAD
#     if is_not_data_valid():
#         return
#     STOP_THREAD = False
#     thread = threading.Thread(target=start_iterations)
#     thread.start()


# # def take_photo(name_file):
# #     ret, fotograma = CAM.read()
# #
# #     if ret:
# #         cv2.imwrite(name_file, fotograma)
# #         log_color("¡Foto guardada como:" + name_file, BLUE)
# #     else:
# #         log_color("Error al capturar la foto.", RED)


# def take_photo(name_file):
#     global SAVE_FOLDER
#     ret, fotograma = CAM.read()
#     if ret:
#         if SAVE_FOLDER:  # Si se seleccionó una carpeta
#             name_file = f"{SAVE_FOLDER}/{name_file}"  # Guardar en la carpeta seleccionada
#         cv2.imwrite(name_file, fotograma)
#         log_color(f"¡Foto guardada como: {name_file}", BLUE)
#     else:
#         log_color("Error al capturar la foto.", RED)


# def show_capture():
#     if not CAM.isOpened():
#         print("Error: No se pudo abrir la cámara.")
#         return

#     while True:
#         ret, frame = CAM.read()
#         if not ret:
#             print("Error: No se pudo capturar el fotograma.")
#             break

#         # Obtener dimensiones originales
#         (h, w) = frame.shape[:2]
#         new_width = 1024  # Ancho deseado
#         ratio = new_width / float(w)
#         new_height = int(h * ratio)  # Mantener la proporción

#         # Redimensionar manteniendo la relación de aspecto
#         framegrande = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

#         # Mostrar el fotograma
#         cv2.imshow('Captura de cámara', framegrande)

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     CAM.release()
#     cv2.destroyAllWindows()



# # def show_capture():
# #     if not CAM.isOpened():
# #         print("Error: No se pudo abrir la cámara.")
# #         return
# #
# #     # Bucle para capturar y mostrar fotogramas de la cámara
# #     while True:
# #         # Capturar fotograma de la cámara
# #         ret, frame = CAM.read()
# #
# #         # Comprobar si el fotograma se capturó correctamente
# #         if not ret:
# #             print("Error: No se pudo capturar el fotograma.")
# #             break
# #
# #         # Escalarla cuatro veces
# #         # framegrande = cv2.resize(frame, None, fx=4, fy=4, interpolation=cv2.INTER_LINEAR) # TEST 1
# #
# #         framegrande = cv2.resize(frame, (1024, 768), interpolation=cv2.INTER_LINEAR)  # Test 2
# #
# #         # Mostrar el fotograma en una ventana
# #         cv2.imshow('Captura de cámara', framegrande)
# #
# #         # Esperar a que se presione la tecla 'q' para salir del bucle
# #         if cv2.waitKey(1) & 0xFF == ord('q'):
# #             break
# #
# #     # Liberar la cámara y cerrar todas las ventanas
# #     CAM.release()
# #     cv2.destroyAllWindows()

# #################################################################################3

# # Agregado
# #
# def close_camera():
#     if CAM.isOpened():
#         CAM.release()
#     cv2.destroyAllWindows()


# #######################################################################
# def thread_show_capture():
#     thread = threading.Thread(target=show_capture)
#     thread.start()


# thread_show_capture()

# tk.Label(WINDOWS_MAIN, text="Port:").grid(row=0, column=0)
# port_select = ttk.Combobox(WINDOWS_MAIN,
#                            values=["COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "COM10",
#                                    "COM11"])
# port_select.grid(row=0, column=1, pady=3)
# port_select.current(3)

# tk.Label(WINDOWS_MAIN, text="Baud:").grid(row=1, column=0)
# baud_select = ttk.Combobox(WINDOWS_MAIN,
#                            values=["2400", "4800", "9600", "19200", "38400", "57600", "115200", "230400", "250000"])
# baud_select.grid(row=1, column=1, pady=3)
# baud_select.current(6)

# btn_connection = tk.Button(WINDOWS_MAIN, text="Connect", command=thread_open_connection)
# btn_connection.grid(row=2, column=0, columnspan=1)

# btn_close_connection = tk.Button(WINDOWS_MAIN, text="Disconnect", command=close_connection)
# btn_close_connection.grid(row=2, column=1, columnspan=1)


# btn_select_folder = tk.Button(WINDOWS_MAIN, text="Save Photo", command=select_save_folder)
# btn_select_folder.grid(column=0, row=0, padx=10, pady=10)

# #################################################################################################
# # Agregado
# WINDOWS_MAIN.protocol("WM_DELETE_WINDOW", lambda: [close_camera(), WINDOWS_MAIN.quit()])

# ###########################################################################################

# #########################################################################################

# for i in range(CANT_VALUES):
#     tk.Label(WINDOWS_MAIN, text=f"x{i + 1}:").grid(row=i, column=2)
#     input_x = tk.Entry(WINDOWS_MAIN)
#     input_x.grid(row=i, column=3, padx=10, pady=3)
#     INPUTS_X.append(input_x)

# for i in range(CANT_VALUES):
#     tk.Label(WINDOWS_MAIN, text=f"y{i + 1}:").grid(row=i, column=4)
#     input_y = tk.Entry(WINDOWS_MAIN)
#     input_y.grid(row=i, column=5, padx=10, pady=3)
#     INPUTS_Y.append(input_y)

# for i in range(CANT_VALUES):
#     tk.Label(WINDOWS_MAIN, text=f"z{i+1}:").grid(row=i, column=6)
#     input_z = tk.Entry(WINDOWS_MAIN)
#     input_z.grid(row=i, column=7, padx=10, pady=3)
#     INPUTS_Z.append(input_z)

# tk.Label(WINDOWS_MAIN, text="Iterations").grid(row=3, column=0)
# input_iterations = tk.Entry(WINDOWS_MAIN)
# input_iterations.grid(row=3, column=1)

# tk.Label(WINDOWS_MAIN, text="Waiting time(s)").grid(row=4, column=0)
# input_waiting_time = tk.Entry(WINDOWS_MAIN)
# input_waiting_time.grid(row=4, column=1)

# btn_start = tk.Button(WINDOWS_MAIN, text="START", command=thread_start_iterations)
# btn_start.grid(row=5, column=0, columnspan=1)

# btn_stop = tk.Button(WINDOWS_MAIN, text="STOP", command=stop_grbl)
# btn_stop.grid(row=5, column=1, columnspan=1)

# text_area = scrolledtext.ScrolledText(WINDOWS_MAIN, height=20, state=tk.DISABLED)
# text_area.grid(row=18, column=0, columnspan=6, padx=10, pady=10)
# text_area.tag_config(BLUE, foreground=BLUE)
# text_area.tag_config(RED, foreground=RED)
# text_area.tag_config(GREEN, foreground=GREEN)

# WINDOWS_MAIN.mainloop()


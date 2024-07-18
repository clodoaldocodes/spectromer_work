# %%
import seabreeze.spectrometers as sb
import matplotlib.pyplot as plt
import numpy as np
import datetime
import os
import RPi.GPIO as GPIO
import time
import os


def measure_target(spec):
    wavelengths = spec.wavelengths()
    spectrum = spec.intensities()

    return wavelengths, spectrum


def realize_measure(aux, i_integration):

    print(f"{aux} measure - Begin\n")

    aux_time = str(datetime.datetime.now())
    GPIO.output(21, True)

    background_values = []
    for j in range(0, 10):
        print(f"Measurement number {j}\n")
        txt_output = aux + "_" + str(j) + "_" + aux_time + ".txt"
        wavelengths_background, spectrum_background = measure_target(spec)
        time.sleep(time_delay)

        with open(output + txt_output, "w") as f:
            f.write(f"Time used to integration {i_integration} ms\n")
            f.write("Wavelengths, Spectrum\n")
            for k in range(np.size(wavelengths_background, axis=0)):
                f.write(f"{wavelengths_background[k]}, {spectrum_background[k]}\n")

        if j == 0:
            background_values = spectrum_background
        else:
            background_values = np.column_stack(
                (background_values, spectrum_background)
            )

    spectrum_background = np.mean(background_values, axis=1)
    print(f"{aux} measure - Finished\n")
    GPIO.output(21, False)
    return spectrum_background


GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)

GPIO.add_event_detect(14, GPIO.RISING)
GPIO.add_event_detect(15, GPIO.RISING)
GPIO.add_event_detect(18, GPIO.RISING)
GPIO.add_event_detect(26, GPIO.RISING)

GPIO.output(21, False)
GPIO.output(20, False)

# Change ---------------------------------------------------------------
i = 5
time_delay = 3
output_basic = "/home/pi/spectromer_work/measurements/"
time_now = str(datetime.datetime.now())
name = f"aquisition_{time_now}/"
output = f"{output_basic}{name}"
if not os.path.exists(output):
    os.makedirs(output)
    print(f"A pasta {output} foi criada.")
# ----------------------------------------------------------------------

# Encontrar e inicializar o espectrômetro
devices = sb.list_devices()
if not devices:
    GPIO.output(20, True)
    print("Nenhum espectrômetro encontrado.")
    time.sleep(time_delay)
    GPIO.output(21, True)
    GPIO.cleanup()
    exit()

GPIO.output(21, True)
time.sleep(2)
GPIO.output(21, False)

print(
    "O que deseja fazer?\n0 - Referência do alvo escuro\n1-Referência do alvo branco\n2 - Medição real\n9 - Sair do processo\n"
)

aux_a14 = False
aux_a15 = False

while i < 8:
    a14 = GPIO.event_detected(14)
    a15 = GPIO.event_detected(15)
    a18 = GPIO.event_detected(18)
    a26 = GPIO.event_detected(26)

    time.sleep(1)

    if a18:
        aux = "Normal"
        print(f"{aux} measure - Begin\n")
        aux_time = str(datetime.datetime.now())
        GPIO.output(21, True)

        for j in range(0, 10):
            print(f"Measurement number {j}\n")

            spec = sb.Spectrometer(devices[0])
            for i_integration in range(10000, 500000, 10000):
                print(i_integration)
                spec.integration_time_micros(i_integration)

                wavelengths, spectrum = measure_target(spec)

                txt_output = (
                    "bg_spectrum_"
                    + str(j)
                    + "_"
                    + aux_time
                    + "integration_time_"
                    + str(i_integration)
                    + ".txt"
                )
                with open(output + txt_output, "w") as f:
                    f.write(f"Time used to integration {i_integration} ms\n")
                    f.write("Wavelengths, Spectrum\n")
                    for k in range(np.size(spectrum, axis=0)):
                        f.write(f"{wavelengths[k]}, {spectrum[k]}\n")

        time.sleep(time_delay)
        print(f"{aux} measure - Finished\n")
        GPIO.output(21, False)

    if a26:
        print("Shutdown\n")
        i = 10
        for r in range(0, 3):
            GPIO.output(20, True)
            time.sleep(1)
            GPIO.output(20, False)
            time.sleep(1)

# Desconectar o espectrômetro
GPIO.cleanup()
spec.close()

os.system("shutdown -h now")

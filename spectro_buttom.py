#%%
import seabreeze.spectrometers as sb
import matplotlib.pyplot as plt
import numpy as np
import datetime
import os
import RPi.GPIO as GPIO
import time

def measure_target(spec):
    wavelengths = spec.wavelengths()
    spectrum = spec.intensities()

    return wavelengths, spectrum

def find_optimal_integration_time(spec):
    spectrum = spec.intensities()
    k_value = 6115.781236274194 * 0.85
    if abs(np.max(spectrum) - k_value) <= 1:
        optimal_find = True
    else:
        optimal_find = False
    return optimal_find

# Encontrar e inicializar o espectrômetro
devices = sb.list_devices()
if not devices:
    print("Nenhum espectrômetro encontrado.")
    exit()

'''
spec = sb.Spectrometer(devices[0])
for i_integration in range(1000, 655350000, 1000):
    print(i_integration)
    spec.integration_time_micros(i_integration)  # Ajustar o tempo de integração conforme necessário
    optimal_find = find_optimal_integration_time(spec)
    if optimal_find == True:
        break

spec.integration_time_micros(i_integration)
'''
i_integration = 2000
spec = sb.Spectrometer(devices[0])
spec.integration_time_micros(i_integration)

output = "/home/pi/spectromer_work/measurements/"

if not os.path.isdir(output):
    os.makedirs(output)

GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(21, GPIO.OUT)

GPIO.add_event_detect(14,GPIO.RISING)
GPIO.add_event_detect(15,GPIO.RISING)
GPIO.add_event_detect(18,GPIO.RISING)

i = 5
time_delay = 3

print("O que deseja fazer?\n0 - Referência do alvo escuro\n1-Referência do alvo branco\n2 - Medição real\n9 - Sair do processo\n")
GPIO.output(21, False)

while i < 8:
    a14 = GPIO.event_detected(14)
    a15 = GPIO.event_detected(15)
    a18 = GPIO.event_detected(18)

    time.sleep(1)

    if a14:
        aux = "Background"
        print(f"{aux} measure - Begin\n")
        GPIO.output(21, True)
        wavelengths_background, spectrum_background = measure_target(spec)
        time.sleep(time_delay)
        print(f"{aux} measure - Finished\n")
        GPIO.output(21, False)
    if a15:
        aux = "Ref"
        print(f"{aux} measure - Begin\n")
        GPIO.output(21, True)
        wavelengths_ref, spectrum_ref = measure_target(spec)
        time.sleep(time_delay)
        print(f"{aux} measure - Finished\n")
        GPIO.output(21, False)
    if a18:
        aux = "Normal"
        print(f"{aux} measure - Begin\n")
        aux_time = str(datetime.datetime.now())

        for j in range(0, 10):
            txt_output = "spectrum_" + str(j) + "_" + aux_time + "txt"
            print(f"Measurement number {j}\n")

            GPIO.output(21, True)
            wavelengths, spectrum = measure_target(spec)

            k_op = 1e2
            op1 = spectrum_ref - spectrum_background
            op2 = spectrum - spectrum_background
            op3 = op2/op1
            op4 = k_op*op3
            op5 = op4/np.max(op4)

            plt.plot(wavelengths, op5)
            plt.xlabel("Wavelength (nm)")
            plt.ylabel("Reflection (%)")
            plt.savefig("foo.png")

            with open(output + txt_output, "w") as f:
                f.write(f"Time used to integration {i_integration} ms")
                f.write("Wavelengths, Spectrum\n")
                for k in range(np.size(op5, axis=0)):
                    f.write(f"{wavelengths[k]}, {op5[k]}\n")

        time.sleep(time_delay)
        print(f"{aux} measure - Finished\n")
        GPIO.output(21, False)

# Desconectar o espectrômetro
GPIO.cleanup()
spec.close()

# %%

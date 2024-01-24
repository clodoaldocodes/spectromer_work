#%%
import seabreeze.spectrometers as sb
import matplotlib.pyplot as plt
import numpy as np
import datetime
import os
from gpiozero import LED, Button

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

spec = sb.Spectrometer(devices[0])
for i_integration in range(1000, 655350000, 1000):
    print(i_integration)
    spec.integration_time_micros(i_integration)  # Ajustar o tempo de integração conforme necessário
    optimal_find = find_optimal_integration_time(spec)
    if optimal_find == True:
        break

spec.integration_time_micros(i_integration)

output = "/home/pi/spectrometer/measurements/"
txt_output = "spectrum_" + str(datetime.datetime.now()) + "txt"

if not os.path.isdir(output):
    os.makedirs(output)

button_background = Button(14)
button_ref = Button(15)

i = 5
while i < 8:
    input_aux = input("O que deseja fazer?\n0 - Referência do alvo escuro\n1-Referência do alvo branco\n2 - Medição real\n9 - Sair do processo\n")
    i = int(input_aux)
    if i == 0:
        wavelengths_background, spectrum_background = measure_target(spec)
    if i == 1:
        wavelengths_ref, spectrum_ref = measure_target(spec)
    if i == 2:
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
            f.write("wavelengths, spectrum\n")
            for k in range(np.size(op5, axis=0)):
                f.write(f"{wavelengths[k]}, {op5[k]}\n")

# Desconectar o espectrômetro
spec.close()

# %%

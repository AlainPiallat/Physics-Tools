# This file is part of Physics-Tools.
# Licensed under the Apache License, Version 2.0.
# See LICENSE file or http://www.apache.org/licenses/LICENSE-2.0 for details.

# RC Circuit timer with Op-Amp
# This program calculates the necessary resistances (R1, R2, R3) based on a given duration and capacitance,
# using the E24 series to minimize the time deviation.
# It explores all possible values of R3 and searches for the best R1, R2 pair,
# minimizing the time deviation from the desired duration.
# It uses a graphical interface with Tkinter to input values and display the result.

import tkinter as tk
import math

# E24 series of standardized resistances (with multipliers)
E24_base = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
            3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1]
E24 = sorted([x * (10**exp) for exp in range(2,5) for x in E24_base])

def find_nearest_E24(value):
    """Finds the closest value in the E24 series."""
    return min(E24, key=lambda x: abs(x - value))

def calculate():
    try:
        T = float(entry_T.get())
        C = int(entry_C.get()) * (10**-6)
        
        best_R1, best_R2, best_R3 = None, None, None
        min_deviation = float('inf')
        
        for R3 in E24:
            # Calculate the Vthreshold/Vcc ratio based on R3, C, and charge time (during capacitor charging)
            ratio_Vthreshold_Vcc = math.exp(-T / (R3 * C))

            # Ensure the Vthreshold/Vcc ratio remains within practical limits
            if ratio_Vthreshold_Vcc < 0.01 or ratio_Vthreshold_Vcc > 0.99:
                continue
            
            # Calculate the R1 and R2 resistances of the voltage divider from the Vcc/Vthreshold ratio
            for R1 in E24:
                if 1000 <= R1 <= 10000:
                    R2_calc = R1 * (1 - ratio_Vthreshold_Vcc) / ratio_Vthreshold_Vcc
                    R2 = find_nearest_E24(R2_calc)
                    
                    # Calculate the obtained ratio with R1 and R2
                    obtained_ratio = R2 / (R1 + R2)

                    # Calculate the optimal R3 resistance with the new ratio
                    R3_calc = -T / (C * math.log(obtained_ratio))
                    R3_calc_E24 = find_nearest_E24(R3_calc)

                    # Calculate the obtained time with R3
                    T_obtained = -math.log(obtained_ratio) * R3_calc_E24 * C

                    # Check if the ratio is optimal
                    deviation = abs(T_obtained - T)
                    
                    if deviation < min_deviation:
                        min_deviation = deviation
                        best_R1, best_R2, best_R3 = R1, R2, R3_calc_E24

        # Best result:
        obtained_ratio = best_R2 / (best_R1 + best_R2)
        T_obtained = -math.log(obtained_ratio) * best_R3 * C
        deviation = abs(T_obtained - T)

        print(f"Calculated Time: {T_obtained:.6f} s | Ratio: {obtained_ratio:.6f} | R1: {best_R1} Ω | R2: {best_R2} Ω | R3: {best_R3} Ω | C: {int(entry_C.get())} | Deviation: {deviation:.6f} s")

        result.set(f"R1 = {best_R1} Ω\nR2 = {best_R2} Ω\nR3 = {best_R3} Ω\nTime Deviation = {min_deviation:.6f} s")
    except ValueError:
        result.set("Error: Check your values")

def reset():
    """Resets input fields and clears the result."""
    entry_T.delete(0, tk.END)
    entry_C.delete(0, tk.END)
    result.set("")

# Graphical Interface
root = tk.Tk()
root.title("RC Resistance Calculator (E24)")

tk.Label(root, text="Duration (s):").grid(row=0, column=0)
entry_T = tk.Entry(root)
entry_T.grid(row=0, column=1)

tk.Label(root, text="Capacitance (uF):").grid(row=1, column=0)
entry_C = tk.Entry(root)
entry_C.grid(row=1, column=1)

result = tk.StringVar()
tk.Label(root, textvariable=result).grid(row=4, columnspan=2)

tk.Button(root, text="Calculate", command=calculate).grid(row=5, column=0)
tk.Button(root, text="Reset", command=reset).grid(row=5, column=1)

root.mainloop()

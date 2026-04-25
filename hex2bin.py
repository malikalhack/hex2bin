#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
********************************************************************************
 * @file    hex2bin.py
 * @version 0.2.0
 * @author  Anton Chernov
 * @date    04/24/2026
 * @brief   Hex/Dec to Binary Converter (32-bit) with GUI
 *
********************************************************************************
"""

############################ Импорт модулей ####################################
import sys
import tkinter as tk
from tkinter import ttk

################################################################################
#                              Версия приложения                               #
################################################################################

APP_VERSION = "0.2.0"

def get_version() -> str:
    """Return the application version string."""
    return APP_VERSION

def validate_py_version() -> bool:
    """
    @brief  Check that the interpreter meets the minimum version requirement.

    @return True if Python >= 3.8, False otherwise.
    """
    bool_result = True
    major_version = sys.version_info.major
    minor_version = sys.version_info.minor
    if not (major_version == 3 and minor_version >= 8):
        print("Python 3.8 or higher is required.")
        print(f"You are using Python {major_version}.{minor_version}")
        bool_result = False
    return bool_result


################################################################################
#                         Класс Hex2Bin Converter                              #
################################################################################

class Hex2BinConverter:
    """
    @brief  Main GUI class for the 32-bit Hex/Dec to Binary converter.

    @details Provides interactive editing of a 32-bit unsigned integer via:
             - Individual bit checkboxes (bits 31..0, arranged in four rows)
             - Hexadecimal entry field (prefix '0x' accepted)
             - Decimal entry field
             - Arithmetic/shift buttons: +, -, <<, >>
             All controls stay synchronised on every change.
    """

    def __init__(self, root):
        """
        @brief  Initialize the main application window.

        @param[in]  root  Tkinter root window object.
        """
        self.root = root
        self.root.title("Hex2Bin Converter - 32 bit")
        self.root.geometry("720x180")
        self.root.resizable(False, False)

        self.value = 0
        self.checkvar_list = []

        # Главный контейнер
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Левая панель - биты
        left_frame = ttk.LabelFrame(
            main_frame,
            text="32-bit значение",
            padding="10"
        )
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Строка с битами (31-24)
        bits_frame1 = ttk.Frame(left_frame)
        bits_frame1.pack(fill=tk.X, pady=2)
        for i in range(31, 23, -1):
            self.create_bit_checkbox(bits_frame1, i)

        # Строка с битами (23-16)
        bits_frame2 = ttk.Frame(left_frame)
        bits_frame2.pack(fill=tk.X, pady=2)
        for i in range(23, 15, -1):
            self.create_bit_checkbox(bits_frame2, i)

        # Строка с битами (15-8)
        bits_frame3 = ttk.Frame(left_frame)
        bits_frame3.pack(fill=tk.X, pady=2)
        for i in range(15, 7, -1):
            self.create_bit_checkbox(bits_frame3, i)

        # Строка с битами (7-0)
        bits_frame4 = ttk.Frame(left_frame)
        bits_frame4.pack(fill=tk.X, pady=2)
        for i in range(7, -1, -1):
            self.create_bit_checkbox(bits_frame4, i)

        # Правая панель - управление и отображение
        right_frame = ttk.LabelFrame(
            main_frame,
            text="Управление",
            padding="15"
        )
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5)

        # Поле HEX
        ttk.Label(right_frame, text="HEX:").grid(
            row=0,
            column=0,
            sticky=tk.W,
            pady=5
        )
        self.hex_var = tk.StringVar(value="0x00000000")
        self.hex_entry = ttk.Entry(
            right_frame,
            textvariable=self.hex_var,
            width=15
        )
        self.hex_entry.grid(row=0, column=1, sticky=tk.EW, padx=10)
        self.hex_entry.bind('<Return>',   lambda e: self.set_from_hex_entry())
        self.hex_entry.bind('<KP_Enter>', lambda e: self.set_from_hex_entry())

        # Поле DEC
        ttk.Label(right_frame, text="DEC:").grid(
            row=1,
            column=0,
            sticky=tk.W,
            pady=5
        )
        self.dec_var = tk.StringVar(value="0")
        self.dec_entry = ttk.Entry(
            right_frame,
            textvariable=self.dec_var,
            width=15
        )
        self.dec_entry.grid(row=1, column=1, sticky=tk.EW, padx=10)
        self.dec_entry.bind('<Return>',   lambda e: self.set_from_dec_entry())
        self.dec_entry.bind('<KP_Enter>', lambda e: self.set_from_dec_entry())

        # Разделитель
        ttk.Separator(right_frame, orient=tk.HORIZONTAL).grid(
            row=2, column=0, columnspan=2, sticky=tk.EW, pady=10)

        # Кнопки управления
        btn_frame = ttk.Frame(right_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, sticky=tk.EW)

        ttk.Button(
            btn_frame,
            text="+",
            width=6,
            command=self.increment
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            btn_frame,
            text="-",
            width=6,
            command=self.decrement
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            btn_frame,
            text="<<",
            width=6,
            command=self.shift_left
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            btn_frame,
            text=">>",
            width=6,
            command=self.shift_right
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            btn_frame,
            text="~",
            width=6,
            command=self.invert
        ).pack(side=tk.LEFT, padx=2)

        right_frame.columnconfigure(1, weight=1)

        self.update_display()

    def create_bit_checkbox(self, parent, bit_pos):
        """
        @brief  Create a labelled checkbox for a single bit position.

        @param[in]  parent   Parent Tkinter widget (frame row).
        @param[in]  bit_pos  Bit position in the 32-bit value (0..31).
        """
        var = tk.BooleanVar()
        self.checkvar_list.append((bit_pos, var))

        def on_bit_change():
            self.update_from_bits()

        cb = ttk.Checkbutton(parent, text=str(bit_pos), variable=var,
                             command=on_bit_change, width=3)
        cb.pack(side=tk.LEFT, padx=2)

    def update_display(self):
        """
        @brief  Synchronise all UI controls from the internal value.

        @details Updates the HEX entry, DEC entry, and all bit checkboxes
                 to reflect the current value of ``self.value``.
        """
        pass

    def update_from_bits(self):
        """
        @brief  Rebuild the internal value from the checkbox states and refresh.
        """
        self.value = 0
        self.update_display()

    def increment(self):
        """
        @brief  Increment the current value by 1 (wraps at 2^32).
        """
        self.value = (self.value + 1) & 0xFFFFFFFF
        self.update_display()

    def decrement(self):
        """
        @brief  Decrement the current value by 1 (wraps at 0).
        """
        self.value = (self.value - 1) & 0xFFFFFFFF
        self.update_display()

    def shift_left(self):
        """
        @brief  Shift the current value left by 1 bit (MSB is discarded).
        """
        self.value = (self.value << 1) & 0xFFFFFFFF
        self.update_display()

    def shift_right(self):
        """
        @brief  Shift the current value right by 1 bit (logical shift).
        """
        self.value = (self.value >> 1) & 0xFFFFFFFF
        self.update_display()

    def invert(self):
        """
        @brief  Bitwise-invert all 32 bits of the current value.
        """
        self.value = (~self.value) & 0xFFFFFFFF
        self.update_display()

    def set_from_hex_entry(self):
        """
        @brief  Parse the HEX entry field and update the internal value.
        """
        pass

    def set_from_dec_entry(self):
        """
        @brief  Parse the DEC entry field and update the internal value.

        @details Restores the previous DEC text on parse error.
        """
        pass


################################################################################
#                              Точка входа                                     #
################################################################################

def main():
    """
    @brief  Application entry point.

    @details Creates the Tkinter root window, instantiates Hex2BinConverter
             and starts the GUI event loop.
    """
    if not validate_py_version():
        sys.exit(1)
    root = tk.Tk()
    app = Hex2BinConverter(root)
    root.mainloop()


if __name__ == "__main__":
    main()

################################################################################
#                          Конец файла hex2bin.py                              #
################################################################################

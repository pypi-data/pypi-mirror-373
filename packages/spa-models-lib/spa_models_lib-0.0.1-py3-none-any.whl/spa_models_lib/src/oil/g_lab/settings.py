# -*- coding: utf-8 -*-
import sys

PATH = sys.path[0]
probability_limit = 0.01
# если внутри дня вероятность превышения 0.5 то считаем сигнал валидным
sensetive_for_pi_data = 0.5

#% специальный символ отделения для split т.к для этих значений ожна функция проверки с разными условиями
to_rename_input = {
    'Viscosity40': 'Кинематическая вязкость при 40 °С',
    'Viscosity100': 'Кинематическая вязкость, при 100°C',
    'ViscosityIndex': 'Кинематическая вязкость',
    'TAN': 'Кислотное число',
    'Density20': 'Плотность при 20 °С',
    'FlashPoint': 'Температура вспышки',
    'Color': 'Цвет на колориметре',
    'Corrosiveness': 'Коррозионность',
    'Zn': 'Цинк (Zn)',
    'Water': 'Вода',
    'Operating_time': 'наработка масла',
    'Al': 'Алюминий',
    'Ca': 'Кальций',
    'Cr': 'Хром',
    'Cu': 'Медь',
    'Fe': 'Железо',
    'Pb': 'Свинец',
    'Na': 'натрий (Na)',
    'Ni': 'никель (Ni)',
    'P': 'фосфор (P)',
    'Pb': 'свинец (Pb)',
    'S': 'сера (S)',
    'Si': 'кремний (Si)',
    'Sn': 'олово (Sn)',
    'Ti': 'титан (Ti)',
    'V': 'ванадий (V)',
    'Zn': 'цинк (Zn)',
    'K': 'Калий (K)',
    'Ag': 'Серебро (Ag)',
}

to_rename_input1 = {
    'Water': 'water',
    'Soot': 'soot',
    'Oxidation': 'oxidation',
    'Nitration': 'nitration',
    'Sulfation': 'sulfation',
    'Fuel': 'fuel',
    'Glycol': 'glycol',
    'Operating_time': 'operating_time',
    'Total_operating_time': 'total_operating_time',
}
to_rename_output = {
    'Viscosity40': 'вязкость при 40 °С (Viscosity40)',
    'Viscosity_index': 'индекс вязкости (Viscosity_index)',
    'nitration': 'продукты нитрификации (nitration)',
    'oxidation': 'продукты окисления (oxidation)',
    'sulfatisation': 'продукты сульфатирования (sulfatisation)',
    'flash_point': 'температура вспышки (flash_point)',
    'TAN': 'кислотное число (TAN)',
    'fuel': 'содержание горючего (fuel)',
    'glycol': 'содержание гликоля (glycol)',
    'water': 'вода (water)',
    'soot': 'сажа (soot)',
    'Ag': 'серебро (Ag)',
    'Al': 'алюминий (Al)',
    'B': 'бор (B)',
    'Ba': 'барий (Ba)',
    'Ca': 'кальций (Ca)',
    'Cd': 'кадмий (Cd)',
    'Cr': 'хром (Cr)',
    'Cu': 'медь (Cu)',
    'Fe': 'железо (Fe)',
    'K': 'калий (K)',
    'Mg': 'магний (Mg)',
    'Mn': 'марганец (Mn)',
    'Mo': 'молибден (Mo)',
    'Na': 'натрий (Na)',
    'Ni': 'никель (Ni)',
    'P': 'фосфор (P)',
    'Pb': 'свинец (Pb)',
    'S': 'сера (S)',
    'Si': 'кремний (Si)',
    'Sn': 'олово (Sn)',
    'Ti': 'титан (Ti)',
    'V': 'ванадий (V)',
    'Zn': 'цинк (Zn)',
    'operating_time': 'наработка (operating time)',
    'total_operating_time': 'общая наработка (total operating time)',
}

#% специальный символ отделения для split т.к для этих значений ожна функция проверки с разными условиями
to_rename_limits = {
    'Viscosity40': 'Viscosity40',
    'TAN': 'TAN',
    'Zn': 'Zn',
    'Water': 'Water',
    'Density20': 'Density20',
    'FlashPoint': 'FlashPoint',
    'Corrosiveness': 'Corrosiveness',
    'Color': 'Color',
    'P1': 'Давление масла%P1',
    'P2': 'Давление масла%P2',
    'P4': 'Давление масла%P4',
    'T1': 'Температура подшипника Вала Компрессора%1',
    'T2': 'Температура подшипника Вала Компрессора%2',
    'T3': 'Температура подшипника Вала Компрессора%3',
    'T4': 'Температура подшипника Вала Компрессора%4',
}

string_fields = ['OilName', 'ViscType', 'OilType', 'UnitName', 'UnitType']

names = {
    'TAN': 'Кислотное число',
    'nitration': 'Степень нитрирования',
    'sulfatisation': 'Содержание сульфатов',
    'oxidation': 'Степерь окисления',
    'Pb': 'Содержание свинца',
}

# не интерпретируемый параметр
parameter_list_not_interp = ['timestamp']

# для прогноза
parameter_list = ['Viscosity40', 'Water', 'FlashPoint', 'Density20', 'Zn', 'Oxidation']

parameter_list_not_predict = ['Corrosiveness', 'timestamp']

graphics_parameter_list = ['Viscosity40', 'Water', 'FlashPoint', 'Density20', 'Color', 'TAN', 'Zn']

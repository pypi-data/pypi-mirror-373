# -*- coding: utf-8 -*-
import json
import logging as logger
import os

from .settings import to_rename_limits


class InputConverter:
    def __init__(self, dir_path, file_constructor):
        logger.info('Запущен модуль конвертации систем измерения проб')
        self.file_constructor = file_constructor
        self.dir_path = dir_path
        if len(self.dir_path) > 0:
            self.dir_path = self.dir_path + '/'
        self.converter = {}
        self.file_connector()
        if self:
            self.samples = self.json_iterator()
            self.input = self.prepare_input()
        if hasattr(self, 'limits_dict'):
            self.limits = self.prepare_limits()

    def json_reader(self, file_instance, set_obj):
        try:
            with open(file_instance, encoding='utf-8') as file:
                setattr(InputConverter, set_obj, json.loads(file.read()))
        except OSError as exp:
            import sys

            logger.info(f'Модуль конвертации систем измерения проб завершил работу с ошибкой\n{exp}')
            sys.exit()

    def file_connector(self):
        for file_type, file_name in self.file_constructor.items():
            if os.path.exists(os.path.join(self.dir_path, file_name)):
                self.json_reader(file_instance=os.path.join(self.dir_path, file_name), set_obj=file_type)

        if hasattr(self, 'converter_rules'):
            self.converter_reference()

    def converter_reference(self):
        for converter_rule in self.converter_rules['units_convert']:
            self.converter[converter_rule['source']] = {'to': converter_rule['target'], 'coef': converter_rule['coef']}

    def json_iterator(self):
        if bool(self.converter):
            for sample in self.samples['samples']:
                for param in sample['params']:
                    unit_mapping = self.converter.get(param['units'])
                    if unit_mapping is not None:
                        param['value'] *= unit_mapping['coef']
                        param['units'] = unit_mapping['to']
            logger.info('Модуль конвертации систем измерения проб успешно завершил работу')
        else:
            logger.info(
                'Из-за отсутствия файла настройки конвертации систем измерения, конвертация не произведена! Единицы измерения оставлены как есть.'
            )
        return self.samples

    def prepare_input(self):
        result_dict = {}
        all_params = []
        print(self.samples['samples'])
        for n, sample in enumerate(self.samples['samples']):
            sample_data = []
            result_dict['OilName'] = result_dict.get('OilName', []) + [self.samples['oil']['name']]
            result_dict['ViscType'] = result_dict.get('ViscType', []) + [self.samples['oil']['visc']]
            result_dict['OilType'] = result_dict.get('OilType', []) + [self.samples['oil']['type']]
            result_dict['UnitName'] = result_dict.get('UnitName', []) + [self.samples['unit']['name']]
            result_dict['UnitType'] = result_dict.get('UnitType', []) + [self.samples['unit']['type']]
            ttime = sample['timestamp'].split('.')[0].split(' ')[0]   # удалим милисекунд и часы

            for param in sample['params']:
                all_params.append(param['name'])
                all_params = list(set(all_params))
                value = param['value']
                if type(value) is str:
                    if value.replace('.', '').isdigit():
                        value = float(value)
                if param['name'] not in sample_data:
                    sample_data.append(param['name'])
                    result_dict[param['name']] = result_dict.get(param['name'], [] if n == 0 else [None] * n) + [value]
            result_dict['timestamp'] = result_dict.get('timestamp', []) + [ttime]
            for param in set(all_params) - set([p['name'] for p in sample['params']]):
                result_dict[param] = result_dict.get(param, [] if n == 0 else [None] * n) + [None]

            for key in list(result_dict.keys()):
                if all(True if i is None else False for i in result_dict[key]):
                    del result_dict[key]

        return result_dict

    def prepare_limits(self):
        result_dict = {}
        for name in self.limits_dict['limits']:
            if name['indicator'] in to_rename_limits:
                name['indicator'] = to_rename_limits.get(name['indicator'])
            else:
                logger.error(f"Отсутствует корректный словарь для Лимитов по параметру {name['indicator']}")
        for limit in self.limits_dict['limits']:
            # if result_dict.get(limit['indicator']) is None:
            if (limit['zone_red'] is not None) and (limit['zone_red'] != ''):
                result_dict[limit['indicator']] = limit['zone_red']
        # else:
        #       logger.info('В файле с лимитами параметр {} повторяется несколько раз. Использовано первое встретившееся значение'.format(limit['indicator']))
        return result_dict


if __name__ == '__main__':
    import sys

    formatter = logger.Formatter('[%(asctime)s] %(filename)s:%(lineno)d %(levelname)-8s %(message)s')
    stdout_handler = logger.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    handlers = [stdout_handler]
    logger.basicConfig(handlers=handlers, level=logger.INFO)
    logger.info('Program started')

    inst = InputConverter('.\\data')
    print(inst.input)
    print(inst.limits)

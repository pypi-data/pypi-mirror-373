#!/usr/bin/env python3

import argparse
import os
import sys
import qrcode # pip install qrcode[pil]

# Инфо о программе
__version__ = "1.0.1"
__year__ = "2025-08-31"
__about__ = "Created by EPluribusNEO"
_appname = "qrc"
_license ="MIT License"


def read_file(filepath):
	"""Чтение содержимого файла"""
	if not os.path.exists(filepath):
		print(f"[ERROR] Ошибка: файл '{filepath}' не найден.")
		sys.exit(1)
	try:
		with open(filepath, 'r', encoding='utf-8') as f:
			content = f.read().strip()
		if not content:
			print("[WARNING] Файл пуст.")
			sys.exit(1)
		return content
	except Exception as e:
		print(f"[ERROR] Ошибка при чтении файла: {e}")
		sys.exit(1)


def generate_qr_terminal(data):
	"""Вывод QR-кода в терминал"""
	print("[DONE] QR-код в терминале:")
	qr = qrcode.QRCode(
		version=1,
		error_correction=qrcode.constants.ERROR_CORRECT_L,
		box_size=1,
		border=4,
	)
	qr.add_data(data)
	qr.make(fit=True)
	qr.print_ascii(invert=True)


def generate_qr_image(data, output_path):
	"""Создание и сохранение QR-кода как PNG"""
	qr = qrcode.QRCode(
		version=1,
		error_correction=qrcode.constants.ERROR_CORRECT_H,
		box_size=10,
		border=4,
	)
	qr.add_data(data)
	qr.make(fit=True)
	img = qr.make_image(fill_color="black", back_color="white")
	try:
		img.save(output_path)
		print(f"[OK] QR-код сохранён: {output_path}")
	except Exception as e:
		print(f"[ERROR] Не удалось сохранить изображение: {e}")
		sys.exit(1)


def main():
	parser = argparse.ArgumentParser(
		prog=_appname,
		description="Преобразует текст (из файла или строки) в QR-код. "
		            "Поддерживает вывод в терминал и сохранение в PNG.",
		epilog=f"Примеры:\n"
		       f"  {_appname} -i 'Hello' -t              # Вывод в терминал\n"
		       f"  {_appname} document.txt -o             # Сохранить как document.png\n"
		       f"  {_appname} -i 'Hi' -o qr.png -t        # И в файл, и в терминал\n"
		       f"  {_appname} -v                          # Показать версию",
		formatter_class=argparse.RawDescriptionHelpFormatter  # Чтобы переносы в epilog работали
	)

	# Добавляем версию
	parser.add_argument(
		'-v', '--version',
		action='version',
		version=f'%(prog)s {__version__}\n{__about__}\n{_license}\n{__year__}'
	)

	# Группа: либо файл, либо текст
	group = parser.add_mutually_exclusive_group(required=False)
	group.add_argument('filepath', nargs='?', help='Путь к .txt файлу (опционально, если используется -i)')
	group.add_argument('-i', '--input', type=str, help='Текст для кодирования в QR-код')

	# Выходные параметры
	parser.add_argument(
		'-o', '--output',
		nargs='?', const=True, default=None,
		help='Сохранить QR как PNG. Без имени — рядом с файлом или как qrcode.png. '
		     'С именем — по указанному пути.'
	)
	parser.add_argument(
		'-t', '--terminal',
		action='store_true',
		help='Вывести QR-код в терминал'
	)

	# Проверяем, если нет аргументов вообще — показываем help
	if len(sys.argv) == 1:
		parser.print_help()
		sys.exit(0)

	args = parser.parse_args()

	# Проверяем, что хотя бы один источник указан
	if args.input is None and args.filepath is None:
		print("[ERROR] Не указан ни текст (-i), ни файл. Используй -h для справки.")
		parser.print_usage()
		sys.exit(1)

	# Определяем источник данных
	if args.input is not None:
		data = args.input.strip()
		if not data:
			print("[WARNING]️ Текст пустой.")
			sys.exit(1)
	else:
		data = read_file(args.filepath)

	# Определяем, выводить ли в терминал
	should_print = args.terminal or (args.output is None)

	if should_print:
		generate_qr_terminal(data)

	# Сохранение в PNG
	if args.output is not None:
		if args.output is True:
			# Автоимя
			if args.input is not None:
				output_path = "qrcode.png"
			else:
				base = os.path.splitext(args.filepath)[0]
				output_path = base + '.png'
		else:
			output_path = args.output

		generate_qr_image(data, output_path)


if __name__ == "__main__":
	main()

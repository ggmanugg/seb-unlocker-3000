import gzip
import zlib
import rncryptor  # https://github.com/RNCryptor/RNCryptor
import tempfile
from pathlib import Path
import os
import logging
import PySimpleGUI as sg

class RNCryptor_modified(rncryptor.RNCryptor):
	def post_decrypt_data(self, data):
		data = data[:-(data[-1])]
		return data

def main():
	sg.theme('Default 1')

	layout = [[sg.Text('SEB Unlocker 3000', font=('Arial Fett Kursiv', 20), justification='right')],

			[sg.Text('SEB Konfigurationsdatei', size=(18, 1)), sg.Input(key='-sourcefile-', size=(45, 1)),
			sg.FileBrowse(file_types=(("SEB Configuration File", "*.seb"),), size=(8, 1))],

			[sg.Text('SEB Start-Passwort', size=(18, 1)), sg.Input(key='-password-', size=(25, 1))],

			[sg.Frame('Output', font=('Arial Fett', 10), layout=[[sg.Output(size=(75, 10), font=('Arial', 10))]])],
			
			[sg.Button('Unlock SEB', button_color=('white', 'green'), bind_return_key=True, size=(10, 1)), sg.Button('Beenden', button_color=('white', 'red'), size=(10, 1))]]

	window = sg.Window('SEB Unlocker 3000', layout, finalize=True)
	# ---===--- Loop taking in user input --- #
	while True:

		event, values = window.read()
		if event in ('Exit', 'Beenden', None):
			break

		source_file = values['-sourcefile-']
		password = values['-password-']

		print("SEB Configuration File:\n" + source_file)
		print("SEB Start-Passwort:\n" + password)
		print("")

		if event == 'Unlock SEB':
			while True:
				print("Start unlocking SEB Configuration File")

				tmp_file = tempfile.NamedTemporaryFile()

				print("Decrypting SEB Configuration File")
				if not decrypt_SEB(password, source_file, tmp_file):
					break

				print("Recrypting SEB Configuration File")
				if not recrypt_SEB(password, source_file, tmp_file):
					break
				
				tmp_file.close()
				print("**** DONE ****")
				break


def decrypt_SEB(password, source_file, tmp_file):
	cryptor = RNCryptor_modified()

	try:
		with gzip.open(source_file, 'rb') as f_source:
			file_content = f_source.read()
	except:
		print("ERROR: Konfigurationsdatei konnte nicht geladen werden")
		print(logging.exception(''))
		return False

	try:
		decrypted_data = cryptor.decrypt(file_content[4:], password)
	except:
		print("ERROR: Falsches SEB Start-Passwort")
		print(logging.exception(''))
		return False
		
	decompressed_data = zlib.decompress(decrypted_data,15 + 32)

	str_data = decompressed_data.decode("utf-8") 
	replaced_data = str_data.replace("<key>createNewDesktop</key>\n    <true/>\n  ", "<key>createNewDesktop</key>\n    <false/>\n  ")
	replaced_data = replaced_data.replace("<key>allowSwitchToApplications</key>\n    <false/>\n  ", "<key>allowSwitchToApplications</key>\n    <true/>\n  ")
	replaced_data = replaced_data.replace("<key>enableAppSwitcherCheck</key>\n    <true/>\n  ", "<key>enableAppSwitcherCheck</key>\n    <false/>\n  ")
	bytes_data = str.encode(replaced_data)

	path = tmp_file.name

	try:
		tmp_file.write(bytes_data)
		tmp_file.seek(0)
	except:
		print("ERROR: TMP Datei konnte nicht gespeichert werden")
		print(logging.exception(''))
	return True

def recrypt_SEB(password, source_file, tmp_file):
	cryptor = RNCryptor_modified()

	try:
		file_content = tmp_file.read()
	except:
		print("ERROR: TMP Datei konnte nicht geladen werden")
		print(logging.exception(''))

	compressed_sets = gzip.compress(file_content)
	recrypted_data = str.encode("pswd") + cryptor.encrypt(compressed_sets, password)

	compressed_data = gzip.compress(recrypted_data)

	path = uniquify(source_file)
	print("Datei gespeichert unter:\n" + path)
	with open(path, "wb") as f:
		f.write(compressed_data)
	return True


def uniquify(path):
	counter = 1
	filename, extension = os.path.splitext(path)
	filename = filename + '_new'
	path = filename + extension

	while os.path.exists(path):
		path = filename + "_new (" + str(counter) + ")" + extension
		counter += 1

	return path

main()
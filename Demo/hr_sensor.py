import serial
arduino = serial.Serial('/dev/ttyACM0', baudrate = 115200)

start_word = False
current_avg_bpm = 0.0
print("Initializing...")
while True:
	try:
		current_line = str(arduino.readline(), 'utf-8') # read line
		# if start_word == False:
		# 		if current_line[0:-2]==b'MAX30102':
		# 				start_word = True
		# 				print("Program Start")
		# 				continue
		# 		else:
		# 				continue
		if 'No finger?' in current_line:
			continue
		else:
			# print(current_line)
			new_avg_bpm = float(current_line.split(",")[2].split("=")[1])
			if new_avg_bpm != current_avg_bpm:
				current_avg_bpm = new_avg_bpm
				# print(current_line)
				print(f'Avg BPM: {current_avg_bpm}')
	except KeyboardInterrupt:
		break
	except TypeError:
		continue
	except IndexError:
		print("Trying...")
		continue


print("Exiting...")

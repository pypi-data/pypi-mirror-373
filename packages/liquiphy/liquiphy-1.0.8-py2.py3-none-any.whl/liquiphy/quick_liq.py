#  liquiphy/quick_liq.py
#
#  Copyright 2025 liyang <liyang@veronica>
#
import sys, logging, argparse
from threading import Event
from conn_jack import JackConnectionManager, JackConnectError
from liquiphy import LiquidSFZ

liq_name = None
conn_man = None
src_ports = []
dest_ports = []
ports_ready = Event()


def on_client_registration(client_name, action):
	global liq_name
	if client_name.startswith('liquidsfz'):
		liq_name = client_name


def on_port_registration(port, action):
	action = 'REGISTERED' if action else 'GONE'
	if port.name.startswith(liq_name + ':'):
		if port.is_input and port.is_midi:
			dest_ports.append(port)
			for sys_port in conn_man.physical_output_ports():
				if sys_port.is_midi:
					src_ports.append(sys_port)
					break
		elif port.is_output and port.is_audio:
			src_ports.append(port)
			for sys_port in conn_man.physical_input_ports():
				if sys_port.is_audio:
					dest_ports.append(sys_port)
	if len(src_ports) == 3:
		ports_ready.set()


def main():
	"""
	Entry point, defined so as to make it easy to reference from bin script.
	"""
	parser = argparse.ArgumentParser()
	parser.epilog = """
	Open an .sfz file with liquidsfz and automatically connect input / outputs.
	"""
	parser.add_argument('sfz', type = str, help = 'SFZ file to resample.')
	parser.add_argument("--verbose", "-v", action = "store_true",
		help = "Show more detailed debug information.")
	options = parser.parse_args()
	log_level = logging.DEBUG if options.verbose else logging.ERROR
	log_format = "[%(filename)24s:%(lineno)4d] %(levelname)-8s %(message)s"
	logging.basicConfig(level = log_level, format = log_format)

	global conn_man, ports_ready
	try:
		conn_man = JackConnectionManager()
	except JackConnectError:
		print('Could not connect to JACK server. Is it running?')
		return 1
	conn_man.on_client_registration(on_client_registration)
	conn_man.on_port_registration(on_port_registration)
	print(options.sfz)
	with LiquidSFZ(options.sfz) as liq:
		if errors := liq.stderr():
			print(errors)
		ports_ready.wait()
		for src_port, dest_port in zip(src_ports, dest_ports):
			conn_man.connect(src_port, dest_port)
			print(f"Connected {src_port} to {dest_port}")
		print('Press Enter to quit...')
		try:
			input()
		except KeyboardInterrupt:
			pass
		return 0


if __name__ == "__main__":
	main()

#  end liquiphy/quick_liq.py

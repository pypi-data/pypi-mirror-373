# liquiphy

A quick and dirty interface to the liquidsfz command-line using python's subprocess.

You must install liquidsfz first for this package to work. To install:

	$ git clone https://github.com/swesterfeld/liquidsfz.git

Follow the instructions found in the liquidsfz README to install.

## QuickStart Example

	from liquiphy import LiquidSFZ
	with LiquidSFZ(<path-to-sfz>) as liq:
		liq.noteon(0, 60, 80)
		sleep(1)
		liq.noteoff(0, 60)

If you need to get a reference to the constructed instance before starting the
liquidsfz subprocess, use the "defer_start" parameter in the constructor:

	with LiquidSFZ(<path-to-sfz>, defer_start = True) as liq:
		... do something first ...
		liq.start()
		... do regular stuff ...

## API

To see a list of available methods, do this:

	from liquiphy import LiquidSFZ
	with LiquidSFZ() as liquid:
		print(dir(liquid))

### liquidsfz help

All the commands which you can call on a LiquidSFZ instance mirror the
underlying "liquidsfz" command API. Calling "help" on the liquidsfz command
line produces the following table:

	quit                - quit liquidsfz

	load sfz_filename   - load sfz from filename
	allsoundoff         - stop all sounds
	reset               - system reset (stop all sounds, reset controllers)
	noteon chan key vel - start note
	noteoff chan key    - stop note
	cc chan ctrl value  - send controller event
	pitch_bend chan val - send pitch bend event (0 <= val <= 16383)
	gain value          - set gain (0 <= value <= 5)
	max_voices value    - set maximum number of voices
	max_cache_size size - set maximum cache size in MB
	preload_time time   - set preload time in ms
	keys                - show keys supported by the sfz
	switches            - show switches supported by the sfz
	ccs                 - show ccs supported by the sfz
	stats               - show voices/cache/cpu usage
	info                - show information
	voice_count         - print number of active synthesis voices
	sleep time_ms       - sleep for some milliseconds
	source filename     - load a file and execute each line as command
	echo text           - print text

Looking at the above table, we see that there is a command "cc", which sends a
controller event. The parameters are "chan, ctrl, value". Interpreting this as
a python method would produce this:

	def cc(self, chan, ctrl, value):
		"""
		send controller event
		"""

So calling this method would work like this:

	from liquiphy import LiquidSFZ
	with LiquidSFZ(<path-to-sfz>) as liq:
		liq.cc(0, 0x78, 0)

... which would send CC 0x78 (all sound off) to channel 0.

### Return values

For methods which print text, the text printed by liquidsfz is the return value
of the function.

	with LiquidSFZ(<path-to-sfz>) as liq:
		print(liq.ccs())

... which in the test I just ran produced the following text:

	ccs
	Supported Controls:
	 - CC #7 - Volume [ default 100 ]
	 - CC #10 - Pan [ default 64 ]

## quick-liq

Need to listen to an .sfz file without a lot of hassle? Call "quick-liq
<path-to-sfz>" from the command line, like so:

	$ quick-liq <path-to-sfz>

The above command loads the given .sfz file in a liquidsfz instance and
automatically connects the Jack MIDI input and Jack audio outputs to the first
available (physical) ports. So far, it's the quickest, easiest way I found to
listen to the sound of an .sfz without hassling with container apps or Jack
connections.

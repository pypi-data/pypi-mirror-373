#  liquiphy/test.py
#
#  Copyright 2025 liyang <liyang@veronica>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
"""
Does a quick test of the LiquidSFZ class API.
"""
import sys, logging
from pprint import pprint
from log_soso import log_error
from liquiphy import LiquidSFZ, UsageError

if __name__ == "__main__":
	log_format = "[%(filename)24s:%(lineno)4d] %(levelname)-8s %(message)s"
	logging.basicConfig(level = logging.DEBUG, format = log_format)

	with LiquidSFZ() as liquid:
		print('******** Attributes:')
		pprint([ att for att in dir(liquid) if att[0] != '_' ])
		print('******** Info:')
		print(liquid.info())
		print('******** Set max_voices to 8 ...')
		print(liquid.max_voices(8))
		print('******** Info:')
		print(liquid.info())

		try:
			print('******** Send bad command ...')
			liquid.bad_command()
		except AttributeError as e:
			log_error(e)

		try:
			print('******** Send bad argument ...')
			liquid.help('bad argument')
		except UsageError as e:
			log_error(e)

		try:
			print('******** Send incomplete arguments ...')
			liquid.gain()
		except UsageError as e:
			log_error(e)

#  end liquiphy/test.py

#!/usr/bin/env python3
# Update DVBV5 channel files, preserving previous video/audio PIDs for channels that were offline while scanning
# Copyright 2020  Simon Arlott
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import collections

def channel_key(channel, data):
	return (channel, data.get('DELIVERY_SYSTEM'), data.get('FREQUENCY'))

def parse(filename):
	def add_channel(channels, channel, data):
		if channel is not None:
			channels[channel_key(channel, data)] = data
		return (None, collections.OrderedDict())

	channels = collections.OrderedDict()

	with open(filename, "rt") as f:
		channel = None
		data = collections.OrderedDict()
		n = 1
		for line in f:
			line = line.rstrip()
			if line.startswith("["):
				channel = line[1:-1]
			elif not line:
				(channel, data) = add_channel(channels, channel, data)
			elif line.startswith("\t"):
				line = line[1:].split(" = ", 1)
				data[line[0]] = line[1]
			else:
				raise Exception(f"{filename}: invalid content on line {n}: {line!r}")
			n += 1

		(channel, data) = add_channel(channels, channel, data)

	return channels

def merge(previous, input):
	previous = parse(previous)
	output = parse(input)

	for channel, data in output.items():
		for value in ["VIDEO_PID", "AUDIO_PID"]:
			if value not in data and channel in previous and value in previous[channel]:
				data[value] = previous[channel][value]

	return output

def format(channels):
	output = []
	for channel, data in channels.items():
		output.append(f"[{channel[0]}]")
		for key, value in data.items():
			output.append(f"\t{key} = {value}")
		output.append("")
	output.append("")
	return "\n".join(output)

if __name__== "__main__":
	parser = argparse.ArgumentParser(description="Update DVBV5 channel files, preserving previous video/audio PIDs for channels that were offline while scanning")
	parser.add_argument("previous", metavar="PREVIOUS", type=str, help="previous file")
	parser.add_argument("input", metavar="INPUT", type=str, help="input file")
	parser.add_argument("output", metavar="OUTPUT", type=str, help="output file")
	args = parser.parse_args()

	output = format(merge(args.previous, args.input))
	with open(args.output, "wt") as f:
		f.write(output)

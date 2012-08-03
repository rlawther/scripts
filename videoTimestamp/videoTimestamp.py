#! /usr/bin/python

import subprocess
import datetime
import time
import copy
import argparse
import os

def parseCmdLine():
    parser = argparse.ArgumentParser(description='Encode timestamp into video file')
    parser.add_argument('inputFile', help='the input move file')
    parser.add_argument('outputFile', help='the output move file')
    parser.add_argument('--relativeTime', action='store_true', help='timestamp relative times')
    args = parser.parse_args()
    return args



def srtTimeFormat(delta):
    total_seconds = delta.total_seconds()
    s = int(total_seconds)
    (hours, remainder) = divmod(s, 3600)
    (minutes, seconds) = divmod(remainder, 60)
    millis = int((total_seconds - s) * 1000)

    return time.strftime('%02d:%02d:%02d,%03d' % (hours, minutes, seconds, millis))

def getMovieTimeInfo(file):
    output = subprocess.check_output(['ffprobe', file], stderr=subprocess.STDOUT)
    lines = output.split('\n')

    for line in lines:
        if line.find('creation_time') > 0:
            tokens = line.split()
            date_str = tokens[2]
            time_str = tokens[3]

    for line in lines:
        if line.find('Duration') > 0:
            tokens = line.split()
            duration_str = tokens[1].strip(',')

    print date_str, time_str, duration_str
    tokens = duration_str.split(':')
    h = int(tokens[0])
    m = int(tokens[1])
    s = float(tokens[2])
    duration_td = datetime.timedelta(hours=h, minutes=m, seconds=int(s), milliseconds=int((s-int(s))*1000))

    start_time = datetime.datetime.strptime('%s %s' % (date_str, time_str), '%Y-%m-%d %H:%M:%S')

    return (start_time, duration_td)

def writeSrtFile(filename, startTime, duration, relativeTime=False, relativeTo=None):
    f = open(filename, 'w')

    abstime = copy.copy(startTime)
    end_time = startTime + duration
    reltime = datetime.timedelta(seconds=0)

    print end_time

    index = 1
    almostSecond = datetime.timedelta(milliseconds=990)
    second = datetime.timedelta(seconds=1)
    while abstime < end_time:
        f.write('%d\n' % index)
        f.write('%s --> %s\n' % (srtTimeFormat(reltime), srtTimeFormat(reltime + almostSecond)))
        if relativeTime:
            f.write('%s\n\n' % reltime)
        else:
            f.write('%s\n\n' % abstime)

        reltime += second
        abstime += second
        index += 1

    f.close()

def encodeMovie(inputFilename, srtFilename, outputFilename):
    subprocess.call(['mencoder', '-oac', 'copy', '-ovc', 'xvid', '-xvidencopts', 'fixed_quant=3', '-sub', srtFilename, '-o', outputFilename, inputFilename])


if __name__ == '__main__':

    args = parseCmdLine()
    (path, ext) = os.path.splitext(args.inputFile)
    srtFile = path + '.srt'

    (startTime, duration) = getMovieTimeInfo(args.inputFile)

    print 'dt : ', startTime
    print 'dt : ', duration

    writeSrtFile(srtFile, startTime, duration, args.relativeTime)
    encodeMovie(args.inputFile, srtFile, args.outputFile)





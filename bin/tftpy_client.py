#!/usr/bin/env python

import sys, logging, os
from optparse import OptionParser
import tftpy

def main():
    usage=""
    parser = OptionParser(usage=usage)
    parser.add_option('-H',
                      '--host',
                      help='remote host or ip address')
    parser.add_option('-p',
                      '--port',
                      help='remote port to use (default: 69)',
                      default=69)
    parser.add_option('-f',
                      '--filename',
                      help='filename to fetch')
    parser.add_option('-b',
                      '--blocksize',
                      help='udp packet size to use (default: 512)',
                      default=512)
    parser.add_option('-o',
                      '--output',
                      help='output file (default: same as requested filename)')
    parser.add_option('-d',
                      '--debug',
                      action='store_true',
                      default=False,
                      help='upgrade logging from info to debug')
    parser.add_option('-q',
                      '--quiet',
                      action='store_true',
                      default=False,
                      help="downgrade logging from info to warning")
    parser.add_option('-t',
                      '--tsize',
                      action='store_true',
                      default=False,
                      help="ask client to send tsize option in download")
    options, args = parser.parse_args()
    if not options.host or not options.filename:
        sys.stderr.write("Both the --host and --filename options "
                         "are required.\n")
        parser.print_help()
        sys.exit(1)

    if options.debug and options.quiet:
        sys.stderr.write("The --debug and --quiet options are "
                         "mutually exclusive.\n")
        parser.print_help()
        sys.exit(1)

    if not options.output:
        options.output = os.path.basename(options.filename)

    class Progress(object):
        def __init__(self, out):
            self.progress = 0
            self.out = out
        def progresshook(self, pkt):
            if isinstance(pkt, tftpy.TftpPacketDAT):
                self.progress += len(pkt.data)
                self.out("Downloaded %d bytes" % self.progress)
            elif isinstance(pkt, tftpy.TftpPacketOACK):
                self.out("Received OACK, options are: %s" % pkt.options)
        
    if options.debug:
        tftpy.setLogLevel(logging.DEBUG)
    elif options.quiet:
        tftpy.setLogLevel(logging.WARNING)
    else:
        tftpy.setLogLevel(logging.INFO)

    progresshook = Progress(tftpy.logger.info).progresshook

    tftp_options = {}
    if options.blocksize:
        tftp_options['blksize'] = int(options.blocksize)
    if options.tsize:
        tftp_options['tsize'] = 1

    tclient = tftpy.TftpClient(options.host,
                               int(options.port),
                               tftp_options)

    tclient.download(options.filename,
                     options.output,
                     progresshook)

if __name__ == '__main__':
    main()

#
# Makefile rules for the ZeroMQInterface package
#
KEXT_NAME = zeromqinterface
KEXT_SOURCES = src/zmqgap.c

KEXT_CFLAGS = 
KEXT_LDFLAGS =  -lzmq

KEXT_USE_AUTOCONF = 1

# include shared GAP package build system
GAPPATH = /host/sage-manylinux_2_28_x86_64/lib/gap
include Makefile.gappkg

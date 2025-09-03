#
# Makefile rules for the io package
#
KEXT_NAME = io
KEXT_SOURCES = src/io.c

KEXT_CFLAGS = -Igen

KEXT_USE_AUTOCONF = 1

# include shared GAP package build system
GAPPATH = /host/sage-manylinux_2_28_aarch64/lib/gap
include Makefile.gappkg

# ensure pkgconfig.h is built
$(KEXT_OBJS): gen/pkgconfig.h

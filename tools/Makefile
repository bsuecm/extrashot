# NDI Discovery Tool Makefile

CC = gcc
CFLAGS = -Wall -O2
LDFLAGS = -L/usr/local/lib -Wl,-rpath,/usr/local/lib
INCLUDES = -I/usr/local/include
LIBS = -lndi

TARGET = ndi_discover
PREFIX = /usr/local

all: $(TARGET)

$(TARGET): ndi_discover.c
	$(CC) $(CFLAGS) $(INCLUDES) -o $@ $< $(LDFLAGS) $(LIBS)

install: $(TARGET)
	install -m 755 $(TARGET) $(PREFIX)/bin/

clean:
	rm -f $(TARGET)

.PHONY: all install clean

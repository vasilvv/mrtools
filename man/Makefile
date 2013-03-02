FILES=mrtools.1 mrquery.1 mrfilesys.1 mruser.1 mrlist.1
GZFILES=$(FILES:.1=.1.gz)
SOURCES=$(FILES:.1=.pod)

POD2MAN=pod2man --center "" --release "mrtools"
GZIP=gzip

%.1.gz: %.pod
	$(POD2MAN) $< | $(GZIP) > $@

all: $(GZFILES)

clean:
	rm -f $(GZFILES)


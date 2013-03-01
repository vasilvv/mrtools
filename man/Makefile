FILES=mrtools.1 mrquery.1 mrfilesys.1 mruser.1 mrlist.1
SOURCES=$(FILES:.1=.pod)

POD2MAN=pod2man --center "" --release "mrtools"

%.1: %.pod
	$(POD2MAN) $< > $@

all: $(FILES)

clean:
	rm -f $(FILES)


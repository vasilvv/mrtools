FILES=mrtools.1
SOURCES=$(FILES:.1=.pod)

POD2MAN=pod2man --center "mrtools Moira client toolkit" --release "mrtools"

%.1: %.pod
	$(POD2MAN) $< > $@

all: $(FILES)

clean:
	rm -f $(FILES)


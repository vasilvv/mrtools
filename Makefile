doc:
	$(MAKE) -C man

doc-clean:
	$(MAKE) -C man clean

all: doc

clean: doc-clean

.PHONY: doc doc-clean all clean

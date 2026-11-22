# Make HTML documentation for Python Xlib

include ../src/defs

index.html: $(SRCS)
	makeinfo --output=. --html --split=node $(TOPSRC)

clean:
	rm -f *.html

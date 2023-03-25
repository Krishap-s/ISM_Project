UNAME_S := $(shell uname -s)

bin/snyk: bin
	wget https://static.snyk.io/cli/latest/snyk-linux -O bin/snyk

bin:
	@mkdir -p bin



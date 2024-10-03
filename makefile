TestCribbage:
	echo "#!/bin/bash" > TestCribbage
	echo "pypy3 test_cribbage.py \"\$$@\"" >> TestCribbage
	chmod u+x TestCribbage

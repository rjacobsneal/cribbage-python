TestCribbage:
	echo "#!/bin/bash" > TestCribbage
	echo "python3 test_cribbage.py \"\$$@\"" >> TestCribbage
	chmod u+x TestCribbage

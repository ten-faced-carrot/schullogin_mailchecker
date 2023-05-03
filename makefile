exec = "main.py"

$(exec):
	pyinstaller --onefile main.py
	cp dist/main .
build:
	pyinstaller --onefile main.py
	cp dist/main .


clean install:
	python3 -m pip install -U virtualenv
	virtualenv launch_venv
	launch_venv/bin/pip install -r requirements.txt
	echo "#!/bin/bash" > run.sh
	echo "launch_venv/bin/python3 main.py" >> run.sh
	chmod +x run.sh
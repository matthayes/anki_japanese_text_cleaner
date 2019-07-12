init:
	pip install -r requirements.txt

test:
	py.test

flake8:
	flake8

check_sort:
	isort --recursive --check-only --diff japanese_text_cleaner/ tests/

fix_sort:
	isort --recursive japanese_text_cleaner/ tests/

release:
	./release_anki21.sh

readme_to_html:
	grip --export

release_ankiaddon: release
	cp target/anki_japanese_text_cleaner.zip target/anki_japanese_text_cleaner.ankiaddon

ci: flake8 check_sort test release release_ankiaddon
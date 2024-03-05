# clean_files -- program do porządkowania plików.

## Obsługa skryptu.
```
usage: clean_files.py [-h] --main-dir MAIN_DIR [--dir DIR] [--config-file CONFIG_FILE] [--missing-in-main-dir [{y,n,ask}]] [--same-content [{y,n,ask}]] [--same-name [{y,n,ask}]] [--temporary [{y,n,ask}]] [--empty [{y,n,ask}]] [--unusual-permissions [{y,n,ask}]] [--forbidden-name [{y,n,ask}]]

perform chosen actions to clean up a set of directories

options:  
  -h, --help            show this help message and exit  
  --main-dir MAIN_DIR   main directory to clean up and move all the files to  
  --dir DIR             additional directory to clean up  
  --config-file CONFIG_FILE
                        use custom config file instead of default  
  --missing-in-main-dir [{y,n,ask}]
                        find files that are not present in the main directory  
  --same-content [{y,n,ask}]
                        find sets of files with the same content  
  --same-name [{y,n,ask}]
                        find sets of files with the same name  
  --temporary [{y,n,ask}]
                        find temporary files  
  --empty [{y,n,ask}]   find files that are empty  
  --unusual-permissions [{y,n,ask}]
                        find files with unusual access permissions  
  --forbidden-name [{y,n,ask}]
                        find files with special characters in their filename
```

## Konfiguracja.
Scieżką domyślną dla pliku konfiguracyjnego jest $HOME/.clean_files. Można ją nadpisać opcją --config-file.
Przykład pliku konfiguracyjnego:  
```json

{
  "permissions": "655",
  "temporary_suffixes": [
    "~",
    "tmp"
  ],
  "forbidden_characters": [
    "*",
    "#",
    "\\"
  ],
  "default_character": "_"  
}
```

permissions - uprawnienia, które mają być nadane plikom (opcja --unusual-permissions)  
temporary_suffixes - lista rozszerzeń plików tymczasowych (opcja --temporary)  
forbidden_characters - lista znaków do zamienienia w nazwach plików oraz default_character - znak, którym należy je zamienić (opcja --forbidden-name)


## Ustawianie katalogów do przeszukania.
Opcją --main-dir można ustawić katalog główny, do którego mogą zostać przeniesione wszystkie pliki.
Za pomocą --dir można zarejestrować dodatkowy katalog do przeszukania. Opcję tę można powtórzyć wiele razy.


## Włączanie poszczególnych sprawdzeń.
Sprawdzenia, które powinny się wykonać należy włączyć opcjami  --missing-in-main-dir, --same-content, --same-name, --temporary, --empty, --unusual-permissions, --forbidden-name.
Należy dodać argument 'ask' jeśli chcemy, aby skrypt pytał nas o potwierdzenie przed każdą operacją, albo 'y' jeśli chcemy wykonać akcje automatycznie.


## Testowanie.
Skrypt test_dir.sh tworzy przykładową strukturę katalogów, której użyć można do testowania.

#!/usr/bin/env bash

rm -rf X Y1 Y2

mkdir -p X
echo content > X/file.txt
mkdir -p X/dir
echo content > X/dir/file2.txt
echo othercontent > X/file3.txt
echo dddddd > X/same_name.txt
echo wwwwww > X/perms777.txt
touch X/empty.txt

mkdir -p Y1
echo missing in x > Y1/same_name.txt
echo content > Y1/existsinx.txt
mkdir -p Y1/subdir
touch Y1/subdir/emptyfile.txt
echo same name file > Y1/subdir/same_name.txt

mkdir -p Y2
echo temp > Y2/temporary.tmp
echo abc > Y2/temp~
echo '123123123' > Y2/illegal*name
echo '123123123' > Y2/illegal\$name2

find X Y1 Y2 -type f -exec chmod 644 {} \;
chmod 777 X/perms777.txt
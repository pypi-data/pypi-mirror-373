# DeltaDir

Compare directories using various methods and optionally synchronize them.

## Examples
### Create test environment
~~~bash
# prepare two identical directories
mkdir -p /tmp/src/subdir
echo x > /tmp/src/test.txt
echo x > /tmp/src/subdir/test.txt
cp -a /tmp/src /tmp/dst
~~~

### Find missing (new) files
The default mode is `exists`: a file is considered different if it is completely missing in the destination directory (dst/).

~~~bash
# create new file in src
echo new > /tmp/src/new.txt

# new file is found
deltadir /tmp/src/ /tmp/dst/
new.txt

# Let's synchronize it using -s or --sync! (no overwrite by default)
deltadir /tmp/src/ /tmp/dst/ --sync
new.txt
~~~


### Find modified files

you can use `-m`/`--method` (exists, mtime, size, hash) for more accurate checking

~~~bash
# create new file in src
echo new content > /tmp/src/new.txt

# find nothing
deltadir /tmp/src/ /tmp/dst/

# use hash (slowest, but most reliable) and detect it
deltadir /tmp/src/ /tmp/dst/ -m hash
new.txt

# sync with overwrite
deltadir /tmp/src/ /tmp/dst/ -m hash -s --overwrite
new.txt
~~~

### Always recursive
deltadir always work recursively.

~~~bash
echo new > /tmp/src/subdir/newfile.txt

deltadir /tmp/src/ /tmp/dst/ 
subdir/newfile.txt
~~~

### See result as table
Add `-t`/`--table` to see results as table:
~~~
deltadir /tmp/src/ /tmp/dst/  -t
File                                     | Reason          | Src                  | Dst                  | Action              
-----------------------------------------------------------------------------------------------------------------------------
subdir/newfile.txt                       | missing         | -                    | -                    | nothing(reported)   
~~~

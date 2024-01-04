#!/bin/sh

set -eu
umask 0022
export LC_ALL=C
if _posix_path="$( command -p getconf PATH 2>/dev/null )"; then
	PATH="$_posix_path${PATH+:}${PATH:-}"
fi
export UNIX_STD=2003 POSIXLY_CORRECT=1

I_AM_AT="$( dirname -- "$0" )"

: ${DIR_DB="$I_AM_AT/../db"}
file_todos="$DIR_DB/todos.txt"

if ! [ -f "$file_todos" ]; then
	msg='Missing TODO file; why?
'
	cat <<-err
	Status: 500 Internal Server Error
	Content-Type: text/plain
	Content-Length: ${#msg}

	${msg}
	err

	exit 1
fi

cat <<-'header'
Content-Type: application/json; encoding=UTF-8

header

cat "$file_todos" |
#
# 1: id 2: date and time 3: content
# 3 is <0x20>able.
#
# Convert item to JSONpath
awk -v MyName="${0##*/}" 'BEGIN {
	q = "\"";
}

{
	id = $1;
	date = $2;

	"let" (content = $0);
	sub(/^[ \t]*/, "", content);
	sub(/^[^ \t]+[ \t]+/, "", content);
	sub(/^[^ \t]+/, "", content);

	if ( ! sub(/^ /, "", content) ) {
		printf "%s: WTF CONTENT FORMAT!\n", MyName | "cat 1>&2";
		exit 1;
	}

	prefix = "$[" (NR-1) "]";

	printf "%s.id %d\n", prefix, id;

	gsub("_", " ", date);
	printf "%s.date %c%s%c\n", prefix, q, date, q;

	# XXX: DO NOT ESCAPE JSON STRING VALUE YET
	
	printf "%s.content %c%s%c\n", prefix, q, content, q;
}' |
#
# Finally
makrj.sh

exit 0


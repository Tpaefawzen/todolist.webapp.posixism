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

if [ -f "$file_todos" ]; then
	cat <<-header
	Content-Type: text/plain; charset=UTF-8
	Content-Length: $( wc -c < "$file_todos" )

	header

	cat "$file_todos"
	exit 0
fi

cat <<-'err'
Status: 500 Internal Server Error
Content-Type: text/plain

Missing TODO file; why?
err

exit 1

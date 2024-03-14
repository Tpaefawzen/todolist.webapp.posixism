#!/bin/sh

# Boilerplate
set -e;umask 0022;export LC_ALL=C
if _p="$(command -p getconf PATH 2>/dev/null)"; then
	export PATH="${_p}${PATH+:}${PATH:-}"
fi
export UNIX_STD=2003 POSIXLY_CORRECT=1

I_AM_AT="$( dirname -- "$0" )"

: ${DIR_DB="$I_AM_AT/../db"}
file_todos="$DIR_DB/todos.txt"

# I want such file PLZ
if ! [ -f "$file_todos" ]; then
	cat <<-'err'
	Status: 500 Internal Server Error
	Content-Type: text/plain

	Missing TODO file; why?
	err
	exit 1
fi

case "$PATH_INFO" in ''|'/')
	cat <<-'err'
	Status: 400 Bad Request
	Content-Type: text/plain

	Usage: DELETE todo/:id
	err
	exit 1
esac

# Now time to do something
id="${PATH_INFO#/}"

# Existence?
if awk -v id="$id" '$1 == id { exit 1 }' "$file_todos"; then
	cat <<-404
	Status: 404 Not Found
	Content-Type: text/plain

	DELETE /todo/${id}: no such TODO
	Status: 404
	404
	exit 1
fi

# Finally
awk -v id="$id" '$1 != id' "$file_todos" > "$file_todos".new
mv "$file_todos".new "$file_todos"

cat <<-'YES'
	Status: 204 No Content

YES

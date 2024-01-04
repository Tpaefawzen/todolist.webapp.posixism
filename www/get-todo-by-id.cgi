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
	cat <<-'err'
	Status: 500 Internal Server Error
	Content-Type: text/plain

	Missing TODO file; why?
	err

	exit 1
fi

case "${QUERY_STRING:-}" in ''|*[!0-9]*)
	cat <<-err
	Status: 400 Bad Request
	Content-Type: text/plain

	Usage: GET ${SCRIPT_NAME:-/get-todo-by-id.cgi}?{ID}
	Params: ID ~ /^[0-9]+$/ in ERE
	err
	exit 1
esac

cat "$file_todos" |
awk -v MyName="${SCRIPT_NAME}" -v myId="$QUERY_STRING" '
BEGIN {
	myId = +myId;
}

$1 == myId {
	print "Content-Type: text/plain; charset=UTF-8";
	printf "Content-Length: %s\n", byte_length($0)+1;
	print "";
	print $0;
	found = 1;
	exit 0;
}

END {
	if ( ! found ) {
		print "Status: 404 Not Found";
		print "Content-Type: text/plain";
		print "";
		print "Not found";
		exit 1;
	}
}

# Since one-true-awk is UTF-8 only, I had to make this
function byte_length(str, _i, _Length, _result, _c) {
	if ( length("あ") == 3 ) {
		return length(str);
	}

	# So it is UTF-8 only.
	_result = 0;
	for ( _i = 1; _i = _Length; _i++ ) {
		_c = substr(str, 1, 1);

		if ( "\000" <= _c && _c <= "\177" ) {
			_result += 1;
		} else if ( "\302\200" <= _c && _c <= "\337\277" ) {
			_result += 2;
		} else if ( "\340\240\200" <= _c && _c <= "\340\277\277" ) {
			_result += 3;
		} else if ( "\341\200\200" <= _c && _c <= "\357\277\277" ) {
			_result += 3;
		} else if ( "\360\220\200\200" <= _c && _c <= "\360\277\277\277" ) {
			_result += 4;
		} else if ( "\361\200\200\200" <= _c && _c <= "\363\277\277\277" ) {
			_result += 4;
		} else if ( "\364\200\200\200" <= _c && _c <= "\364\217\277\277" ) {
			_result += 4;
		} else {
			# ill-formed UTF-8
			# whatever
		}
	}
	return _result;
}'

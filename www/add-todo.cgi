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
	if ! : > "$file_todos"; then
		cat <<-'err'
		Status: 500 Internal Server Error
		Content-Type: text/plain

		Missing TODO file; why?
		err

		exit 1
	fi
fi

case "$REQUEST_METHOD" in POST)
	:
;;GET|PUT|DELETE|*)
	cat <<-'err'
	Status: 405 Method Not Allowed
	Content-Type: text/plain

	Use POST method.
	err
	exit 1
esac

set -- ${CONTENT_LENGTH:-""}
CONTENT_LENGTH="$1"

case "$CONTENT_LENGTH" in ''|0|*[!0-9]*)
	cat <<-'err'
	Status: 400 Bad Request
	Content-Type: text/plain

	The to-do must be non-empty content.
	err
	exit 1
esac

tmpdir="$( mktemp -t -d "${0##*/}.XXXXXXXXXXXX" )"
__exit_trap__() {
	set -- ${1:-$?}
	trap '' EXIT HUP INT QUIT ABRT PIPE ALRM TERM
	rm -Rf "$tmpdir"
	trap - EXIT HUP INT QUIT ABRT PIPE ALRM TERM
	exit $1
}
trap __exit_trap__ EXIT HUP INT QUIT ABRT PIPE ALRM TERM

f_errmsg="$tmpdir/errmsg"
f_result="$tmpdir/result"

# So what is ID?
last_id="$( self 1 "$file_todos" | sort -rnk1 | head -n1 )"
case last_id in '')
	last_id=0
esac

# Get content of my to-do.
if ! dd status=none bs=1 count="$CONTENT_LENGTH"; then
	echo "dd error WHY?" >> "$f_errmsg"
fi |
#
# First of all convert LFs to SSV-compatible one.
# Second reject content with control chars except LF, CR, or TAB.
# Finally convert content to "\\" or "\n"
# 
if ! awk -v MyName="${0##*/}" -v f_errmsg="$f_errmsg" -v id="$last_id" -v date="$( date +'%Y-%m-%d_%H:%M:%S' )" '
BEGIN {
	id++;

	ORS = "";
	linesep = "";

	content = "";
}

/[\001-\010]/ || /[\v\f]/ || /[\016-\037]/ {
	printf "%s: %s\n", MyName, "the to-do cannot have control characters" >> f_errmsg;
	exit 1;
}

{
	# I want to convert CR+LF to LF.
	sub("\r$", "");

	# Then what about tabs
	gsub("\t", " ");

	# Escape.
	gsub(/\\/, "&&");

	# Output.
	content = content linesep $0;
	linesep = "\\n";
}

END {
	# Finally
	print id, date, content;
	print "\n";
}' > "$f_result"; then
	echo "awk error" >> "$f_errmsg"
fi

if [ -s "f_errmsg" ]; then
	cat <<-'head_err'
	Status: 400 Bad Request
	Content-Type: text/plain
	
	head_err
	cat "$f_errmsg"
	__exit_trap__ 1
fi

# Now I can append the new column.
cat "$f_result" |
tee -a "$file_todos" |
sed '1i\
Content-Type: text/plain; UTF-8\
'

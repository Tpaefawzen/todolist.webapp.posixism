var e_new_todo = document.getElementById("new-todo");
var button_add_new_todo = document.getElementById("add-new-todo");
var e_list_todos = document.getElementById("list-todos");

button_add_new_todo.addEventListener("click", async function(event) {
	const new_todo = e_new_todo.value.trim();
	if ( ! new_todo ) return;

	let result;
	try {
		const response = await fetch("add-todo.cgi", {
			method: "POST",
			body: new_todo,
		});
		result = await response.text();
		console.log({result});
	} catch ( err ) {
		console.error(`Could not POST /add-todo.cgi: ${err}`);
		return;
	}

	parse_ssv_response_to_display(result);
	e_new_todo.value = "";
});

document.addEventListener("DOMContentLoaded", async function(event) {
	let response, todos;
	try {
		response = await fetch("list-todos.cgi");
		todos = await response.text();
	} catch ( err ) {
		console.error(`Could not GET /list-todos.cgi: ${err}`);
		return;
	}

	parse_ssv_response_to_display(todos);
});

function display_new_todo({id, timestamp, todo}) {
	const e = document.createElement("li");
	e.textContent = `${timestamp} ${todo}`;
	e_list_todos.appendChild(e);
}

function parse_ssv_response_to_display(str) {
	str.split("\n").map(col => col.trimStart()).filter(Boolean).forEach(col => {
		let [id, _, timestamp, __0x20__, ...todo] = col.split(/([ \t]+)/);
		
		try {
			timestamp = timestamp.replaceAll(/_/g, " ");
			todo = todo.join("");
			todo = todo.replaceAll(/\\n/ug, "\n").replaceAll(/\\\\/ug, "\\");
			if ( __0x20__[0] !== " " && __0x20__[0] !== "\t" ) {
				return;
			}
			todo = `${__0x20__.slice(1)}${todo}`;
		} catch ( err ) {
			return;
		}

		if ( ! ( todo = todo.trim() ) ) return;

		console.log({id, timestamp, todo});
		
		display_new_todo({id, timestamp, todo});
	});
}

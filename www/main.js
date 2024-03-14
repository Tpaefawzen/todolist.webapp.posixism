var e_new_todo = document.getElementById("new-todo");
var button_add_new_todo = document.getElementById("add-new-todo");
var e_list_todos = document.getElementById("list-todos");
var button_delete_selected_todos = document.getElementById("delete-selected-todos");

button_add_new_todo.addEventListener("click", async function(event) {
	const new_todo = e_new_todo.value.trim();
	if ( ! new_todo ) return;

	let result;
	try {
		const response = await fetch("todo", {
			method: "POST",
			body: new_todo,
		});
		result = await response.text();
		console.log({result});
	} catch ( err ) {
		console.error(`Could not POST /todo: ${err}`);
		return;
	}

	parse_ssv_response_to_display(result);
	e_new_todo.value = "";
});

button_delete_selected_todos.addEventListener("click", function(event) {
	const what2del = Array.from(document.getElementsByClassName("please-delete"));
	
	if ( what2del.length === 0 ) {
		return;
	}
	if ( ! window.confirm("Really?") ) {
		return;
	}

	// Finally
	what2del.forEach(async e => {
		let id = e.getAttribute("id");
		if ( id.substr(0, 5) !== "todo-" ) {
			console.error("Obtained non-todo .please-delete: ${e}");
			return;
		}

		id = id.slice(5);

		const response = await fetch(`todo/${id}`, { method: "DELETE" });
		console.log(response);

		e.remove();
	});
});

document.addEventListener("DOMContentLoaded", async function(event) {
	let response, todos;
	try {
		response = await fetch("todo");
		todos = await response.text();
	} catch ( err ) {
		console.error(`Could not GET /todo: ${err}`);
		return;
	}

	parse_ssv_response_to_display(todos);
});

function display_new_todo({id, timestamp, todo}) {
	// <li id=todo-:id>
	//   :timestamp :todo
	// </li>
	const e = document.createElement("li");
	e.setAttribute("id", `todo-${id}`);
	e.textContent = `${timestamp} ${todo}`;
	e.addEventListener("click", function(event) {
		e.classList.toggle("please-delete");
	});
	e_list_todos.appendChild(e);
}

function parse_ssv_response_to_display(str) {
	str.split("\n")
	//
	// [ line, ... ]
	.map(col => col.trimStart())
	//
	// [ line, ... ]
	//
	// Only non-null line
	.filter(Boolean)
	//
	// [ line, ... ]
	.forEach(col => {
		// col is /^[0-9]+ TIMESTAMP .*$/
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
			console.error(err);
			return;
		}

		if ( ! ( todo = todo.trim() ) ) return;

		console.log({id, timestamp, todo});
		
		display_new_todo({id, timestamp, todo});
	});
}

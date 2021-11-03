function xmlHttpRequestHandler(type, url, data={}, callback) {
	const http = new XMLHttpRequest();
	http.open(type, url, true);
	http.onreadystatechange = function() {
		if(http.readyState === XMLHttpRequest.DONE) {
			callback(JSON.parse(http.responseText))
		}
	}
	http.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
	http.send(JSON.stringify(data));
}


function responseHandler({command, output}) {
	const div = document.getElementById(command).querySelector('.apiActionOutputContainer')
	const outputElement = document.getElementById(command + "-output") || document.createElement('p')
	const sanitizedOutput = output.replace(/[^ -~]+/g, "")
	outputElement.innerHTML = "";
	outputElement.id = command + "-output"
	outputElement.innerHTML = sanitizedOutput;
	div.appendChild(outputElement)
}



document.addEventListener('DOMContentLoaded',function () {
	
	const nodes = document.getElementsByClassName('node');
	const nodesParentContainer = document.getElementById('nodes');
	
	window.containerId = nodesParentContainer.options[nodesParentContainer.selectedIndex].dataset.id;
	
	for(let i = 0; i< nodes.length; i++) {
		nodes[i].addEventListener('click',function(event) {
			window.containerId = event.target.dataset.id;	
		})
	}

	const apiButtons = document.getElementsByClassName('apiBtn');
	for (let i = 0; i<apiButtons.length; i++) {
		apiButtons[i].addEventListener('click', (event) => {
			xmlHttpRequestHandler('POST', 'http://localhost:3000', {
				command: event.target.dataset.command,
				containerId: window.containerId,
				params: (function(){
					const parentContainer = event.target.parentElement;
					const inputs = parentContainer.querySelectorAll(".apiParams");
					const paramValues = [];
					inputs.forEach((input) => {
						paramValues.push(input.value)
					})
					return paramValues
				})()
			}, responseHandler)
		})
	}
})



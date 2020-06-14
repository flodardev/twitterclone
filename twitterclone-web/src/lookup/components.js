export function loadTweets(callback) {
	const xhr = new XMLHttpRequest();
	xhr.responseType = "json";
	xhr.open("GET", "http://127.0.0.1:8000/api/tweets/");
	xhr.onload = () => {
		callback(xhr.response, xhr.status);
	};
	xhr.onerror = (e) => {
		console.log(e);
		callback({ messsage: "The request was an error" }, 400);
	};
	xhr.send();
}

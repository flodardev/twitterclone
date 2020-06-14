import React, { useEffect, useState } from "react";
import logo from "./logo.svg";
import "./App.css";

// init xhr request
function loadTweets(callback) {
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

// Components

// Like Button
function ActionBtn(props) {
	const { tweet, action } = props;
	const className = props.className
		? props.className
		: "btn btn-primary btn-sm";
	return action.type === "like" ? (
		<button className={className}>{tweet.likes} Likes</button>
	) : null;
}

function Tweet(props) {
	const { tweet } = props;
	const className = props.className ? props.className : "container";
	return (
		<div className={className}>
			<p>
				{tweet.id} - {tweet.content}
			</p>
			<div className="btn btn-group">
				<ActionBtn tweet={tweet} action={{ type: "like" }} />
				<ActionBtn tweet={tweet} action={{ type: "unlike" }} />
			</div>
		</div>
	);
}

function App() {
	const [tweets, setTweets] = useState([]);

	useEffect(() => {
		const myCallback = (response, status) => {
			if (status === 200) {
				setTweets(response);
			} else {
				alert("There was an error");
			}
		};
		loadTweets(myCallback);
	}, []);
	return (
		<div className="App">
			<header className="App-header">
				<img src={logo} className="App-logo" alt="logo" />
				<p>
					Edit <code>src/App.js</code> and save to reload.
				</p>
				<div>
					{tweets.map((item, index) => {
						return (
							<Tweet
								tweet={item}
								key={`${index}-{item.id}`}
								className="container border rounded my-4 "
							></Tweet>
						);
					})}
				</div>
				<a
					className="App-link"
					href="https://reactjs.org"
					target="_blank"
					rel="noopener noreferrer"
				>
					Learn React
				</a>
			</header>
		</div>
	);
}

export default App;

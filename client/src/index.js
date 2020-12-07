import React from 'react';
import ReactDOM from 'react-dom';
import Amplify from "aws-amplify";
import { ServiceWorker } from 'aws-amplify';
import './index.css';
import App from './App';
import awsExports from "./aws-exports";
import reportWebVitals from './reportWebVitals';

Amplify.configure(awsExports);
const serviceWorker = new ServiceWorker();
var registeredServiceWorker = null;
ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://cra.link/PWA
//serviceWorkerRegistration.register();
(async () => {
  registeredServiceWorker = await serviceWorker.register('/service-worker.js', '/');
  serviceWorker.enablePush('BLx__NGvdasMNkjd6VYPdzQJVBkb2qafh')
})();
// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals(console.log);

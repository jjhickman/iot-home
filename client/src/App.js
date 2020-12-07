import React from 'react';
import { BrowserRouter as Router, Route, Link, Switch, Redirect } from 'react-router-dom';
import PrivateRoute from './components/PrivateRoute'
import './App.css';

export default App = () => {
  return (
    <div className="App">
      <Router>
        <NavBar />
        <div className="container">
          <Switch>
            <Route path='/login' component={Login} />
            <PrivateRoute authed={this.state.authed} path='/' exact component={Home} />
          </Switch>
        </div>
      </Router>
    </div>
  );
}


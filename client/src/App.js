import React, { useEffect, useReducer } from 'react';
import {Router, Route, Switch} from 'react-router-dom';
import { Hub, Auth } from 'aws-amplify';
import PrivateRoute from './components/PrivateRoute';
import Header from './components/Header';
import Home from './pages/Home';
import Login from './pages/Login';
import history from './history';
import './App.css';


const reducer = (state, action) => {
  switch(action.type) {
    case 'setUser':  
      return { ...state, user: action.user, loading: false }
    case 'loaded':
      return { ...state, loading: false }
    default:
      return state
  }
}

const App = () => {
  const [userState, setUserState] = useReducer(reducer, { user: null, loading: true });
  
  const checkUser = async (setUserState) => {
    try {
      const user = await Auth.currentAuthenticatedUser()
      console.log('user: ', user)
      setUserState({ type: 'setUser', user })
    } catch (err) {
      console.log('err: ', err)
      setUserState({ type: 'loaded' })
    }
  }

  useEffect(() => {
    // set listener for auth events
    Hub.listen('auth', (data) => {
      const { payload } = data
      if (payload.event === 'signIn') {
        setImmediate(() => setUserState({ type: 'setUser', user: payload.data }));
        history.push('/');
      }
      // this listener is needed for form sign ups since the OAuth will redirect & reload
      if (payload.event === 'signOut') {
        setTimeout(() => setUserState({ type: 'setUser', user: null }), 350);
        history.push('/login');
      }
    })
    // we check for the current user unless there is a redirect to ?signedIn=true 
    if (!window.location.search.includes('?signedin=true')) {
      checkUser(setUserState)
    }
  }, []);


  return (
    <div className="App">
      <Router history={history}>
        <Header authorized={userState.user !== null ? true : false}/>
        <div className="container">
          <Switch>
            <PrivateRoute authorized={userState.user !== null ? true : false} path='/' exact component={Home} />
            <Route path='/login' component={Login} />
          </Switch>
        </div>
      </Router>
    </div>
  );
}

export default App;
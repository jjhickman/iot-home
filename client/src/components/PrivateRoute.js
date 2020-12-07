import React from 'react';
import { Route, Redirect } from 'react-router-dom';

const PrivateRoute = ({component: Component, authorized, ...rest})  => {
    return (
      <Route
        {...rest}
        render={(props) => authorized === true
          ? <Component {...props} />
          : <Redirect to={{pathname: '/login', state: {from: props.location}}} />}
      />
    )
  }

  export default PrivateRoute;
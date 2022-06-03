import React, { useContext, useState } from "react";

interface UserAuth {
  username: string;
  password: string;
  role: string;
}

const LogoutState = {
  username: "",
  password: "",
  role: "",
};

const UserContext = React.createContext({
  userAuth: LogoutState,
  save: (userAuth: UserAuth, save: boolean) => {
    console.log(userAuth.username, userAuth.password, save);
  },
  delete: () => {
    console.log("delete");
  },
  get: () => LogoutState,
});

function UserContextProvider(props: { children: JSX.Element }) {
  const initState = {
    userAuth: {
      username: localStorage.getItem("username") || "",
      password: localStorage.getItem("password") || "",
      role: localStorage.getItem("role") || "",
    },
    save(userAuth: UserAuth, forever: boolean) {
      if (forever) {
        localStorage.setItem("username", userAuth.username);
        localStorage.setItem("password", userAuth.password);
        localStorage.setItem("role", userAuth.role);
      }
      setState({ ...state, userAuth });
    },
    delete() {
      localStorage.removeItem("username");
      localStorage.removeItem("password");
      localStorage.removeItem("role");
      setState({ ...state, userAuth: LogoutState });
    },
    get() {
      return state.userAuth;
    },
  };

  const [state, setState] = useState(initState);

  return (
    <UserContext.Provider value={state}>{props.children}</UserContext.Provider>
  );
}

const useAuth = () => {
  return useContext(UserContext);
};

export { useAuth, UserContextProvider };

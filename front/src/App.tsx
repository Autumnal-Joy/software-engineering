import React, { StrictMode } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import {
  Admin,
  Bills,
  Chargers,
  Login,
  MakeOrder,
  OrderInfo,
  User,
  Table,
} from "./pages";
import { UserContextProvider } from "./components/UserManager";
import { ProtectedRoute } from "./components/ProtectedRoute";

function App() {
  return (
    <StrictMode>
      <UserContextProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/">
              <Route index element={<Login />} />
            </Route>
            <Route element={<ProtectedRoute />}>
              <Route path="/user">
                <Route index element={<User />} />
                <Route path="make-order" element={<MakeOrder />}></Route>
                <Route path="order-info" element={<OrderInfo />}></Route>
                <Route path="bills" element={<Bills />}></Route>
              </Route>
              <Route path="/admin">
                <Route index element={<Admin />} />
                <Route path="chargers" element={<Chargers />} />
                <Route path="table" element={<Table />} />
              </Route>
              <Route path="*" />
            </Route>
          </Routes>
        </BrowserRouter>
      </UserContextProvider>
    </StrictMode>
  );
}

export default App;

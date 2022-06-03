import { Table } from "antd";
import React, { StrictMode } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import {
  Admin,
  Bills,
  Cars,
  Chargers,
  Login,
  MakeOrder,
  OrderInfo,
  User,
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
                <Route path="chargers">
                  <Route index element={<Chargers />} />
                  <Route path=":chargerID" element={<Cars />} />
                </Route>
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

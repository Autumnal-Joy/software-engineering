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
import Test from "./pages/test/Test";

function App() {
  return (
    <StrictMode>
      <UserContextProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Login />} />
            <Route element={<ProtectedRoute />}>
              <Route path="/user">
                <Route index element={<User />} />
                <Route path="make-order" element={<MakeOrder />} />
                <Route path="order-info" element={<OrderInfo />} />
                <Route path="bills" element={<Bills />} />
              </Route>
              <Route path="/admin">
                <Route index element={<Admin />} />
                <Route path="chargers" element={<Chargers />} />
                <Route path="table" element={<Table />} />
              </Route>
            </Route>
            <Route path="/test" element={<Test />} />
          </Routes>
        </BrowserRouter>
      </UserContextProvider>
    </StrictMode>
  );
}

export default App;

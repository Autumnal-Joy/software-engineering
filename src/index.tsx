import React, { StrictMode } from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import {
  Admin,
  Bills,
  Cars,
  Chargers,
  Login,
  MakeOrder,
  OrderInfo,
  Table,
  User,
} from "./components";
import "./index.css";
import reportWebVitals from "./reportWebVitals";

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement
);

root.render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/">
          <Route index element={<Login />} />
        </Route>
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
      </Routes>
    </BrowserRouter>
  </StrictMode>
);

// If you want to start measuring performance in your Login, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();

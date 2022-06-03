import React from "react";
import { useParams } from "react-router-dom";
import Back from "../back/Back";
import "./Cars.css";

function Cars() {
  const params = useParams();
  return (
    <>
      <Back title="当前服务对象" />
      <div>查看充电桩{params.chargerID}</div>
    </>
  );
}

export default Cars;

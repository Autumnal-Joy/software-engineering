import { PageHeader } from "antd";
import React from "react";
import { Outlet, useNavigate } from "react-router-dom";
import "./Back.css";

function Back(props: { title: string }) {
  const navigate = useNavigate();
  return (
    <>
      <PageHeader
        onBack={() => {
          navigate(-1);
        }}
        title={props.title}
      />
      <Outlet />
    </>
  );
}

export default Back;
